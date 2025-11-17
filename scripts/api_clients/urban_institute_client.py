"""
Urban Institute Education Data Portal API Client

This client retrieves data from the Urban Institute's Education Data Portal API.
Primary use: IPEDS institutional directory data for 4-year colleges.

Documentation: https://educationdata.urban.org/documentation/
API Endpoint: https://educationdata.urban.org/api/v1/
"""

import requests
import time
import pandas as pd
from pathlib import Path
import sys

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import REQUEST_DELAY, MAX_RETRIES, TIMEOUT


class UrbanInstituteClient:
    """Client for Urban Institute Education Data Portal API"""

    def __init__(self):
        """Initialize Urban Institute client."""
        self.base_url = 'https://educationdata.urban.org/api/v1'
        self.session = requests.Session()

    def _make_request(self, url, params=None, retries=MAX_RETRIES):
        """
        Make API request with retry logic.

        Args:
            url: API endpoint URL
            params: Query parameters (optional)
            retries: Number of retries remaining

        Returns:
            dict: JSON response
        """
        try:
            response = self.session.get(url, params=params, timeout=TIMEOUT)
            response.raise_for_status()
            time.sleep(REQUEST_DELAY)
            return response.json()

        except requests.exceptions.RequestException as e:
            if retries > 0:
                print(f"  Request failed, retrying... ({retries} attempts left)")
                time.sleep(REQUEST_DELAY * 2)
                return self._make_request(url, params, retries - 1)
            else:
                raise Exception(f"Urban Institute API request failed after {MAX_RETRIES} attempts: {str(e)}")

    def get_colleges_count(self, year=2022, state_fips=None):
        """
        Get count of 4-year degree-granting colleges.

        Args:
            year: Year to query (default 2022)
            state_fips: Optional 2-digit state FIPS code to filter

        Returns:
            int: Count of 4-year degree-granting colleges
        """
        endpoint = f'{self.base_url}/college-university/ipeds/directory/{year}/'

        params = {
            'degree_granting': 1,
            'inst_level': 4
        }

        if state_fips:
            params['fips'] = state_fips

        response = self._make_request(endpoint, params)
        return response.get('count', 0)

    def get_four_year_colleges(self, year=2022, state_fips_list=None):
        """
        Retrieve all 4-year degree-granting college data with pagination.

        Note: API query uses fips + inst_level filters only (combining with degree_granting
        can cause 503 errors). We filter for degree_granting==1 after fetching.

        Args:
            year: Year to query (default 2022)
            state_fips_list: Optional list of 2-digit state FIPS codes to filter

        Returns:
            DataFrame: College data with columns: unitid, inst_name, county_fips, state_fips,
                      city, inst_level, degree_granting, inst_control, sector
        """
        all_colleges = []

        # If state list provided, query each state separately
        # (more efficient than querying all and filtering)
        if state_fips_list:
            states_to_query = state_fips_list
        else:
            # Must query by state to avoid API errors
            raise ValueError("state_fips_list is required for reliable API access")

        for state_fips in states_to_query:
            if state_fips:
                print(f"  Fetching data for state FIPS: {state_fips}")

            endpoint = f'{self.base_url}/college-university/ipeds/directory/{year}/'

            # Only use fips + inst_level filters (adding degree_granting causes 503 errors)
            params = {
                'fips': state_fips,
                'inst_level': 4
            }

            # Fetch first page
            response = self._make_request(endpoint, params)

            if 'results' in response:
                colleges = response['results']
                all_colleges.extend(colleges)

                count = response.get('count', 0)
                fetched = len(colleges)

                print(f"    Retrieved {fetched} / {count} inst_level=4 institutions")

                # Handle pagination
                next_url = response.get('next')
                while next_url:
                    try:
                        response = self._make_request(next_url)

                        if 'results' in response:
                            colleges = response['results']
                            all_colleges.extend(colleges)
                            fetched += len(colleges)

                            print(f"    Retrieved {fetched} / {count} inst_level=4 institutions")

                            next_url = response.get('next')

                            if len(colleges) == 0:
                                break
                        else:
                            break

                    except Exception as e:
                        print(f"  Error during pagination: {e}")
                        break

        print(f"✓ Retrieved {len(all_colleges)} total inst_level=4 institutions")

        # Convert to DataFrame
        college_data = []
        for college in all_colleges:
            college_data.append({
                'unitid': college.get('unitid'),
                'inst_name': college.get('inst_name'),
                'county_fips': college.get('county_fips'),
                'state_fips': college.get('fips'),
                'city': college.get('city'),
                'state_abbr': college.get('state_abbr'),
                'inst_level': college.get('inst_level'),
                'degree_granting': college.get('degree_granting'),
                'inst_control': college.get('inst_control'),
                'sector': college.get('sector'),
                'year': year
            })

        df = pd.DataFrame(college_data)

        # Filter for degree-granting institutions only
        if not df.empty:
            df_filtered = df[df['degree_granting'] == 1].copy()
            print(f"✓ Filtered to {len(df_filtered)} degree-granting institutions")
            return df_filtered

        return df

    def aggregate_colleges_by_county(self, colleges_df):
        """
        Aggregate college data to county level.

        Args:
            colleges_df: DataFrame of colleges from get_four_year_colleges()

        Returns:
            DataFrame: County-level college counts with columns: area_fips, college_count,
                      state_fips, state_abbr
        """
        # Ensure county_fips is 5-digit string
        colleges_df['county_fips_str'] = colleges_df['county_fips'].astype(str).str.zfill(5)

        # Count colleges per county
        county_college_counts = colleges_df.groupby('county_fips_str').agg({
            'unitid': 'count',
            'state_fips': 'first',
            'state_abbr': 'first'
        }).reset_index()

        county_college_counts.rename(columns={
            'county_fips_str': 'area_fips',
            'unitid': 'college_count'
        }, inplace=True)

        # Convert area_fips to integer for consistency
        county_college_counts['area_fips'] = county_college_counts['area_fips'].astype(int)

        return county_college_counts


if __name__ == '__main__':
    # Test the Urban Institute client
    print("Testing Urban Institute Education Data Portal API Client...")
    print("=" * 60)

    client = UrbanInstituteClient()

    # Test 1: Get total count for Virginia
    print("\nTest 1: Get 4-Year College Count - Virginia")
    print("-" * 60)
    try:
        count = client.get_colleges_count(year=2022, state_fips='51')
        print(f"✓ Total 4-year colleges in Virginia: {count}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Get college data for Delaware (small state for testing)
    print("\n\nTest 2: Get 4-Year Colleges - Delaware Only")
    print("-" * 60)
    try:
        df = client.get_four_year_colleges(year=2022, state_fips_list=['10'])
        print(f"✓ Retrieved {len(df)} 4-year colleges for Delaware")
        if not df.empty:
            print(f"\nColumns: {df.columns.tolist()}")
            print(f"\nSample data:")
            print(df[['unitid', 'inst_name', 'city', 'county_fips']].head())
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Aggregate to county level
    print("\n\nTest 3: Aggregate to County Level")
    print("-" * 60)
    try:
        if not df.empty:
            county_df = client.aggregate_colleges_by_county(df)
            print(f"✓ Aggregated to {len(county_df)} counties")
            print(f"\nCounty-level data:")
            print(county_df.to_string())
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Urban Institute Client test complete")
