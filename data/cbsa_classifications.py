"""
CBSA (Core-Based Statistical Area) Classifications

Maps counties to their metropolitan/micropolitan/rural status based on
Census Bureau CBSA delineation files (July 2023).

Classifications:
- Metropolitan: Urban area 50,000+ population
- Micropolitan: Urban area 10,000-49,999 population
- Rural: Neither metropolitan nor micropolitan

Generated automatically from Census Bureau delineation files.
Source: https://www.census.gov/geographies/reference-files/time-series/demo/metro-micro/delineation-files.html
Date: July 2023

Coverage:
- Total counties: 339
- Metropolitan: 246 (72.6%)
- Micropolitan: 93 (27.4%)
- Rural: 0 (0.0%)

Study states: VA, MD, WV, NC, TN, KY, DC
"""

from typing import Dict

# CBSA classifications for all counties in the study
# Format: {FIPS: {'name': 'County Name', 'cbsa': 'metro'|'micro'|'rural', 'cbsa_name': 'MSA Name'}}

CBSA_CLASSIFICATIONS = {
    '11001': {'name': 'District of Columbia', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '21003': {'name': 'Allen', 'cbsa': 'metro', 'cbsa_name': 'Bowling Green, KY'},
    '21005': {'name': 'Anderson', 'cbsa': 'micro', 'cbsa_name': 'Frankfort, KY'},
    '21007': {'name': 'Ballard', 'cbsa': 'metro', 'cbsa_name': 'Paducah, KY-IL'},
    '21009': {'name': 'Barren', 'cbsa': 'micro', 'cbsa_name': 'Glasgow, KY'},
    '21011': {'name': 'Bath', 'cbsa': 'micro', 'cbsa_name': 'Mount Sterling, KY'},
    '21013': {'name': 'Bell', 'cbsa': 'micro', 'cbsa_name': 'Middlesborough, KY'},
    '21015': {'name': 'Boone', 'cbsa': 'metro', 'cbsa_name': 'Cincinnati, OH-KY-IN'},
    '21017': {'name': 'Bourbon', 'cbsa': 'metro', 'cbsa_name': 'Lexington-Fayette, KY'},
    '21019': {'name': 'Boyd', 'cbsa': 'metro', 'cbsa_name': 'Huntington-Ashland, WV-KY-OH'},
    '21021': {'name': 'Boyle', 'cbsa': 'micro', 'cbsa_name': 'Danville, KY'},
    '21023': {'name': 'Bracken', 'cbsa': 'metro', 'cbsa_name': 'Cincinnati, OH-KY-IN'},
    '21029': {'name': 'Bullitt', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21031': {'name': 'Butler', 'cbsa': 'metro', 'cbsa_name': 'Bowling Green, KY'},
    '21035': {'name': 'Calloway', 'cbsa': 'micro', 'cbsa_name': 'Murray, KY'},
    '21037': {'name': 'Campbell', 'cbsa': 'metro', 'cbsa_name': 'Cincinnati, OH-KY-IN'},
    '21039': {'name': 'Carlisle', 'cbsa': 'metro', 'cbsa_name': 'Paducah, KY-IL'},
    '21043': {'name': 'Carter', 'cbsa': 'metro', 'cbsa_name': 'Huntington-Ashland, WV-KY-OH'},
    '21047': {'name': 'Christian', 'cbsa': 'metro', 'cbsa_name': 'Clarksville, TN-KY'},
    '21049': {'name': 'Clark', 'cbsa': 'metro', 'cbsa_name': 'Lexington-Fayette, KY'},
    '21051': {'name': 'Clay', 'cbsa': 'micro', 'cbsa_name': 'Corbin, KY'},
    '21059': {'name': 'Daviess', 'cbsa': 'metro', 'cbsa_name': 'Owensboro, KY'},
    '21061': {'name': 'Edmonson', 'cbsa': 'metro', 'cbsa_name': 'Bowling Green, KY'},
    '21065': {'name': 'Estill', 'cbsa': 'micro', 'cbsa_name': 'Richmond-Berea, KY'},
    '21067': {'name': 'Fayette', 'cbsa': 'metro', 'cbsa_name': 'Lexington-Fayette, KY'},
    '21071': {'name': 'Floyd', 'cbsa': 'micro', 'cbsa_name': 'Pikeville, KY'},
    '21073': {'name': 'Franklin', 'cbsa': 'micro', 'cbsa_name': 'Frankfort, KY'},
    '21077': {'name': 'Gallatin', 'cbsa': 'metro', 'cbsa_name': 'Cincinnati, OH-KY-IN'},
    '21081': {'name': 'Grant', 'cbsa': 'metro', 'cbsa_name': 'Cincinnati, OH-KY-IN'},
    '21083': {'name': 'Graves', 'cbsa': 'micro', 'cbsa_name': 'Mayfield, KY'},
    '21087': {'name': 'Green', 'cbsa': 'micro', 'cbsa_name': 'Campbellsville, KY'},
    '21089': {'name': 'Greenup', 'cbsa': 'metro', 'cbsa_name': 'Huntington-Ashland, WV-KY-OH'},
    '21093': {'name': 'Hardin', 'cbsa': 'metro', 'cbsa_name': 'Elizabethtown, KY'},
    '21101': {'name': 'Henderson', 'cbsa': 'micro', 'cbsa_name': 'Henderson, KY'},
    '21103': {'name': 'Henry', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21107': {'name': 'Hopkins', 'cbsa': 'micro', 'cbsa_name': 'Madisonville, KY'},
    '21111': {'name': 'Jefferson', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21113': {'name': 'Jessamine', 'cbsa': 'metro', 'cbsa_name': 'Lexington-Fayette, KY'},
    '21117': {'name': 'Kenton', 'cbsa': 'metro', 'cbsa_name': 'Cincinnati, OH-KY-IN'},
    '21121': {'name': 'Knox', 'cbsa': 'micro', 'cbsa_name': 'Corbin, KY'},
    '21123': {'name': 'Larue', 'cbsa': 'metro', 'cbsa_name': 'Elizabethtown, KY'},
    '21125': {'name': 'Laurel', 'cbsa': 'micro', 'cbsa_name': 'Corbin, KY'},
    '21127': {'name': 'Lawrence', 'cbsa': 'metro', 'cbsa_name': 'Huntington-Ashland, WV-KY-OH'},
    '21137': {'name': 'Lincoln', 'cbsa': 'micro', 'cbsa_name': 'Danville, KY'},
    '21139': {'name': 'Livingston', 'cbsa': 'metro', 'cbsa_name': 'Paducah, KY-IL'},
    '21145': {'name': 'McCracken', 'cbsa': 'metro', 'cbsa_name': 'Paducah, KY-IL'},
    '21149': {'name': 'McLean', 'cbsa': 'metro', 'cbsa_name': 'Owensboro, KY'},
    '21151': {'name': 'Madison', 'cbsa': 'micro', 'cbsa_name': 'Richmond-Berea, KY'},
    '21163': {'name': 'Meade', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21165': {'name': 'Menifee', 'cbsa': 'micro', 'cbsa_name': 'Mount Sterling, KY'},
    '21169': {'name': 'Metcalfe', 'cbsa': 'micro', 'cbsa_name': 'Glasgow, KY'},
    '21173': {'name': 'Montgomery', 'cbsa': 'micro', 'cbsa_name': 'Mount Sterling, KY'},
    '21179': {'name': 'Nelson', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21185': {'name': 'Oldham', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21191': {'name': 'Pendleton', 'cbsa': 'metro', 'cbsa_name': 'Cincinnati, OH-KY-IN'},
    '21195': {'name': 'Pike', 'cbsa': 'micro', 'cbsa_name': 'Pikeville, KY'},
    '21199': {'name': 'Pulaski', 'cbsa': 'micro', 'cbsa_name': 'Somerset, KY'},
    '21203': {'name': 'Rockcastle', 'cbsa': 'micro', 'cbsa_name': 'Richmond-Berea, KY'},
    '21209': {'name': 'Scott', 'cbsa': 'metro', 'cbsa_name': 'Lexington-Fayette, KY'},
    '21211': {'name': 'Shelby', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21213': {'name': 'Simpson', 'cbsa': 'micro', 'cbsa_name': 'Franklin, KY'},
    '21215': {'name': 'Spencer', 'cbsa': 'metro', 'cbsa_name': 'Louisville/Jefferson County, KY-IN'},
    '21217': {'name': 'Taylor', 'cbsa': 'micro', 'cbsa_name': 'Campbellsville, KY'},
    '21221': {'name': 'Trigg', 'cbsa': 'metro', 'cbsa_name': 'Clarksville, TN-KY'},
    '21227': {'name': 'Warren', 'cbsa': 'metro', 'cbsa_name': 'Bowling Green, KY'},
    '21233': {'name': 'Webster', 'cbsa': 'micro', 'cbsa_name': 'Henderson, KY'},
    '21235': {'name': 'Whitley', 'cbsa': 'micro', 'cbsa_name': 'Corbin, KY'},
    '21239': {'name': 'Woodford', 'cbsa': 'metro', 'cbsa_name': 'Lexington-Fayette, KY'},
    '24001': {'name': 'Allegany', 'cbsa': 'micro', 'cbsa_name': 'Cumberland, MD-WV'},
    '24003': {'name': 'Anne Arundel', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24005': {'name': 'Baltimore', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24009': {'name': 'Calvert', 'cbsa': 'metro', 'cbsa_name': 'Lexington Park, MD'},
    '24013': {'name': 'Carroll', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24015': {'name': 'Cecil', 'cbsa': 'metro', 'cbsa_name': 'Philadelphia-Camden-Wilmington, PA-NJ-DE-MD'},
    '24017': {'name': 'Charles', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '24019': {'name': 'Dorchester', 'cbsa': 'micro', 'cbsa_name': 'Cambridge, MD'},
    '24021': {'name': 'Frederick', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '24025': {'name': 'Harford', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24027': {'name': 'Howard', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24031': {'name': 'Montgomery', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '24033': {'name': 'Prince George\'s', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '24035': {'name': 'Queen Anne\'s', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '24037': {'name': 'St. Mary\'s', 'cbsa': 'metro', 'cbsa_name': 'Lexington Park, MD'},
    '24039': {'name': 'Somerset', 'cbsa': 'metro', 'cbsa_name': 'Salisbury, MD'},
    '24041': {'name': 'Talbot', 'cbsa': 'micro', 'cbsa_name': 'Easton, MD'},
    '24043': {'name': 'Washington', 'cbsa': 'metro', 'cbsa_name': 'Hagerstown-Martinsburg, MD-WV'},
    '24045': {'name': 'Wicomico', 'cbsa': 'metro', 'cbsa_name': 'Salisbury, MD'},
    '24047': {'name': 'Worcester', 'cbsa': 'micro', 'cbsa_name': 'Ocean Pines, MD'},
    '24510': {'name': 'Baltimore', 'cbsa': 'metro', 'cbsa_name': 'Baltimore-Columbia-Towson, MD'},
    '37001': {'name': 'Alamance', 'cbsa': 'metro', 'cbsa_name': 'Burlington, NC'},
    '37003': {'name': 'Alexander', 'cbsa': 'metro', 'cbsa_name': 'Hickory-Lenoir-Morganton, NC'},
    '37007': {'name': 'Anson', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37013': {'name': 'Beaufort', 'cbsa': 'micro', 'cbsa_name': 'Washington, NC'},
    '37019': {'name': 'Brunswick', 'cbsa': 'metro', 'cbsa_name': 'Wilmington, NC'},
    '37021': {'name': 'Buncombe', 'cbsa': 'metro', 'cbsa_name': 'Asheville, NC'},
    '37023': {'name': 'Burke', 'cbsa': 'metro', 'cbsa_name': 'Hickory-Lenoir-Morganton, NC'},
    '37025': {'name': 'Cabarrus', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37027': {'name': 'Caldwell', 'cbsa': 'metro', 'cbsa_name': 'Hickory-Lenoir-Morganton, NC'},
    '37029': {'name': 'Camden', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '37031': {'name': 'Carteret', 'cbsa': 'micro', 'cbsa_name': 'Morehead City, NC'},
    '37035': {'name': 'Catawba', 'cbsa': 'metro', 'cbsa_name': 'Hickory-Lenoir-Morganton, NC'},
    '37037': {'name': 'Chatham', 'cbsa': 'metro', 'cbsa_name': 'Durham-Chapel Hill, NC'},
    '37045': {'name': 'Cleveland', 'cbsa': 'micro', 'cbsa_name': 'Shelby-Kings Mountain, NC'},
    '37049': {'name': 'Craven', 'cbsa': 'micro', 'cbsa_name': 'New Bern, NC'},
    '37051': {'name': 'Cumberland', 'cbsa': 'metro', 'cbsa_name': 'Fayetteville, NC'},
    '37053': {'name': 'Currituck', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '37055': {'name': 'Dare', 'cbsa': 'micro', 'cbsa_name': 'Kill Devil Hills, NC'},
    '37057': {'name': 'Davidson', 'cbsa': 'metro', 'cbsa_name': 'Winston-Salem, NC'},
    '37059': {'name': 'Davie', 'cbsa': 'metro', 'cbsa_name': 'Winston-Salem, NC'},
    '37063': {'name': 'Durham', 'cbsa': 'metro', 'cbsa_name': 'Durham-Chapel Hill, NC'},
    '37065': {'name': 'Edgecombe', 'cbsa': 'metro', 'cbsa_name': 'Rocky Mount, NC'},
    '37067': {'name': 'Forsyth', 'cbsa': 'metro', 'cbsa_name': 'Winston-Salem, NC'},
    '37069': {'name': 'Franklin', 'cbsa': 'metro', 'cbsa_name': 'Raleigh-Cary, NC'},
    '37071': {'name': 'Gaston', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37073': {'name': 'Gates', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '37081': {'name': 'Guilford', 'cbsa': 'metro', 'cbsa_name': 'Greensboro-High Point, NC'},
    '37083': {'name': 'Halifax', 'cbsa': 'micro', 'cbsa_name': 'Roanoke Rapids, NC'},
    '37085': {'name': 'Harnett', 'cbsa': 'micro', 'cbsa_name': 'Anderson Creek, NC'},
    '37087': {'name': 'Haywood', 'cbsa': 'micro', 'cbsa_name': 'Waynesville, NC'},
    '37089': {'name': 'Henderson', 'cbsa': 'metro', 'cbsa_name': 'Asheville, NC'},
    '37093': {'name': 'Hoke', 'cbsa': 'metro', 'cbsa_name': 'Fayetteville, NC'},
    '37097': {'name': 'Iredell', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37101': {'name': 'Johnston', 'cbsa': 'metro', 'cbsa_name': 'Raleigh-Cary, NC'},
    '37103': {'name': 'Jones', 'cbsa': 'micro', 'cbsa_name': 'New Bern, NC'},
    '37105': {'name': 'Lee', 'cbsa': 'micro', 'cbsa_name': 'Sanford, NC'},
    '37107': {'name': 'Lenoir', 'cbsa': 'micro', 'cbsa_name': 'Kinston, NC'},
    '37109': {'name': 'Lincoln', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37111': {'name': 'McDowell', 'cbsa': 'micro', 'cbsa_name': 'Marion, NC'},
    '37115': {'name': 'Madison', 'cbsa': 'metro', 'cbsa_name': 'Asheville, NC'},
    '37119': {'name': 'Mecklenburg', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37125': {'name': 'Moore', 'cbsa': 'metro', 'cbsa_name': 'Pinehurst-Southern Pines, NC'},
    '37127': {'name': 'Nash', 'cbsa': 'metro', 'cbsa_name': 'Rocky Mount, NC'},
    '37129': {'name': 'New Hanover', 'cbsa': 'metro', 'cbsa_name': 'Wilmington, NC'},
    '37131': {'name': 'Northampton', 'cbsa': 'micro', 'cbsa_name': 'Roanoke Rapids, NC'},
    '37133': {'name': 'Onslow', 'cbsa': 'metro', 'cbsa_name': 'Jacksonville, NC'},
    '37135': {'name': 'Orange', 'cbsa': 'metro', 'cbsa_name': 'Durham-Chapel Hill, NC'},
    '37137': {'name': 'Pamlico', 'cbsa': 'micro', 'cbsa_name': 'New Bern, NC'},
    '37139': {'name': 'Pasquotank', 'cbsa': 'micro', 'cbsa_name': 'Elizabeth City, NC'},
    '37141': {'name': 'Pender', 'cbsa': 'metro', 'cbsa_name': 'Wilmington, NC'},
    '37145': {'name': 'Person', 'cbsa': 'metro', 'cbsa_name': 'Durham-Chapel Hill, NC'},
    '37147': {'name': 'Pitt', 'cbsa': 'metro', 'cbsa_name': 'Greenville, NC'},
    '37151': {'name': 'Randolph', 'cbsa': 'metro', 'cbsa_name': 'Greensboro-High Point, NC'},
    '37153': {'name': 'Richmond', 'cbsa': 'micro', 'cbsa_name': 'Rockingham, NC'},
    '37155': {'name': 'Robeson', 'cbsa': 'micro', 'cbsa_name': 'Lumberton, NC'},
    '37157': {'name': 'Rockingham', 'cbsa': 'metro', 'cbsa_name': 'Greensboro-High Point, NC'},
    '37159': {'name': 'Rowan', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37161': {'name': 'Rutherford', 'cbsa': 'micro', 'cbsa_name': 'Forest City, NC'},
    '37165': {'name': 'Scotland', 'cbsa': 'micro', 'cbsa_name': 'Laurinburg, NC'},
    '37167': {'name': 'Stanly', 'cbsa': 'micro', 'cbsa_name': 'Albemarle, NC'},
    '37169': {'name': 'Stokes', 'cbsa': 'metro', 'cbsa_name': 'Winston-Salem, NC'},
    '37171': {'name': 'Surry', 'cbsa': 'micro', 'cbsa_name': 'Mount Airy, NC'},
    '37175': {'name': 'Transylvania', 'cbsa': 'micro', 'cbsa_name': 'Brevard, NC'},
    '37179': {'name': 'Union', 'cbsa': 'metro', 'cbsa_name': 'Charlotte-Concord-Gastonia, NC-SC'},
    '37181': {'name': 'Vance', 'cbsa': 'micro', 'cbsa_name': 'Henderson, NC'},
    '37183': {'name': 'Wake', 'cbsa': 'metro', 'cbsa_name': 'Raleigh-Cary, NC'},
    '37189': {'name': 'Watauga', 'cbsa': 'micro', 'cbsa_name': 'Boone, NC'},
    '37191': {'name': 'Wayne', 'cbsa': 'metro', 'cbsa_name': 'Goldsboro, NC'},
    '37193': {'name': 'Wilkes', 'cbsa': 'micro', 'cbsa_name': 'North Wilkesboro, NC'},
    '37195': {'name': 'Wilson', 'cbsa': 'micro', 'cbsa_name': 'Wilson, NC'},
    '37197': {'name': 'Yadkin', 'cbsa': 'metro', 'cbsa_name': 'Winston-Salem, NC'},
    '47001': {'name': 'Anderson', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47003': {'name': 'Bedford', 'cbsa': 'micro', 'cbsa_name': 'Shelbyville, TN'},
    '47009': {'name': 'Blount', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47011': {'name': 'Bradley', 'cbsa': 'metro', 'cbsa_name': 'Cleveland, TN'},
    '47013': {'name': 'Campbell', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47015': {'name': 'Cannon', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47019': {'name': 'Carter', 'cbsa': 'metro', 'cbsa_name': 'Johnson City, TN'},
    '47021': {'name': 'Cheatham', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47023': {'name': 'Chester', 'cbsa': 'metro', 'cbsa_name': 'Jackson, TN'},
    '47029': {'name': 'Cocke', 'cbsa': 'micro', 'cbsa_name': 'Newport, TN'},
    '47031': {'name': 'Coffee', 'cbsa': 'micro', 'cbsa_name': 'Tullahoma-Manchester, TN'},
    '47033': {'name': 'Crockett', 'cbsa': 'metro', 'cbsa_name': 'Jackson, TN'},
    '47035': {'name': 'Cumberland', 'cbsa': 'micro', 'cbsa_name': 'Crossville, TN'},
    '47037': {'name': 'Davidson', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47043': {'name': 'Dickson', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47045': {'name': 'Dyer', 'cbsa': 'micro', 'cbsa_name': 'Dyersburg, TN'},
    '47047': {'name': 'Fayette', 'cbsa': 'metro', 'cbsa_name': 'Memphis, TN-MS-AR'},
    '47051': {'name': 'Franklin', 'cbsa': 'micro', 'cbsa_name': 'Winchester, TN'},
    '47053': {'name': 'Gibson', 'cbsa': 'metro', 'cbsa_name': 'Jackson, TN'},
    '47057': {'name': 'Grainger', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47059': {'name': 'Greene', 'cbsa': 'micro', 'cbsa_name': 'Greeneville, TN'},
    '47063': {'name': 'Hamblen', 'cbsa': 'metro', 'cbsa_name': 'Morristown, TN'},
    '47065': {'name': 'Hamilton', 'cbsa': 'metro', 'cbsa_name': 'Chattanooga, TN-GA'},
    '47073': {'name': 'Hawkins', 'cbsa': 'metro', 'cbsa_name': 'Kingsport-Bristol, TN-VA'},
    '47079': {'name': 'Henry', 'cbsa': 'micro', 'cbsa_name': 'Paris, TN'},
    '47081': {'name': 'Hickman', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47087': {'name': 'Jackson', 'cbsa': 'micro', 'cbsa_name': 'Cookeville, TN'},
    '47089': {'name': 'Jefferson', 'cbsa': 'metro', 'cbsa_name': 'Morristown, TN'},
    '47093': {'name': 'Knox', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47099': {'name': 'Lawrence', 'cbsa': 'micro', 'cbsa_name': 'Lawrenceburg, TN'},
    '47103': {'name': 'Lincoln', 'cbsa': 'micro', 'cbsa_name': 'Fayetteville, TN'},
    '47105': {'name': 'Loudon', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47107': {'name': 'McMinn', 'cbsa': 'micro', 'cbsa_name': 'Athens, TN'},
    '47111': {'name': 'Macon', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47113': {'name': 'Madison', 'cbsa': 'metro', 'cbsa_name': 'Jackson, TN'},
    '47115': {'name': 'Marion', 'cbsa': 'metro', 'cbsa_name': 'Chattanooga, TN-GA'},
    '47117': {'name': 'Marshall', 'cbsa': 'micro', 'cbsa_name': 'Lewisburg, TN'},
    '47119': {'name': 'Maury', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47121': {'name': 'Meigs', 'cbsa': 'micro', 'cbsa_name': 'Athens, TN'},
    '47125': {'name': 'Montgomery', 'cbsa': 'metro', 'cbsa_name': 'Clarksville, TN-KY'},
    '47127': {'name': 'Moore', 'cbsa': 'micro', 'cbsa_name': 'Tullahoma-Manchester, TN'},
    '47129': {'name': 'Morgan', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47131': {'name': 'Obion', 'cbsa': 'micro', 'cbsa_name': 'Union City, TN'},
    '47133': {'name': 'Overton', 'cbsa': 'micro', 'cbsa_name': 'Cookeville, TN'},
    '47139': {'name': 'Polk', 'cbsa': 'metro', 'cbsa_name': 'Cleveland, TN'},
    '47141': {'name': 'Putnam', 'cbsa': 'micro', 'cbsa_name': 'Cookeville, TN'},
    '47145': {'name': 'Roane', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47147': {'name': 'Robertson', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47149': {'name': 'Rutherford', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47153': {'name': 'Sequatchie', 'cbsa': 'metro', 'cbsa_name': 'Chattanooga, TN-GA'},
    '47155': {'name': 'Sevier', 'cbsa': 'micro', 'cbsa_name': 'Sevierville, TN'},
    '47157': {'name': 'Shelby', 'cbsa': 'metro', 'cbsa_name': 'Memphis, TN-MS-AR'},
    '47159': {'name': 'Smith', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47161': {'name': 'Stewart', 'cbsa': 'metro', 'cbsa_name': 'Clarksville, TN-KY'},
    '47163': {'name': 'Sullivan', 'cbsa': 'metro', 'cbsa_name': 'Kingsport-Bristol, TN-VA'},
    '47165': {'name': 'Sumner', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47167': {'name': 'Tipton', 'cbsa': 'metro', 'cbsa_name': 'Memphis, TN-MS-AR'},
    '47169': {'name': 'Trousdale', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47171': {'name': 'Unicoi', 'cbsa': 'metro', 'cbsa_name': 'Johnson City, TN'},
    '47173': {'name': 'Union', 'cbsa': 'metro', 'cbsa_name': 'Knoxville, TN'},
    '47177': {'name': 'Warren', 'cbsa': 'micro', 'cbsa_name': 'McMinnville, TN'},
    '47179': {'name': 'Washington', 'cbsa': 'metro', 'cbsa_name': 'Johnson City, TN'},
    '47183': {'name': 'Weakley', 'cbsa': 'micro', 'cbsa_name': 'Martin, TN'},
    '47185': {'name': 'White', 'cbsa': 'micro', 'cbsa_name': 'Cookeville, TN'},
    '47187': {'name': 'Williamson', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '47189': {'name': 'Wilson', 'cbsa': 'metro', 'cbsa_name': 'Nashville-Davidson--Murfreesboro--Franklin, TN'},
    '51003': {'name': 'Albemarle', 'cbsa': 'metro', 'cbsa_name': 'Charlottesville, VA'},
    '51007': {'name': 'Amelia', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51009': {'name': 'Amherst', 'cbsa': 'metro', 'cbsa_name': 'Lynchburg, VA'},
    '51011': {'name': 'Appomattox', 'cbsa': 'metro', 'cbsa_name': 'Lynchburg, VA'},
    '51013': {'name': 'Arlington', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51015': {'name': 'Augusta', 'cbsa': 'metro', 'cbsa_name': 'Staunton-Stuarts Draft, VA'},
    '51019': {'name': 'Bedford', 'cbsa': 'metro', 'cbsa_name': 'Lynchburg, VA'},
    '51023': {'name': 'Botetourt', 'cbsa': 'metro', 'cbsa_name': 'Roanoke, VA'},
    '51031': {'name': 'Campbell', 'cbsa': 'metro', 'cbsa_name': 'Lynchburg, VA'},
    '51036': {'name': 'Charles City', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51041': {'name': 'Chesterfield', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51043': {'name': 'Clarke', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51045': {'name': 'Craig', 'cbsa': 'metro', 'cbsa_name': 'Roanoke, VA'},
    '51047': {'name': 'Culpeper', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51053': {'name': 'Dinwiddie', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51059': {'name': 'Fairfax', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51061': {'name': 'Fauquier', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51063': {'name': 'Floyd', 'cbsa': 'metro', 'cbsa_name': 'Blacksburg-Christiansburg-Radford, VA'},
    '51065': {'name': 'Fluvanna', 'cbsa': 'metro', 'cbsa_name': 'Charlottesville, VA'},
    '51067': {'name': 'Franklin', 'cbsa': 'metro', 'cbsa_name': 'Roanoke, VA'},
    '51069': {'name': 'Frederick', 'cbsa': 'metro', 'cbsa_name': 'Winchester, VA-WV'},
    '51071': {'name': 'Giles', 'cbsa': 'metro', 'cbsa_name': 'Blacksburg-Christiansburg-Radford, VA'},
    '51073': {'name': 'Gloucester', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51075': {'name': 'Goochland', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51079': {'name': 'Greene', 'cbsa': 'metro', 'cbsa_name': 'Charlottesville, VA'},
    '51085': {'name': 'Hanover', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51087': {'name': 'Henrico', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51089': {'name': 'Henry', 'cbsa': 'micro', 'cbsa_name': 'Martinsville, VA'},
    '51093': {'name': 'Isle of Wight', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51095': {'name': 'James City', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51097': {'name': 'King and Queen', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51101': {'name': 'King William', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51107': {'name': 'Loudoun', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51115': {'name': 'Mathews', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51121': {'name': 'Montgomery', 'cbsa': 'metro', 'cbsa_name': 'Blacksburg-Christiansburg-Radford, VA'},
    '51125': {'name': 'Nelson', 'cbsa': 'metro', 'cbsa_name': 'Charlottesville, VA'},
    '51127': {'name': 'New Kent', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51137': {'name': 'Orange', 'cbsa': 'micro', 'cbsa_name': 'Lake of the Woods, VA'},
    '51143': {'name': 'Pittsylvania', 'cbsa': 'micro', 'cbsa_name': 'Danville, VA'},
    '51145': {'name': 'Powhatan', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51149': {'name': 'Prince George', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51153': {'name': 'Prince William', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51155': {'name': 'Pulaski', 'cbsa': 'metro', 'cbsa_name': 'Blacksburg-Christiansburg-Radford, VA'},
    '51157': {'name': 'Rappahannock', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51161': {'name': 'Roanoke', 'cbsa': 'metro', 'cbsa_name': 'Roanoke, VA'},
    '51165': {'name': 'Rockingham', 'cbsa': 'metro', 'cbsa_name': 'Harrisonburg, VA'},
    '51169': {'name': 'Scott', 'cbsa': 'metro', 'cbsa_name': 'Kingsport-Bristol, TN-VA'},
    '51177': {'name': 'Spotsylvania', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51179': {'name': 'Stafford', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51181': {'name': 'Surry', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51183': {'name': 'Sussex', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51185': {'name': 'Tazewell', 'cbsa': 'micro', 'cbsa_name': 'Bluefield, WV-VA'},
    '51187': {'name': 'Warren', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51191': {'name': 'Washington', 'cbsa': 'metro', 'cbsa_name': 'Kingsport-Bristol, TN-VA'},
    '51199': {'name': 'York', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51510': {'name': 'Alexandria', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51520': {'name': 'Bristol', 'cbsa': 'metro', 'cbsa_name': 'Kingsport-Bristol, TN-VA'},
    '51540': {'name': 'Charlottesville', 'cbsa': 'metro', 'cbsa_name': 'Charlottesville, VA'},
    '51550': {'name': 'Chesapeake', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51570': {'name': 'Colonial Heights', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51590': {'name': 'Danville', 'cbsa': 'micro', 'cbsa_name': 'Danville, VA'},
    '51600': {'name': 'Fairfax', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51610': {'name': 'Falls Church', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51630': {'name': 'Fredericksburg', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51650': {'name': 'Hampton', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51660': {'name': 'Harrisonburg', 'cbsa': 'metro', 'cbsa_name': 'Harrisonburg, VA'},
    '51670': {'name': 'Hopewell', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51680': {'name': 'Lynchburg', 'cbsa': 'metro', 'cbsa_name': 'Lynchburg, VA'},
    '51683': {'name': 'Manassas', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51685': {'name': 'Manassas Park', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '51690': {'name': 'Martinsville', 'cbsa': 'micro', 'cbsa_name': 'Martinsville, VA'},
    '51700': {'name': 'Newport News', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51710': {'name': 'Norfolk', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51730': {'name': 'Petersburg', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51735': {'name': 'Poquoson', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51740': {'name': 'Portsmouth', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51750': {'name': 'Radford', 'cbsa': 'metro', 'cbsa_name': 'Blacksburg-Christiansburg-Radford, VA'},
    '51760': {'name': 'Richmond', 'cbsa': 'metro', 'cbsa_name': 'Richmond, VA'},
    '51770': {'name': 'Roanoke', 'cbsa': 'metro', 'cbsa_name': 'Roanoke, VA'},
    '51775': {'name': 'Salem', 'cbsa': 'metro', 'cbsa_name': 'Roanoke, VA'},
    '51790': {'name': 'Staunton', 'cbsa': 'metro', 'cbsa_name': 'Staunton-Stuarts Draft, VA'},
    '51800': {'name': 'Suffolk', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51810': {'name': 'Virginia Beach', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51820': {'name': 'Waynesboro', 'cbsa': 'metro', 'cbsa_name': 'Staunton-Stuarts Draft, VA'},
    '51830': {'name': 'Williamsburg', 'cbsa': 'metro', 'cbsa_name': 'Virginia Beach-Chesapeake-Norfolk, VA-NC'},
    '51840': {'name': 'Winchester', 'cbsa': 'metro', 'cbsa_name': 'Winchester, VA-WV'},
    '54003': {'name': 'Berkeley', 'cbsa': 'metro', 'cbsa_name': 'Hagerstown-Martinsburg, MD-WV'},
    '54005': {'name': 'Boone', 'cbsa': 'metro', 'cbsa_name': 'Charleston, WV'},
    '54009': {'name': 'Brooke', 'cbsa': 'metro', 'cbsa_name': 'Weirton-Steubenville, WV-OH'},
    '54011': {'name': 'Cabell', 'cbsa': 'metro', 'cbsa_name': 'Huntington-Ashland, WV-KY-OH'},
    '54015': {'name': 'Clay', 'cbsa': 'metro', 'cbsa_name': 'Charleston, WV'},
    '54017': {'name': 'Doddridge', 'cbsa': 'micro', 'cbsa_name': 'Clarksburg, WV'},
    '54019': {'name': 'Fayette', 'cbsa': 'metro', 'cbsa_name': 'Beckley, WV'},
    '54027': {'name': 'Hampshire', 'cbsa': 'metro', 'cbsa_name': 'Winchester, VA-WV'},
    '54029': {'name': 'Hancock', 'cbsa': 'metro', 'cbsa_name': 'Weirton-Steubenville, WV-OH'},
    '54033': {'name': 'Harrison', 'cbsa': 'micro', 'cbsa_name': 'Clarksburg, WV'},
    '54037': {'name': 'Jefferson', 'cbsa': 'metro', 'cbsa_name': 'Washington-Arlington-Alexandria, DC-VA-MD-WV'},
    '54039': {'name': 'Kanawha', 'cbsa': 'metro', 'cbsa_name': 'Charleston, WV'},
    '54049': {'name': 'Marion', 'cbsa': 'micro', 'cbsa_name': 'Fairmont, WV'},
    '54051': {'name': 'Marshall', 'cbsa': 'metro', 'cbsa_name': 'Wheeling, WV-OH'},
    '54055': {'name': 'Mercer', 'cbsa': 'micro', 'cbsa_name': 'Bluefield, WV-VA'},
    '54057': {'name': 'Mineral', 'cbsa': 'micro', 'cbsa_name': 'Cumberland, MD-WV'},
    '54061': {'name': 'Monongalia', 'cbsa': 'metro', 'cbsa_name': 'Morgantown, WV'},
    '54065': {'name': 'Morgan', 'cbsa': 'metro', 'cbsa_name': 'Hagerstown-Martinsburg, MD-WV'},
    '54069': {'name': 'Ohio', 'cbsa': 'metro', 'cbsa_name': 'Wheeling, WV-OH'},
    '54077': {'name': 'Preston', 'cbsa': 'metro', 'cbsa_name': 'Morgantown, WV'},
    '54079': {'name': 'Putnam', 'cbsa': 'metro', 'cbsa_name': 'Huntington-Ashland, WV-KY-OH'},
    '54081': {'name': 'Raleigh', 'cbsa': 'metro', 'cbsa_name': 'Beckley, WV'},
    '54083': {'name': 'Randolph', 'cbsa': 'micro', 'cbsa_name': 'Elkins, WV'},
    '54091': {'name': 'Taylor', 'cbsa': 'micro', 'cbsa_name': 'Clarksburg, WV'},
    '54099': {'name': 'Wayne', 'cbsa': 'metro', 'cbsa_name': 'Huntington-Ashland, WV-KY-OH'},
    '54105': {'name': 'Wirt', 'cbsa': 'metro', 'cbsa_name': 'Parkersburg-Vienna, WV'},
    '54107': {'name': 'Wood', 'cbsa': 'metro', 'cbsa_name': 'Parkersburg-Vienna, WV'},
}

# Classification summary counts
CBSA_SUMMARY = {
    'total_counties': 339,
    'metropolitan': 246,
    'micropolitan': 93,
    'rural': 0
}


def get_cbsa_classification(fips: str) -> Dict:
    """
    Get CBSA classification for a county.

    Args:
        fips: 5-digit FIPS code

    Returns:
        Dictionary with classification info, or default rural if not found
    """
    return CBSA_CLASSIFICATIONS.get(fips, {
        'name': 'Unknown',
        'cbsa': 'rural',
        'cbsa_name': None
    })


def get_micropolitan_percentage(fips_list: list) -> float:
    """
    Calculate percentage of population in micropolitan areas.

    Args:
        fips_list: List of FIPS codes for a region

    Returns:
        Percentage (0-100) of area classified as micropolitan
    """
    total = len(fips_list)
    if total == 0:
        return 0.0

    micro_count = sum(1 for fips in fips_list
                      if get_cbsa_classification(fips)['cbsa'] == 'micro')

    return (micro_count / total) * 100


def classify_region_type(fips_list: list) -> str:
    """
    Classify a region as predominantly metro, micro, or rural.

    Args:
        fips_list: List of FIPS codes for a region

    Returns:
        'metro', 'micro', or 'rural'
    """
    classifications = [get_cbsa_classification(fips)['cbsa'] for fips in fips_list]

    counts = {
        'metro': classifications.count('metro'),
        'micro': classifications.count('micro'),
        'rural': classifications.count('rural')
    }

    # Return classification with highest count
    return max(counts, key=counts.get)
