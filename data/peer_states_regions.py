"""
Peer States Region Definitions for Virginia Thriving Index

This module defines all counties and regions in the peer states used for
comparison with Virginia localities:
- Maryland (MD): 23 counties + 1 independent city
- West Virginia (WV): 55 counties
- North Carolina (NC): 100 counties
- Tennessee (TN): 95 counties
- Kentucky (KY): 120 counties
- Washington DC: Single jurisdiction

Each region includes:
- State FIPS code
- County FIPS code
- County name
- Region type (county or city)

FIPS codes follow the format: SS + CCC where:
- SS = 2-digit state FIPS code
- CCC = 3-digit county FIPS code
"""

# State FIPS codes
STATE_FIPS = {
    'MD': '24',  # Maryland
    'WV': '54',  # West Virginia
    'NC': '37',  # North Carolina
    'TN': '47',  # Tennessee
    'KY': '21',  # Kentucky
    'DC': '11',  # District of Columbia
}

# Maryland: 23 counties + Baltimore City
# Total: 24 regions
MARYLAND_COUNTIES = [
    {'fips': '24001', 'name': 'Allegany County', 'type': 'county'},
    {'fips': '24003', 'name': 'Anne Arundel County', 'type': 'county'},
    {'fips': '24005', 'name': 'Baltimore County', 'type': 'county'},
    {'fips': '24009', 'name': 'Calvert County', 'type': 'county'},
    {'fips': '24011', 'name': 'Caroline County', 'type': 'county'},
    {'fips': '24013', 'name': 'Carroll County', 'type': 'county'},
    {'fips': '24015', 'name': 'Cecil County', 'type': 'county'},
    {'fips': '24017', 'name': 'Charles County', 'type': 'county'},
    {'fips': '24019', 'name': 'Dorchester County', 'type': 'county'},
    {'fips': '24021', 'name': 'Frederick County', 'type': 'county'},
    {'fips': '24023', 'name': 'Garrett County', 'type': 'county'},
    {'fips': '24025', 'name': 'Harford County', 'type': 'county'},
    {'fips': '24027', 'name': 'Howard County', 'type': 'county'},
    {'fips': '24029', 'name': 'Kent County', 'type': 'county'},
    {'fips': '24031', 'name': 'Montgomery County', 'type': 'county'},
    {'fips': '24033', 'name': "Prince George's County", 'type': 'county'},
    {'fips': '24035', 'name': "Queen Anne's County", 'type': 'county'},
    {'fips': '24037', 'name': "St. Mary's County", 'type': 'county'},
    {'fips': '24039', 'name': 'Somerset County', 'type': 'county'},
    {'fips': '24041', 'name': 'Talbot County', 'type': 'county'},
    {'fips': '24043', 'name': 'Washington County', 'type': 'county'},
    {'fips': '24045', 'name': 'Wicomico County', 'type': 'county'},
    {'fips': '24047', 'name': 'Worcester County', 'type': 'county'},
    {'fips': '24510', 'name': 'Baltimore City', 'type': 'city'},
]

# West Virginia: 55 counties
WEST_VIRGINIA_COUNTIES = [
    {'fips': '54001', 'name': 'Barbour County', 'type': 'county'},
    {'fips': '54003', 'name': 'Berkeley County', 'type': 'county'},
    {'fips': '54005', 'name': 'Boone County', 'type': 'county'},
    {'fips': '54007', 'name': 'Braxton County', 'type': 'county'},
    {'fips': '54009', 'name': 'Brooke County', 'type': 'county'},
    {'fips': '54011', 'name': 'Cabell County', 'type': 'county'},
    {'fips': '54013', 'name': 'Calhoun County', 'type': 'county'},
    {'fips': '54015', 'name': 'Clay County', 'type': 'county'},
    {'fips': '54017', 'name': 'Doddridge County', 'type': 'county'},
    {'fips': '54019', 'name': 'Fayette County', 'type': 'county'},
    {'fips': '54021', 'name': 'Gilmer County', 'type': 'county'},
    {'fips': '54023', 'name': 'Grant County', 'type': 'county'},
    {'fips': '54025', 'name': 'Greenbrier County', 'type': 'county'},
    {'fips': '54027', 'name': 'Hampshire County', 'type': 'county'},
    {'fips': '54029', 'name': 'Hancock County', 'type': 'county'},
    {'fips': '54031', 'name': 'Hardy County', 'type': 'county'},
    {'fips': '54033', 'name': 'Harrison County', 'type': 'county'},
    {'fips': '54035', 'name': 'Jackson County', 'type': 'county'},
    {'fips': '54037', 'name': 'Jefferson County', 'type': 'county'},
    {'fips': '54039', 'name': 'Kanawha County', 'type': 'county'},
    {'fips': '54041', 'name': 'Lewis County', 'type': 'county'},
    {'fips': '54043', 'name': 'Lincoln County', 'type': 'county'},
    {'fips': '54045', 'name': 'Logan County', 'type': 'county'},
    {'fips': '54047', 'name': 'McDowell County', 'type': 'county'},
    {'fips': '54049', 'name': 'Marion County', 'type': 'county'},
    {'fips': '54051', 'name': 'Marshall County', 'type': 'county'},
    {'fips': '54053', 'name': 'Mason County', 'type': 'county'},
    {'fips': '54055', 'name': 'Mercer County', 'type': 'county'},
    {'fips': '54057', 'name': 'Mineral County', 'type': 'county'},
    {'fips': '54059', 'name': 'Mingo County', 'type': 'county'},
    {'fips': '54061', 'name': 'Monongalia County', 'type': 'county'},
    {'fips': '54063', 'name': 'Monroe County', 'type': 'county'},
    {'fips': '54065', 'name': 'Morgan County', 'type': 'county'},
    {'fips': '54067', 'name': 'Nicholas County', 'type': 'county'},
    {'fips': '54069', 'name': 'Ohio County', 'type': 'county'},
    {'fips': '54071', 'name': 'Pendleton County', 'type': 'county'},
    {'fips': '54073', 'name': 'Pleasants County', 'type': 'county'},
    {'fips': '54075', 'name': 'Pocahontas County', 'type': 'county'},
    {'fips': '54077', 'name': 'Preston County', 'type': 'county'},
    {'fips': '54079', 'name': 'Putnam County', 'type': 'county'},
    {'fips': '54081', 'name': 'Raleigh County', 'type': 'county'},
    {'fips': '54083', 'name': 'Randolph County', 'type': 'county'},
    {'fips': '54085', 'name': 'Ritchie County', 'type': 'county'},
    {'fips': '54087', 'name': 'Roane County', 'type': 'county'},
    {'fips': '54089', 'name': 'Summers County', 'type': 'county'},
    {'fips': '54091', 'name': 'Taylor County', 'type': 'county'},
    {'fips': '54093', 'name': 'Tucker County', 'type': 'county'},
    {'fips': '54095', 'name': 'Tyler County', 'type': 'county'},
    {'fips': '54097', 'name': 'Upshur County', 'type': 'county'},
    {'fips': '54099', 'name': 'Wayne County', 'type': 'county'},
    {'fips': '54101', 'name': 'Webster County', 'type': 'county'},
    {'fips': '54103', 'name': 'Wetzel County', 'type': 'county'},
    {'fips': '54105', 'name': 'Wirt County', 'type': 'county'},
    {'fips': '54107', 'name': 'Wood County', 'type': 'county'},
    {'fips': '54109', 'name': 'Wyoming County', 'type': 'county'},
]

# North Carolina: 100 counties
# Note: This is a large list - including all 100 NC counties
NORTH_CAROLINA_COUNTIES = [
    {'fips': '37001', 'name': 'Alamance County', 'type': 'county'},
    {'fips': '37003', 'name': 'Alexander County', 'type': 'county'},
    {'fips': '37005', 'name': 'Alleghany County', 'type': 'county'},
    {'fips': '37007', 'name': 'Anson County', 'type': 'county'},
    {'fips': '37009', 'name': 'Ashe County', 'type': 'county'},
    {'fips': '37011', 'name': 'Avery County', 'type': 'county'},
    {'fips': '37013', 'name': 'Beaufort County', 'type': 'county'},
    {'fips': '37015', 'name': 'Bertie County', 'type': 'county'},
    {'fips': '37017', 'name': 'Bladen County', 'type': 'county'},
    {'fips': '37019', 'name': 'Brunswick County', 'type': 'county'},
    {'fips': '37021', 'name': 'Buncombe County', 'type': 'county'},
    {'fips': '37023', 'name': 'Burke County', 'type': 'county'},
    {'fips': '37025', 'name': 'Cabarrus County', 'type': 'county'},
    {'fips': '37027', 'name': 'Caldwell County', 'type': 'county'},
    {'fips': '37029', 'name': 'Camden County', 'type': 'county'},
    {'fips': '37031', 'name': 'Carteret County', 'type': 'county'},
    {'fips': '37033', 'name': 'Caswell County', 'type': 'county'},
    {'fips': '37035', 'name': 'Catawba County', 'type': 'county'},
    {'fips': '37037', 'name': 'Chatham County', 'type': 'county'},
    {'fips': '37039', 'name': 'Cherokee County', 'type': 'county'},
    {'fips': '37041', 'name': 'Chowan County', 'type': 'county'},
    {'fips': '37043', 'name': 'Clay County', 'type': 'county'},
    {'fips': '37045', 'name': 'Cleveland County', 'type': 'county'},
    {'fips': '37047', 'name': 'Columbus County', 'type': 'county'},
    {'fips': '37049', 'name': 'Craven County', 'type': 'county'},
    {'fips': '37051', 'name': 'Cumberland County', 'type': 'county'},
    {'fips': '37053', 'name': 'Currituck County', 'type': 'county'},
    {'fips': '37055', 'name': 'Dare County', 'type': 'county'},
    {'fips': '37057', 'name': 'Davidson County', 'type': 'county'},
    {'fips': '37059', 'name': 'Davie County', 'type': 'county'},
    {'fips': '37061', 'name': 'Duplin County', 'type': 'county'},
    {'fips': '37063', 'name': 'Durham County', 'type': 'county'},
    {'fips': '37065', 'name': 'Edgecombe County', 'type': 'county'},
    {'fips': '37067', 'name': 'Forsyth County', 'type': 'county'},
    {'fips': '37069', 'name': 'Franklin County', 'type': 'county'},
    {'fips': '37071', 'name': 'Gaston County', 'type': 'county'},
    {'fips': '37073', 'name': 'Gates County', 'type': 'county'},
    {'fips': '37075', 'name': 'Graham County', 'type': 'county'},
    {'fips': '37077', 'name': 'Granville County', 'type': 'county'},
    {'fips': '37079', 'name': 'Greene County', 'type': 'county'},
    {'fips': '37081', 'name': 'Guilford County', 'type': 'county'},
    {'fips': '37083', 'name': 'Halifax County', 'type': 'county'},
    {'fips': '37085', 'name': 'Harnett County', 'type': 'county'},
    {'fips': '37087', 'name': 'Haywood County', 'type': 'county'},
    {'fips': '37089', 'name': 'Henderson County', 'type': 'county'},
    {'fips': '37091', 'name': 'Hertford County', 'type': 'county'},
    {'fips': '37093', 'name': 'Hoke County', 'type': 'county'},
    {'fips': '37095', 'name': 'Hyde County', 'type': 'county'},
    {'fips': '37097', 'name': 'Iredell County', 'type': 'county'},
    {'fips': '37099', 'name': 'Jackson County', 'type': 'county'},
    {'fips': '37101', 'name': 'Johnston County', 'type': 'county'},
    {'fips': '37103', 'name': 'Jones County', 'type': 'county'},
    {'fips': '37105', 'name': 'Lee County', 'type': 'county'},
    {'fips': '37107', 'name': 'Lenoir County', 'type': 'county'},
    {'fips': '37109', 'name': 'Lincoln County', 'type': 'county'},
    {'fips': '37111', 'name': 'McDowell County', 'type': 'county'},
    {'fips': '37113', 'name': 'Macon County', 'type': 'county'},
    {'fips': '37115', 'name': 'Madison County', 'type': 'county'},
    {'fips': '37117', 'name': 'Martin County', 'type': 'county'},
    {'fips': '37119', 'name': 'Mecklenburg County', 'type': 'county'},
    {'fips': '37121', 'name': 'Mitchell County', 'type': 'county'},
    {'fips': '37123', 'name': 'Montgomery County', 'type': 'county'},
    {'fips': '37125', 'name': 'Moore County', 'type': 'county'},
    {'fips': '37127', 'name': 'Nash County', 'type': 'county'},
    {'fips': '37129', 'name': 'New Hanover County', 'type': 'county'},
    {'fips': '37131', 'name': 'Northampton County', 'type': 'county'},
    {'fips': '37133', 'name': 'Onslow County', 'type': 'county'},
    {'fips': '37135', 'name': 'Orange County', 'type': 'county'},
    {'fips': '37137', 'name': 'Pamlico County', 'type': 'county'},
    {'fips': '37139', 'name': 'Pasquotank County', 'type': 'county'},
    {'fips': '37141', 'name': 'Pender County', 'type': 'county'},
    {'fips': '37143', 'name': 'Perquimans County', 'type': 'county'},
    {'fips': '37145', 'name': 'Person County', 'type': 'county'},
    {'fips': '37147', 'name': 'Pitt County', 'type': 'county'},
    {'fips': '37149', 'name': 'Polk County', 'type': 'county'},
    {'fips': '37151', 'name': 'Randolph County', 'type': 'county'},
    {'fips': '37153', 'name': 'Richmond County', 'type': 'county'},
    {'fips': '37155', 'name': 'Robeson County', 'type': 'county'},
    {'fips': '37157', 'name': 'Rockingham County', 'type': 'county'},
    {'fips': '37159', 'name': 'Rowan County', 'type': 'county'},
    {'fips': '37161', 'name': 'Rutherford County', 'type': 'county'},
    {'fips': '37163', 'name': 'Sampson County', 'type': 'county'},
    {'fips': '37165', 'name': 'Scotland County', 'type': 'county'},
    {'fips': '37167', 'name': 'Stanly County', 'type': 'county'},
    {'fips': '37169', 'name': 'Stokes County', 'type': 'county'},
    {'fips': '37171', 'name': 'Surry County', 'type': 'county'},
    {'fips': '37173', 'name': 'Swain County', 'type': 'county'},
    {'fips': '37175', 'name': 'Transylvania County', 'type': 'county'},
    {'fips': '37177', 'name': 'Tyrrell County', 'type': 'county'},
    {'fips': '37179', 'name': 'Union County', 'type': 'county'},
    {'fips': '37181', 'name': 'Vance County', 'type': 'county'},
    {'fips': '37183', 'name': 'Wake County', 'type': 'county'},
    {'fips': '37185', 'name': 'Warren County', 'type': 'county'},
    {'fips': '37187', 'name': 'Washington County', 'type': 'county'},
    {'fips': '37189', 'name': 'Watauga County', 'type': 'county'},
    {'fips': '37191', 'name': 'Wayne County', 'type': 'county'},
    {'fips': '37193', 'name': 'Wilkes County', 'type': 'county'},
    {'fips': '37195', 'name': 'Wilson County', 'type': 'county'},
    {'fips': '37197', 'name': 'Yadkin County', 'type': 'county'},
    {'fips': '37199', 'name': 'Yancey County', 'type': 'county'},
]

# Tennessee: 95 counties
TENNESSEE_COUNTIES = [
    {'fips': '47001', 'name': 'Anderson County', 'type': 'county'},
    {'fips': '47003', 'name': 'Bedford County', 'type': 'county'},
    {'fips': '47005', 'name': 'Benton County', 'type': 'county'},
    {'fips': '47007', 'name': 'Bledsoe County', 'type': 'county'},
    {'fips': '47009', 'name': 'Blount County', 'type': 'county'},
    {'fips': '47011', 'name': 'Bradley County', 'type': 'county'},
    {'fips': '47013', 'name': 'Campbell County', 'type': 'county'},
    {'fips': '47015', 'name': 'Cannon County', 'type': 'county'},
    {'fips': '47017', 'name': 'Carroll County', 'type': 'county'},
    {'fips': '47019', 'name': 'Carter County', 'type': 'county'},
    {'fips': '47021', 'name': 'Cheatham County', 'type': 'county'},
    {'fips': '47023', 'name': 'Chester County', 'type': 'county'},
    {'fips': '47025', 'name': 'Claiborne County', 'type': 'county'},
    {'fips': '47027', 'name': 'Clay County', 'type': 'county'},
    {'fips': '47029', 'name': 'Cocke County', 'type': 'county'},
    {'fips': '47031', 'name': 'Coffee County', 'type': 'county'},
    {'fips': '47033', 'name': 'Crockett County', 'type': 'county'},
    {'fips': '47035', 'name': 'Cumberland County', 'type': 'county'},
    {'fips': '47037', 'name': 'Davidson County', 'type': 'county'},
    {'fips': '47039', 'name': 'Decatur County', 'type': 'county'},
    {'fips': '47041', 'name': 'DeKalb County', 'type': 'county'},
    {'fips': '47043', 'name': 'Dickson County', 'type': 'county'},
    {'fips': '47045', 'name': 'Dyer County', 'type': 'county'},
    {'fips': '47047', 'name': 'Fayette County', 'type': 'county'},
    {'fips': '47049', 'name': 'Fentress County', 'type': 'county'},
    {'fips': '47051', 'name': 'Franklin County', 'type': 'county'},
    {'fips': '47053', 'name': 'Gibson County', 'type': 'county'},
    {'fips': '47055', 'name': 'Giles County', 'type': 'county'},
    {'fips': '47057', 'name': 'Grainger County', 'type': 'county'},
    {'fips': '47059', 'name': 'Greene County', 'type': 'county'},
    {'fips': '47061', 'name': 'Grundy County', 'type': 'county'},
    {'fips': '47063', 'name': 'Hamblen County', 'type': 'county'},
    {'fips': '47065', 'name': 'Hamilton County', 'type': 'county'},
    {'fips': '47067', 'name': 'Hancock County', 'type': 'county'},
    {'fips': '47069', 'name': 'Hardeman County', 'type': 'county'},
    {'fips': '47071', 'name': 'Hardin County', 'type': 'county'},
    {'fips': '47073', 'name': 'Hawkins County', 'type': 'county'},
    {'fips': '47075', 'name': 'Haywood County', 'type': 'county'},
    {'fips': '47077', 'name': 'Henderson County', 'type': 'county'},
    {'fips': '47079', 'name': 'Henry County', 'type': 'county'},
    {'fips': '47081', 'name': 'Hickman County', 'type': 'county'},
    {'fips': '47083', 'name': 'Houston County', 'type': 'county'},
    {'fips': '47085', 'name': 'Humphreys County', 'type': 'county'},
    {'fips': '47087', 'name': 'Jackson County', 'type': 'county'},
    {'fips': '47089', 'name': 'Jefferson County', 'type': 'county'},
    {'fips': '47091', 'name': 'Johnson County', 'type': 'county'},
    {'fips': '47093', 'name': 'Knox County', 'type': 'county'},
    {'fips': '47095', 'name': 'Lake County', 'type': 'county'},
    {'fips': '47097', 'name': 'Lauderdale County', 'type': 'county'},
    {'fips': '47099', 'name': 'Lawrence County', 'type': 'county'},
    {'fips': '47101', 'name': 'Lewis County', 'type': 'county'},
    {'fips': '47103', 'name': 'Lincoln County', 'type': 'county'},
    {'fips': '47105', 'name': 'Loudon County', 'type': 'county'},
    {'fips': '47107', 'name': 'McMinn County', 'type': 'county'},
    {'fips': '47109', 'name': 'McNairy County', 'type': 'county'},
    {'fips': '47111', 'name': 'Macon County', 'type': 'county'},
    {'fips': '47113', 'name': 'Madison County', 'type': 'county'},
    {'fips': '47115', 'name': 'Marion County', 'type': 'county'},
    {'fips': '47117', 'name': 'Marshall County', 'type': 'county'},
    {'fips': '47119', 'name': 'Maury County', 'type': 'county'},
    {'fips': '47121', 'name': 'Meigs County', 'type': 'county'},
    {'fips': '47123', 'name': 'Monroe County', 'type': 'county'},
    {'fips': '47125', 'name': 'Montgomery County', 'type': 'county'},
    {'fips': '47127', 'name': 'Moore County', 'type': 'county'},
    {'fips': '47129', 'name': 'Morgan County', 'type': 'county'},
    {'fips': '47131', 'name': 'Obion County', 'type': 'county'},
    {'fips': '47133', 'name': 'Overton County', 'type': 'county'},
    {'fips': '47135', 'name': 'Perry County', 'type': 'county'},
    {'fips': '47137', 'name': 'Pickett County', 'type': 'county'},
    {'fips': '47139', 'name': 'Polk County', 'type': 'county'},
    {'fips': '47141', 'name': 'Putnam County', 'type': 'county'},
    {'fips': '47143', 'name': 'Rhea County', 'type': 'county'},
    {'fips': '47145', 'name': 'Roane County', 'type': 'county'},
    {'fips': '47147', 'name': 'Robertson County', 'type': 'county'},
    {'fips': '47149', 'name': 'Rutherford County', 'type': 'county'},
    {'fips': '47151', 'name': 'Scott County', 'type': 'county'},
    {'fips': '47153', 'name': 'Sequatchie County', 'type': 'county'},
    {'fips': '47155', 'name': 'Sevier County', 'type': 'county'},
    {'fips': '47157', 'name': 'Shelby County', 'type': 'county'},
    {'fips': '47159', 'name': 'Smith County', 'type': 'county'},
    {'fips': '47161', 'name': 'Stewart County', 'type': 'county'},
    {'fips': '47163', 'name': 'Sullivan County', 'type': 'county'},
    {'fips': '47165', 'name': 'Sumner County', 'type': 'county'},
    {'fips': '47167', 'name': 'Tipton County', 'type': 'county'},
    {'fips': '47169', 'name': 'Trousdale County', 'type': 'county'},
    {'fips': '47171', 'name': 'Unicoi County', 'type': 'county'},
    {'fips': '47173', 'name': 'Union County', 'type': 'county'},
    {'fips': '47175', 'name': 'Van Buren County', 'type': 'county'},
    {'fips': '47177', 'name': 'Warren County', 'type': 'county'},
    {'fips': '47179', 'name': 'Washington County', 'type': 'county'},
    {'fips': '47181', 'name': 'Wayne County', 'type': 'county'},
    {'fips': '47183', 'name': 'Weakley County', 'type': 'county'},
    {'fips': '47185', 'name': 'White County', 'type': 'county'},
    {'fips': '47187', 'name': 'Williamson County', 'type': 'county'},
    {'fips': '47189', 'name': 'Wilson County', 'type': 'county'},
]

# Kentucky: 120 counties
# Note: Kentucky has the most counties in our peer states
KENTUCKY_COUNTIES = [
    {'fips': '21001', 'name': 'Adair County', 'type': 'county'},
    {'fips': '21003', 'name': 'Allen County', 'type': 'county'},
    {'fips': '21005', 'name': 'Anderson County', 'type': 'county'},
    {'fips': '21007', 'name': 'Ballard County', 'type': 'county'},
    {'fips': '21009', 'name': 'Barren County', 'type': 'county'},
    {'fips': '21011', 'name': 'Bath County', 'type': 'county'},
    {'fips': '21013', 'name': 'Bell County', 'type': 'county'},
    {'fips': '21015', 'name': 'Boone County', 'type': 'county'},
    {'fips': '21017', 'name': 'Bourbon County', 'type': 'county'},
    {'fips': '21019', 'name': 'Boyd County', 'type': 'county'},
    {'fips': '21021', 'name': 'Boyle County', 'type': 'county'},
    {'fips': '21023', 'name': 'Bracken County', 'type': 'county'},
    {'fips': '21025', 'name': 'Breathitt County', 'type': 'county'},
    {'fips': '21027', 'name': 'Breckinridge County', 'type': 'county'},
    {'fips': '21029', 'name': 'Bullitt County', 'type': 'county'},
    {'fips': '21031', 'name': 'Butler County', 'type': 'county'},
    {'fips': '21033', 'name': 'Caldwell County', 'type': 'county'},
    {'fips': '21035', 'name': 'Calloway County', 'type': 'county'},
    {'fips': '21037', 'name': 'Campbell County', 'type': 'county'},
    {'fips': '21039', 'name': 'Carlisle County', 'type': 'county'},
    {'fips': '21041', 'name': 'Carroll County', 'type': 'county'},
    {'fips': '21043', 'name': 'Carter County', 'type': 'county'},
    {'fips': '21045', 'name': 'Casey County', 'type': 'county'},
    {'fips': '21047', 'name': 'Christian County', 'type': 'county'},
    {'fips': '21049', 'name': 'Clark County', 'type': 'county'},
    {'fips': '21051', 'name': 'Clay County', 'type': 'county'},
    {'fips': '21053', 'name': 'Clinton County', 'type': 'county'},
    {'fips': '21055', 'name': 'Crittenden County', 'type': 'county'},
    {'fips': '21057', 'name': 'Cumberland County', 'type': 'county'},
    {'fips': '21059', 'name': 'Daviess County', 'type': 'county'},
    {'fips': '21061', 'name': 'Edmonson County', 'type': 'county'},
    {'fips': '21063', 'name': 'Elliott County', 'type': 'county'},
    {'fips': '21065', 'name': 'Estill County', 'type': 'county'},
    {'fips': '21067', 'name': 'Fayette County', 'type': 'county'},
    {'fips': '21069', 'name': 'Fleming County', 'type': 'county'},
    {'fips': '21071', 'name': 'Floyd County', 'type': 'county'},
    {'fips': '21073', 'name': 'Franklin County', 'type': 'county'},
    {'fips': '21075', 'name': 'Fulton County', 'type': 'county'},
    {'fips': '21077', 'name': 'Gallatin County', 'type': 'county'},
    {'fips': '21079', 'name': 'Garrard County', 'type': 'county'},
    {'fips': '21081', 'name': 'Grant County', 'type': 'county'},
    {'fips': '21083', 'name': 'Graves County', 'type': 'county'},
    {'fips': '21085', 'name': 'Grayson County', 'type': 'county'},
    {'fips': '21087', 'name': 'Green County', 'type': 'county'},
    {'fips': '21089', 'name': 'Greenup County', 'type': 'county'},
    {'fips': '21091', 'name': 'Hancock County', 'type': 'county'},
    {'fips': '21093', 'name': 'Hardin County', 'type': 'county'},
    {'fips': '21095', 'name': 'Harlan County', 'type': 'county'},
    {'fips': '21097', 'name': 'Harrison County', 'type': 'county'},
    {'fips': '21099', 'name': 'Hart County', 'type': 'county'},
    {'fips': '21101', 'name': 'Henderson County', 'type': 'county'},
    {'fips': '21103', 'name': 'Henry County', 'type': 'county'},
    {'fips': '21105', 'name': 'Hickman County', 'type': 'county'},
    {'fips': '21107', 'name': 'Hopkins County', 'type': 'county'},
    {'fips': '21109', 'name': 'Jackson County', 'type': 'county'},
    {'fips': '21111', 'name': 'Jefferson County', 'type': 'county'},
    {'fips': '21113', 'name': 'Jessamine County', 'type': 'county'},
    {'fips': '21115', 'name': 'Johnson County', 'type': 'county'},
    {'fips': '21117', 'name': 'Kenton County', 'type': 'county'},
    {'fips': '21119', 'name': 'Knott County', 'type': 'county'},
    {'fips': '21121', 'name': 'Knox County', 'type': 'county'},
    {'fips': '21123', 'name': 'Larue County', 'type': 'county'},
    {'fips': '21125', 'name': 'Laurel County', 'type': 'county'},
    {'fips': '21127', 'name': 'Lawrence County', 'type': 'county'},
    {'fips': '21129', 'name': 'Lee County', 'type': 'county'},
    {'fips': '21131', 'name': 'Leslie County', 'type': 'county'},
    {'fips': '21133', 'name': 'Letcher County', 'type': 'county'},
    {'fips': '21135', 'name': 'Lewis County', 'type': 'county'},
    {'fips': '21137', 'name': 'Lincoln County', 'type': 'county'},
    {'fips': '21139', 'name': 'Livingston County', 'type': 'county'},
    {'fips': '21141', 'name': 'Logan County', 'type': 'county'},
    {'fips': '21143', 'name': 'Lyon County', 'type': 'county'},
    {'fips': '21145', 'name': 'McCracken County', 'type': 'county'},
    {'fips': '21147', 'name': 'McCreary County', 'type': 'county'},
    {'fips': '21149', 'name': 'McLean County', 'type': 'county'},
    {'fips': '21151', 'name': 'Madison County', 'type': 'county'},
    {'fips': '21153', 'name': 'Magoffin County', 'type': 'county'},
    {'fips': '21155', 'name': 'Marion County', 'type': 'county'},
    {'fips': '21157', 'name': 'Marshall County', 'type': 'county'},
    {'fips': '21159', 'name': 'Martin County', 'type': 'county'},
    {'fips': '21161', 'name': 'Mason County', 'type': 'county'},
    {'fips': '21163', 'name': 'Meade County', 'type': 'county'},
    {'fips': '21165', 'name': 'Menifee County', 'type': 'county'},
    {'fips': '21167', 'name': 'Mercer County', 'type': 'county'},
    {'fips': '21169', 'name': 'Metcalfe County', 'type': 'county'},
    {'fips': '21171', 'name': 'Monroe County', 'type': 'county'},
    {'fips': '21173', 'name': 'Montgomery County', 'type': 'county'},
    {'fips': '21175', 'name': 'Morgan County', 'type': 'county'},
    {'fips': '21177', 'name': 'Muhlenberg County', 'type': 'county'},
    {'fips': '21179', 'name': 'Nelson County', 'type': 'county'},
    {'fips': '21181', 'name': 'Nicholas County', 'type': 'county'},
    {'fips': '21183', 'name': 'Ohio County', 'type': 'county'},
    {'fips': '21185', 'name': 'Oldham County', 'type': 'county'},
    {'fips': '21187', 'name': 'Owen County', 'type': 'county'},
    {'fips': '21189', 'name': 'Owsley County', 'type': 'county'},
    {'fips': '21191', 'name': 'Pendleton County', 'type': 'county'},
    {'fips': '21193', 'name': 'Perry County', 'type': 'county'},
    {'fips': '21195', 'name': 'Pike County', 'type': 'county'},
    {'fips': '21197', 'name': 'Powell County', 'type': 'county'},
    {'fips': '21199', 'name': 'Pulaski County', 'type': 'county'},
    {'fips': '21201', 'name': 'Robertson County', 'type': 'county'},
    {'fips': '21203', 'name': 'Rockcastle County', 'type': 'county'},
    {'fips': '21205', 'name': 'Rowan County', 'type': 'county'},
    {'fips': '21207', 'name': 'Russell County', 'type': 'county'},
    {'fips': '21209', 'name': 'Scott County', 'type': 'county'},
    {'fips': '21211', 'name': 'Shelby County', 'type': 'county'},
    {'fips': '21213', 'name': 'Simpson County', 'type': 'county'},
    {'fips': '21215', 'name': 'Spencer County', 'type': 'county'},
    {'fips': '21217', 'name': 'Taylor County', 'type': 'county'},
    {'fips': '21219', 'name': 'Todd County', 'type': 'county'},
    {'fips': '21221', 'name': 'Trigg County', 'type': 'county'},
    {'fips': '21223', 'name': 'Trimble County', 'type': 'county'},
    {'fips': '21225', 'name': 'Union County', 'type': 'county'},
    {'fips': '21227', 'name': 'Warren County', 'type': 'county'},
    {'fips': '21229', 'name': 'Washington County', 'type': 'county'},
    {'fips': '21231', 'name': 'Wayne County', 'type': 'county'},
    {'fips': '21233', 'name': 'Webster County', 'type': 'county'},
    {'fips': '21235', 'name': 'Whitley County', 'type': 'county'},
    {'fips': '21237', 'name': 'Wolfe County', 'type': 'county'},
    {'fips': '21239', 'name': 'Woodford County', 'type': 'county'},
]

# District of Columbia: Single jurisdiction
DISTRICT_OF_COLUMBIA = [
    {'fips': '11001', 'name': 'District of Columbia', 'type': 'district'},
]

# Combined dictionary of all peer state regions
ALL_PEER_REGIONS = {
    'MD': MARYLAND_COUNTIES,
    'WV': WEST_VIRGINIA_COUNTIES,
    'NC': NORTH_CAROLINA_COUNTIES,
    'TN': TENNESSEE_COUNTIES,
    'KY': KENTUCKY_COUNTIES,
    'DC': DISTRICT_OF_COLUMBIA,
}

# Summary statistics
PEER_STATES_SUMMARY = {
    'total_regions': (
        len(MARYLAND_COUNTIES) +
        len(WEST_VIRGINIA_COUNTIES) +
        len(NORTH_CAROLINA_COUNTIES) +
        len(TENNESSEE_COUNTIES) +
        len(KENTUCKY_COUNTIES) +
        len(DISTRICT_OF_COLUMBIA)
    ),
    'by_state': {
        'MD': len(MARYLAND_COUNTIES),
        'WV': len(WEST_VIRGINIA_COUNTIES),
        'NC': len(NORTH_CAROLINA_COUNTIES),
        'TN': len(TENNESSEE_COUNTIES),
        'KY': len(KENTUCKY_COUNTIES),
        'DC': len(DISTRICT_OF_COLUMBIA),
    }
}


def get_all_peer_regions():
    """
    Returns a flat list of all peer state regions.

    Returns:
        list: List of dictionaries with region information including state
    """
    all_regions = []
    for state, regions in ALL_PEER_REGIONS.items():
        for region in regions:
            region_copy = region.copy()
            region_copy['state'] = state
            all_regions.append(region_copy)
    return all_regions


def get_regions_by_state(state_code):
    """
    Get all regions for a specific state.

    Args:
        state_code (str): Two-letter state code (MD, WV, NC, TN, KY, DC)

    Returns:
        list: List of region dictionaries, or empty list if state not found
    """
    return ALL_PEER_REGIONS.get(state_code.upper(), [])


def get_region_by_fips(fips_code):
    """
    Look up a specific region by its FIPS code.

    Args:
        fips_code (str): 5-digit FIPS code

    Returns:
        dict: Region information, or None if not found
    """
    all_regions = get_all_peer_regions()
    for region in all_regions:
        if region['fips'] == fips_code:
            return region
    return None


if __name__ == '__main__':
    # Print summary when run directly
    print("Peer States Region Summary")
    print("=" * 50)
    print(f"Total peer regions: {PEER_STATES_SUMMARY['total_regions']}")
    print("\nBreakdown by state:")
    for state, count in PEER_STATES_SUMMARY['by_state'].items():
        print(f"  {state}: {count} regions")

    print("\nSample regions from each state:")
    for state in ['MD', 'WV', 'NC', 'TN', 'KY', 'DC']:
        regions = get_regions_by_state(state)
        if regions:
            print(f"\n{state} ({len(regions)} total):")
            # Show first 3 regions
            for region in regions[:3]:
                print(f"  - {region['name']} (FIPS: {region['fips']})")
            if len(regions) > 3:
                print(f"  ... and {len(regions) - 3} more")
