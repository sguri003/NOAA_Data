#
#   Written by:  Mark W Kiehl
#   http://mechatronicsolutionsllc.com/
#   http://www.savvysolutions.info/savvycodesolutions/

#   Altered by:  Steven Guridi
#   Former Florida Power & Light Worker living in florida/storm export
#   I have not been able to pull data from NOAA since 2021. 
#   FYI: NOAA IS NOT CELLECTIN STORM DATA AFTER 2O21 NOR TEMP, WIND, ETC.
#   ORIGINAL EDITOR: MARK W KIESHI HAD TO HARDCDE STATIONS BECAUSE OF CHANGES TO NOAA
#   API FROM 2020-2021. NOAA IS NOT RECORDING AND THIS WHAT FIRST RESPONDER'S USE FOR STORM ASSESMENT. 
#   OBJECTIVE: TO CHANGE MARKS CODE AND FIND WEATHER DATA POINTS. NOAA DOES NOT STORE ANY STORM NAMES PRIOR 2021
#   2025 FLORIDA IS HAVING A LOT OF HAIL, I AM ALTERING THE CODE AND JSON RESULTS TO SOMEHOW FIND WEATHER DATA POINTS.
#   CONCLUSION: ALTERING MIKES CODE TO FIND WIND, TEMP, HUMIDITY PAST 2021. NO STORM NAMES WILL APPEAR THOUGH
"""
Extraction of historical climate data from NOAA National Centers for Environmental Information (NCEI) using their new (2023) API.

IMPORTANT:

The old (depreciated) endpoint is: https://www.ncei.noaa.gov/cdo-web/api/v2 
The old documentation: https://www.ncdc.noaa.gov/cdo-web/webservices/

Two new endpoints exist, one to search and another to aquire data.
The new search endpoint is: https://www.ncei.noaa.gov/access/services/search/v1/data
Example HTTP GET for search: https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=daily-summaries&startDate=2010-01-01T00:00:00&endDate=2016-12-31T23:09:59&boundingBox=35.462327,-82.563951,35.412327,-82.513951&dataTypes=PRCP&stations=USW00003812&limit=10&offset=0
Search service documentation: https://www.ncei.noaa.gov/support/access-search-service-api-user-documentation

The new data endpoint is: https://www.ncei.noaa.gov/access/services/data/v1
Example HTTP GET for data: https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-summary-of-the-year&dataTypes=DP01,DP05,DP10,DSND,DSNW,DT00,DT32,DX32,DX70,DX90,SNOW,PRCP&stations=ASN00084027&startDate=1952-01-01&endDate=1970-12-31&includeAttributes=true&format=json
Data endpoint documentation: https://www.ncei.noaa.gov/support/access-data-service-api-user-documentation

Access Support Service  (Management Service API (v3))
https://www.ncei.noaa.gov/support/access-support-service



https://medium.com/@markwkiehl/noaa-climate-api-c2e36e7a49c5


WORKFLOW
- Use the Search Service endpoint to find weather stations near the target location, with type of data set of interest, and the the data type(s).
- Pass the station id to the Data Service endpoint to acquire the data.


TEMPERATURE CHANGE BY ELEVATION & LATITUDE

The temperature drops 5.4 F every 1000 ft (305 m) in elevation gain on a sunny day. 
Temperature changes 1.3 F (0.7 C) for every degree change in latitude. 
One degree of latitude = 69 mi = 111 km = 110567 m
A latitude change of 265 miles toward the equator will increase the temperature 5 F. 
A latitude change of 3.8 degrees toward the equator will increase the temperature 5 F. 

DATA TYPES

See the output at the end of get_noaa_ncei_datatypes_by_dataset() for lists of datatypes by dataset. 



NWS Directive 10-1605
NWS Directive 10-1605 is a National Weather Service (NWS) Instruction titled "Storm Data Preparation."
This directive outlines the specific procedures and guidelines that NWS Weather Forecast Offices (WFOs) 
must follow for collecting, compiling, and submitting severe weather event data to the Storm Events Database, 
which is maintained by the National Centers for Environmental Information (NCEI) and is part of the broader 
Severe Weather Data Inventory (SWDI).
Event Types: It defines the official list of weather event types that are to be included in Storm Data 
(e.g., Tornado, Hail, Thunderstorm Wind, Flash Flood, Heavy Snow, Extreme Cold/Wind Chill, etc.).
Data Elements: It details what information needs to be collected for each event.
Reporting Standards: It sets standards for how this information should be recorded, including consistent 
terminology, units of measurement, and procedures for estimating damage.
NWS Directive 10-1605, "Storm Data Preparation," was initially put into use on January 6, 2003.
It superseded previous instructions, specifically Weather Service Operations Manual (WSOM) Chapter F-42, 
"Storm Data and Related Reports," Issuance 94-5, dated July 1, 1994, and other Operations Manual Letters.



pip install requests
pip install geocodio
pip install folium
pip install numpy
pip install python-dotenv
pip install rfc3339-validator
"""

#   The source for this file api_noaa.py resides in the 'api' folder.

# Define the script version in terms of Semantic Versioning (SemVer)
# when Git or other versioning systems are not employed.
__version__ = "0.0.0"
from pathlib import Path
print("'" + Path(__file__).stem + ".py'  v" + __version__)
# v0.0.0    Initial release


from time import perf_counter
t_start_sec = perf_counter()


# ---------------------------------------------------------------------------
# Configure the required API keys to be retrieved from either the module savvy_secrets or the local .env file.
# *** Update the .env file with your API keys for NOAA, Google Maps, and Geocodio and everything will work ***

import os
import sys
from pathlib import Path

# Retrieve API Keys stored in the local .env file (if it exists).
import os
try:
	# pip install python-dotenv
    from dotenv import load_dotenv
except Exception as e:
    raise Exception(f"{e} \t Is dotenv module installed?  pip install python-dotenv")
# Load environment variables from the .env file
load_dotenv()

# Add path 'savvy' so it can be found for library imports, including the module savvy_secrets.
from pathlib import Path
import sys
sys.path.insert(1, str(Path(Path.cwd().parent).joinpath('savvy')))      

# API_GEOCODIO_KEY
#if Path.cwd().parts[len(Path.cwd().parts)-1]=="savvy" or str(Path(Path.cwd().parent).joinpath("savvy")) in sys.path:
    # The folder 'savvy' is the current project path OR it exists in the Python interpreter's search path for modules.
    # Get the API Key from the module savvy_secrets and define the OS environment variable.
#   try:
#       from savvy_secrets import api_secrets
#    except Exception as e:
#        raise Exception(f"{e}\nThe folder 'savvy' is not the current project folder NOR does it exist in the Python interpreter's search path for modules (sys.path). Try: sys.path.insert(1, str(Path(Path.cwd().parent).joinpath('savvy')))")
#    if not "api_geocodio" in api_secrets.keys(): raise Exception("ERROR: api_secrets from savvy_secrets.py doesn't have the key 'api_geocodio'.")
os.environ['API_GEOCODIO_KEY']
# Verify the Windows environment variable API_GEOCODIO_KEY is set & demonstrate how to access it.
if not os.getenv('API_GEOCODIO_KEY'): raise Exception("Windows environment variable 'API_GEOCODIO_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

# API_NOAA_NCEI
#if Path.cwd().parts[len(Path.cwd().parts)-1]=="savvy" or str(Path(Path.cwd().parent).joinpath("savvy")) in sys.path:
    # The folder 'savvy' is the current project path OR it exists in the Python interpreter's search path for modules.
    # Get the API Key from the module savvy_secrets and define the OS environment variable.
#    try:
#        from savvy_secrets import api_secrets
#    except Exception as e:
#        raise Exception(f"{e}\nThe folder 'savvy' is not the current project folder NOR does it exist in the Python interpreter's search path for modules (sys.path). Try: sys.path.insert(1, str(Path(Path.cwd().parent).joinpath('savvy')))")
#    if not "api_noaa_header_key_mwk" in api_secrets.keys(): raise Exception("ERROR: api_secrets from savvy_secrets.py doesn't have the key 'api_noaa_header_key_mwk'.")
os.environ['API_NOAA_NCEI']
# Verify the Windows environment variable API_NOAA_NCEI is set & demonstrate how to access it.
if not os.getenv('API_NOAA_NCEI'): raise Exception("Windows environment variable 'API_NOAA_NCEI' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")
# ---------------------------------------------------------------------------
# Imports

from savvy_gps import haversine_distance, elevation_by_lat_lon, midpoint_euclidean, get_gps_bounding_box, lat_lon_is_valid


# ---------------------------------------------------------------------------
# savvy_requests.py

#from savvy_requests import savvy_request_get

def savvy_request_get(url:str=None, retries:int=3, headers:dict=None, verbose=False):
    """
    Returns the response object from a HTTP GET to 'url' of up to 'retries' attempts for HTTP response codes 429,500-504.
    Returns None for other errors. 
    Argument headers is optional.
    Note: If experience HTTP 403 Forbidden error, try savvy_request_get_urllib().
    
    from savvy_requests import savvy_request_get
    response = savvy_request_get(url="https://httpbin.org/json")

    from savvy_requests import savvy_request_get
    from savvy_stealth import get_organic_req_header
    headers = get_organic_req_header(referer="https://mechatronicsolutionsllc.com/")
    # Optionally add something to headers
    #headers.update({"Authorization": f"Bearer {'abcdefghijkl'}","Content-Type": "application/json"})
    response = savvy_request_get(url="https://httpbin.org/json", headers=headers)

    from savvy_requests import savvy_request_get
    from savvy_stealth import get_captcha_free_header
    headers = get_captcha_free_header()
    # Optionally add something to headers
    #headers.update({"Authorization": f"Bearer {'abcdefghijkl'}","Content-Type": "application/json"})
    response = savvy_request_get(url="https://httpbin.org/json", headers=headers)

    """
    import requests
    from requests.exceptions import HTTPError    
    import time
    from http import HTTPStatus

    if url is None: raise Exception("Argument 'url' not passed to function")
    #if headers is None: raise Exception("Argument 'headers' not passed to function")

    """
    # Problem: requests.exceptions.HTTPError: 403 Client Error: Forbidden for url: https://lmarena.ai/?leaderboard=
    # https://tariyekorogha.medium.com/solution-to-403-client-error-forbidden-for-url-with-python-3-180effbdb21
    from urllib.request import Request, urlopen
    response = Request(url=url, headers={'User-Agent': 'Mozilla/5.0'})
    return response
    """


    retry_codes = [
        HTTPStatus.TOO_MANY_REQUESTS,       # 429
        HTTPStatus.INTERNAL_SERVER_ERROR,   # 500
        HTTPStatus.BAD_GATEWAY,             # 502
        HTTPStatus.SERVICE_UNAVAILABLE,     # 503
        HTTPStatus.GATEWAY_TIMEOUT,         # 504
    ]

    # HTTP GET with up to retries
    response = None
    for n in range(retries):
        try:
            response = requests.get(url=url, headers=headers)
            response.raise_for_status()
            break

        except HTTPError as e:
            code = e.response.status_code
            if code in retry_codes:
                if verbose: print(f"Retry {n+1} of {retries+1} error #{code}  {response.reason}  waiting {n*3}s..")
                # retry after n seconds
                time.sleep(n*3)
                continue
            elif code == 403:   # HTTP Error 403: Forbidden
                print("HTTP Error 403: Forbidden.  Try using savvy_request_get_urllib()")
                return None
            else:
                print(f"{e}")
                return None

    # Check if retries exceeded.
    if n == retries-1: 
        print(f"Request failed after {n+1} retries")
        return None

    # Process the response
    #print(f"response.json: \n{response.json()}")        # content as JSON
    #print(f"response.content: \n{response.content}")    # content as bytes
    #print(f"response.text: \n{response.text}")          # content in unicode

    return response


# ---------------------------------------------------------------------------
# NCEI Search Service API
import requests
def get_noaa_ncei_datatypes_by_dataset(dataset:str=None, verbose:bool=False):
    """
    Return a list of datatypes for 'dataset' from the lates NCEI Search Service API.

    Partial list of data types for global-hourly: 
    AJ1:  snow depth
    AK1:  snow accumulation
    OC1:  wind gust observation
    WND:  wind observation    
    RH1:  relative humidity
    SLP:  sea level pressure
    TMP:  dry bulb temperature

    Partial list of data types for daily & monthly:
    TMIN: Minimum temperature
    TMAX: Maximum temperature
    RHMN: Minimum relative humidity for the day
    RHMX: Maximum relative humidity for the day
    PRCP: Precipitation
    WSF2: wind speed
    WDF2: wind direction
    WSF5: wind gust
    WDF5: wind gust direction
    SNOW: Snowfall (mm)
    SNWD: Snow depth (mm)

    """

    datasets = ["daily-summaries", "global-hourly", "global-summary-of-the-month"]
    if not dataset in datasets: raise Exception(f"dataset {dataset} is not a member of {datasets}")

    url = "https://www.ncei.noaa.gov/access/services/search/v1/data"
    url += f"?dataset={dataset}"
    print(url)

    # Get your NOAA NCEI API key/token at: https://www.ncdc.noaa.gov/cdo-web/token
    headers={'token': os.getenv('API_NOAA_NCEI')}
    
    datatypes = []
    data_types_to_ignore = ["REM", "REPORT_TYPE", "SOURCE", "QUALITY_CONTROL", "CALL_SIGN"]

    try:
        req =  requests.get(url, data=None, json=None, headers=None)
        #req = savvy_request_get(url=url, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), ' fn()', url)
        print(f"get_noaa_ncei_stations_by_search() experienced a HTTP GET error while executing the request for url {url}")
        print(f"ERROR: {repr(e)}")
        return datatypes
    
    if req is None:
        print(f"get_noaa_ncei_stations_by_search() experienced a HTTP GET error while executing the request for url {url}")
        return datatypes

    resp = req.json()
    if len(resp) == 0:
        print("No results from query ", url)
        return datatypes
    else:
        # 

        #print(json.dumps(resp, sort_keys=False, indent=2))

        # Build a list of datatypes from dataTypes/buckets
        if not 'dataTypes' in resp.keys(): raise Exception("key 'dataType' not in response (root)")
        data_types = resp['dataTypes']
        if not 'buckets' in data_types.keys(): raise Exception("key 'buckets' not found in dataTypes/")
        buckets = data_types['buckets']
        for bucket in buckets:
            if not 'key' in bucket.keys(): raise Exception("key 'key' not found in dataTypes/buckets")
            if bucket['key'] not in data_types_to_ignore: 
                datatypes.append({"id": bucket['key'], "description": None})
        #print(f"{len(datatypes)} datatypes found")

        # Update 'datatypes' key 'description' with the description obtained from results/dataTypes
        if not 'results' in resp.keys(): raise Exception("ERROR: key 'results' not in response")
        results = resp['results']
        for result in results:
            if not 'dataTypes' in result.keys(): raise Exception("key 'dataTypes' not in results/")
            data_types = result['dataTypes']
            for data_type in data_types:
                if not 'name' in data_type.keys(): raise Exception(f"key 'name' not in results/dataTypes.  {data_type}")
                if not 'id' in data_type.keys(): raise Exception(f"key 'id' not in results/dataTypes.  {data_type}")
                for item in datatypes:
                    if item.get("id") == data_type['id']:
                        item['description'] = data_type['name']
                        #item.update({"description": data_type['name']})
                        break
    # Count the number of 'descriptions' that are None
    desc_is_none = 0
    for item in datatypes:
        if item['description'] is None: desc_is_none += 1

    print(f"{desc_is_none} of {len(datatypes)} descriptions were NOT found for the datatypes")
    print(f"\nData Types for {dataset}:")
    for item in datatypes:
        if item['description'] is None:
            print(f"{item['id']}: ")
        else:
            print(f"{item['id']}: {item['description']}")

    """
    Data Types for global-hourly:
    AA1: Liquid-Precipitation (Hourly)
    AA2: Liquid-Precipitation (Hourly) #2
    AA3: Liquid-Precipitation (Hourly) #3
    AA4: Liquid-Precipitation (Hourly) #4
    AB1: Liquid-Precipitation Monthly Total
    AC1:
    AD1: Liquid-Precipitation Greatest Amount In 24 Hours, For The Month
    AE1: Liquid-Precipitation, Number Of Days With Specific Amounts, For The Month
    AG1:
    AH1: Liquid-Precipitation Maximum Short Duration, For The Month
    AH2: Liquid-Precipitation Maximum Short Duration, For The Month #2
    AH3: Liquid-Precipitation Maximum Short Duration, For The Month #3
    AH4: Liquid-Precipitation Maximum Short Duration, For The Month #4
    AH5: Liquid-Precipitation Maximum Short Duration, For The Month #5
    AH6: Liquid-Precipitation Maximum Short Duration, For The Month #6
    AI1: Liquid-Precipitation Maximum Short Duration, For The Month (Continued)
    AI2: Liquid-Precipitation Maximum Short Duration, For The Month (Continued) #2
    AI3: Liquid-Precipitation Maximum Short Duration, For The Month (Continued) #3
    AI4: Liquid-Precipitation Maximum Short Duration, For The Month (Continued) #4
    AI5: Liquid-Precipitation Maximum Short Duration, For The Month (Continued) #5
    AI6: Liquid-Precipitation Maximum Short Duration, For The Month (Continued) #6
    AJ1: Snow-Depth
    AK1: Snow-Depth Greatest Depth On The Ground, For The Month
    AL1: Snow-Accumulation
    AL2: Snow-Accumulation #2
    AL3:
    AM1: Snow-Accumulation Greatest Amount In 24 Hours, For The Month
    AN1: Snow-Accumulation For The Month
    AO1:
    AT1: Daily Present Weather Observation #1
    AT2: Daily Present Weather Observation #2
    AT3: Daily Present Weather Observation #3
    AT4: Daily Present Weather Observation #4
    AT5: Daily Present Weather Observation #5
    AT6: Daily Present Weather Observation #6
    AT7: Daily Present Weather Observation #7
    AT8: Daily Present Weather Observation #8
    AU1: Present Weather Observation Automated Occurrence (Asos/Awos Only) #1
    AU2: Present Weather Observation Automated Occurrence (Asos/Awos Only) #2
    AU3: Present Weather Observation Automated Occurrence (Asos/Awos Only) #3
    AU4: Present Weather Observation Automated Occurrence (Asos/Awos Only) #4
    AU5: Present Weather Observation Automated Occurrence (Asos/Awos Only) #5
    AU6:
    AW1: Present-Weather-Observation Automated
    AW2: Present-Weather-Observation Automated #2
    AW3: Present-Weather-Observation Automated #3
    AW4: Present-Weather-Observation Automated #4
    AW5: Present-Weather-Observation Automated #5
    AW6: Present-Weather-Observation Automated #6
    AW7:
    AX1: Past-Weather-Observation Summary Of Day
    AX2: Past-Weather-Observation Summary Of Day #2
    AX3: Past-Weather-Observation Summary Of Day #3
    AX4: Past-Weather-Observation Summary Of Day #4
    AX5: Past-Weather-Observation Summary Of Day #5
    AX6: Past-Weather-Observation Summary Of Day #6
    AY1:
    AY2:
    AZ1:
    AZ2:
    CB1:
    CF1:
    CF2:
    CF3:
    CG1:
    CG2:
    CG3:
    CH1:
    CI1:
    CIG: Sky-Condition-Observation
    CN1:
    CN2:
    CN3:
    CN4:
    CO1:
    CR1:
    CT1:
    CT2:
    CT3:
    CU1:
    CU2:
    CU3:
    CV1:
    CV2:
    CV3:
    CW1:
    CX1:
    CX2:
    CX3:
    DEW: Dew Point Temperature
    ED1: Runway-Visual-Range-Observation
    EQD: Eqd
    GA1: Sky-Cover-Layer
    GA2: Sky-Cover-Layer #2
    GA3: Sky-Cover-Layer #3
    GA4: Sky-Cover-Layer #4
    GA5: Sky-Cover-Layer #5
    GA6: Sky-Cover-Layer #6
    GD1: Sky-Cover-Summation-State
    GD2: Sky-Cover-Summation-State #2
    GD3: Sky-Cover-Summation-State #3
    GD4: Sky-Cover-Summation-State #4
    GD5:
    GD6:
    GE1: Sky-Condition-Observation Identifier
    GF1: Sky-Condition-Observation #2
    GG1:
    GG2:
    GG3:
    GG4:
    GG5:
    GH1:
    GJ1: Sunshine-Observation (For the Reporting Period)
    GK1: Sunshine-Observation (For Previous 24 Hour Period)
    GL1:
    GM1:
    GN1:
    GO1:
    GP1:
    GQ1:
    GR1:
    HL1:
    IA1:
    IA2:
    IB1:
    IB2:
    IC1:
    KA1: Extreme-Air-Temperature
    KA2: Extreme-Air-Temperature #2
    KA3: Extreme-Air-Temperature #3
    KA4: Extreme-Air-Temperature #4
    KB1: Average-Air-Temperature
    KB2: Average-Air-Temperature #2
    KB3: Average-Air-Temperature #3
    KC1: Extreme Air-Temperature For The Month
    KC2: Extreme Air-Temperature For The Month #2
    KD1: Heating-Cooling-Degree-Days
    KD2: Heating-Cooling-Degree-Days #2
    KE1: Extreme Temperatures, Number Of Days Exceeding Criteria, For The Month
    KF1:
    KG1: Average-Dew-Point-And-Wet-Bulb-Temperature
    KG2: Average-Dew-Point-And-Wet-Bulb-Temperature #2
    MA1: Atmospheric-Pressure-Observation (Alt/Stp)
    MD1: Atmospheric-Pressure-Change
    ME1:
    MF1: Atmospheric-Pressure-Observation (Stp/Slp)
    MG1: Atmospheric-Pressure-Observation (Stp/Slp) #2
    MH1: Atmospheric-Pressure-Observation For The Month
    MK1: Atmospheric-Pressure-Observation For The Month (Continued)
    MV1: Present-Weather-In-Vicinity-Observation
    MV2:
    MW1: Present-Weather-Observation Manual
    MW2: Present-Weather-Observation Manual #2
    MW3: Present-Weather-Observation Manual #3
    MW4:
    MW5:
    MW6:
    MW7:
    OA1:
    OA2:
    OA3:
    OB1:
    OC1: Wind-Gust-Observation
    OD1: Supplementary-Wind-Observation Identifier
    OD2:
    OD3:
    OE1: Summary-Of-Day-Wind-Observation
    OE2: Summary-Of-Day-Wind-Observation #2
    OE3: Summary-Of-Day-Wind-Observation #3
    RH1: Relative-Humidity
    RH2: Relative-Humidity #2
    RH3: Relative-Humidity #3
    SA1:
    SLP: Sea Level Pressure
    TMP: Dry Bulb Temperature
    UA1:
    UG1:
    UG2:
    VIS: Visibility-Observation
    WA1: Platform-Ice-Accretion
    WD1:
    WG1:
    WND: Wind-Observation


    Data Types for daily-summaries:
    ACMC:
    ACMH: Average cloudiness midnight to midnight from manual observations
    ACSC:
    ACSH: Average cloudiness sunrise to sunset from manual observations
    ADPT: Average Dew Point Temperature for the day
    ASLP: Average Sea Level Pressure for the day
    ASTP: Average Station Level Pressure for the day
    AWBT: Average Wet Bulb Temperature for the day
    AWDR:
    AWND: Average daily wind speed
    DAEV: Number of days included in the multiday evaporation total (MDEV)
    DAPR: Number of days included in the multiday precipitation total (MDPR)
    DASF: Number of days included in the multiday snow fall total (MDSF)
    DATN:
    DATX:
    DAWM: Number of days included in the multiday wind movement (MDWM)
    DWPR:
    EVAP: Evaporation of water from evaporation pan
    FMTM: Time of fastest mile or fastest 1-minute wind
    FRGB: Base of frozen ground layer
    FRGT: Top of frozen ground layer
    FRTH: Thickness of frozen ground layer
    GAHT: Difference between river and gauge height
    MDEV: Multiday evaporation total (use with DAEV)
    MDPR: Multiday precipitation total (use with DAPR and DWPR, if available)
    MDSF: Multiday snowfall total
    MDTN:
    MDTX:
    MDWM: Multiday wind movement
    MNPN: Daily minimum temperature of water in an evaporation pan (tenths of degrees C)
    MXPN: Daily maximum temperature of water in an evaporation pan (tenths of degrees C)
    PGTM: Peak gust time (hours and minutes, i.e., HHMM)
    PRCP: Precipitation
    PSUN: Daily percent of possible sunshine
    RHAV: Average relative humidity for the day
    RHMN: Minimum relative humidity for the day
    RHMX: Maximum relative humidity for the day
    SN01:
    SN02: Minimum soil temperature with unknown cover at 10 cm depth
    SN03: Minimum soil temperature with unknown cover at 20 cm depth
    SN11:
    SN12: Minimum soil temperature with grass cover at 10 cm depth
    SN13:
    SN14:
    SN21:
    SN22:
    SN23:
    SN31:
    SN32: Minimum soil temperature with bare ground cover at 10 cm depth
    SN33:
    SN34:
    SN35:
    SN36:
    SN51: Minimum soil temperature with sod cover at 5 cm depth
    SN52: Minimum soil temperature with sod cover at 10 cm depth
    SN53: Minimum soil temperature with sod cover at 20 cm depth
    SN54:
    SN55:
    SN56:
    SN57:
    SN61:
    SN72:
    SN81:
    SN82:
    SN83:
    SNOW: Snowfall (mm)
    SNWD: Snow depth (mm)
    SX01:
    SX02: Maximum soil temperature with unknown cover at 10 cm depth
    SX03: Maximum soil temperature with unknown cover at 20 cm depth
    SX11:
    SX12: Maximum soil temperature with grass cover at 10 cm depth
    SX13:
    SX14: 
    SX15:
    SX17:
    SX21:
    SX22:
    SX23:
    SX31:
    SX32: Maximum soil temperature with bare ground cover at 10 cm depth
    SX33:
    SX34:
    SX35:
    SX36:
    SX51:
    SX52: Maximum soil temperature with sod cover at 10 cm depth
    SX53: Maximum soil temperature with sod cover at 20 cm depth
    SX54:
    SX55:
    SX56:
    SX57:
    SX61:
    SX72:
    SX81:
    SX82:
    SX83:
    TAVG: Average temperature
    THIC: Thickness of ice on water
    TMAX: Maximum temperature (tenths of degrees C)
    TMIN: Minimum temperature (tenths of degrees C)
    TOBS: Temperature at the time of observation (tenths of degrees C)
    TSUN: Daily total sunshine (minutes)
    WDF1: Direction of fastest 1-minute wind (degrees)
    WDF2: Direction of fastest 2-minute wind (degrees)
    WDF5: Direction of fastest 5-second wind (degrees)
    WDFG: Direction of peak wind gust (degrees)
    WDFI: Direction of highest instantaneous wind (degrees)
    WDFM: Fastest mile wind direction (degrees)
    WDMV: 24-hour wind movement
    WESD: Water equivalent of snow on the ground
    WESF:
    WSF1: Fastest 1-minute wind speed
    WSF2: Fastest 2-minute wind speed
    WSF5: Fastest 5-second wind speed
    WSFG: Peak guest wind speed
    WSFI: Highest instantaneous wind speed
    WSFM: Fastest mile wind speed
    WT01: Fog, ice fog, or freezing fog (may include heavy fog)
    WT02: Heavy fog or heaving freezing fog (not always distinguished from fog)
    WT03: Thunder
    WT04: Ice pellets, sleet, snow pellets, or small hail
    WT05: Hail (may include small hail)
    WT06: Glaze or rime
    WT07: Dust, volcanic ash, blowing dust, blowing sand, or blowing obstruction
    WT08: Smoke or haze
    WT09: Blowing or drifting snow
    WT10: Tornado, waterspout, or funnel cloud
    WT11: High or damaging winds
    WT12: Blowing spray
    WT13: Mist
    WT14: Drizzle
    WT15: Freezing drizzle
    WT16: Rain (may include freezing rain, drizzle, and freezing drizzle)
    WT17: Freezing rain
    WT18: Snow, snow pellets, snow grains, or ice crystals
    WT19: Unknown source of precipitation
    WT21: Ground fog
    WT22: Ice fog or freezing fog
    WV01: Fog, ice fog, or freezing fog (may include heavy fog)
    WV03: Thunder
    WV07: Ash, dust, sand, or other blowing obstruction
    WV18:
    WV20: Rain or snow shower


    Data Types for global-summary-of-the-month:
    ADPT: Monthly Average Dew Point Temperature
    ASLP: Monthly Average Sea Level Pressure
    ASTP: Monthly Average Station Level Pressure
    AWBT: Monthly Average Wet Bulb Temperature
    AWND: Average Wind Speed for the month
    CDSD: Cooling Degree Days Season to Date
    CLDD: Cooling Degree Days
    DP01: Number days with greater than 0.01 inch (0.25mm) of precipitation
    DP10: Number days with greater than 0.10 inch (2.54mm) of precipitation
    DP1X: Number days with greater than 1.00 inch (25.4mm) of precipitation
    DSND: Number days with greater than 1.0 inch (25.4mm) of snow depth
    DSNW: Number of days with greater than or equal to 1.0 inch (25.4mm) of snowfall
    DT00: Number days with minimum temperature less than 0F (-17.6C)
    DT32: Number days with minimum temperature less than 32F (0C)
    DX32: Number days with maximum temperature less than 32F (0C)
    DX70: Number days with maximum temperature greater than 70F (21.1C)
    DX90: Number days with maximum temperature greater than 90F (32.2C)
    DYFG: Number days with fog
    DYHF: Number days with heavy fog
    DYNT: Day of month of extreme minimum temperature
    DYSD: Day of month of highest daily snow depth
    DYSN: Day of month of highest daily snowfall
    DYTS: Number days with thunderstorms
    DYXP: Day of month of highest daily total of precipitation
    DYXT: Day of month with extreme maximum temperature
    EMNT: Extreme minimum temperature
    EMSD: Extreme maximum snow depth
    EMSN: Extreme maximum snowfall
    EMXP: Extreme maximum precipitation
    EMXT: Extreme maximum temperature
    EVAP: Total Evaporation
    HDSD: Heating Degree Days Season to TIME
    HN01: Highest minimum soil temperature - 01
    HN02: Highest minimum soil temperature - 02
    HN03: Highest minimum soil temperature - 03
    HN04: Highest minimum soil temperature - 04
    HN05: Highest minimum soil temperature - 05
    HN06: Highest minimum soil temperature - 06
    HN07: Highest minimum soil temperature - 07
    HN08: Highest minimum soil temperature - 08
    HN09: Highest minimum soil temperature - 09
    HTDD: Heating Degree Days
    HX01: Highest maximum soil temperature - 01
    HX02: Highest maximum soil temperature - 02
    HX03: Highest maximum soil temperature - 03
    HX04: Highest maximum soil temperature - 04
    HX05: Highest maximum soil temperature - 05
    HX06: Highest maximum soil temperature - 06
    HX07: Highest maximum soil temperature - 07
    HX08: Highest maximum soil temperature - 08
    HX09: Highest maximum soil temperature - 09
    LN01: Lowest minimum soil temperature - 01
    LN02: Lowest minimum soil temperature - 02
    LN03: Lowest minimum soil temperature - 03
    LN04: Lowest minimum soil temperature - 04
    LN05: Lowest minimum soil temperature - 05
    LN06: Lowest minimum soil temperature - 06
    LN07: Lowest minimum soil temperature - 07
    LN08: Lowest minimum soil temperature - 08
    LN09: Lowest minimum soil temperature - 09
    LX01: Lowest maximum soil temperature - 01
    LX02: Lowest maximum soil temperature - 02
    LX03: Lowest maximum soil temperature - 03
    LX04: Lowest maximum soil temperature - 04
    LX05: Lowest maximum soil temperature - 05
    LX06: Lowest maximum soil temperature - 06
    LX07: Lowest maximum soil temperature - 07
    LX08: Lowest maximum soil temperature - 08
    LX09: Lowest maximum soil temperature - 09
    MN01: Monthly mean minimum soil temperature - 01
    MN02: Monthly mean minimum soil temperature - 02
    MN03: Monthly mean minimum soil temperature - 03
    MN04: Monthly mean minimum soil temperature - 04
    MN05: Monthly mean minimum soil temperature - 05
    MN06: Monthly mean minimum soil temperature - 06
    MN07: Monthly mean minimum soil temperature - 07
    MN08: Monthly mean minimum soil temperature - 08
    MN09: Monthly mean minimum soil temperature - 09
    MNPN: Monthly mean minimum evaporation pan water temperature
    MX01: Monthly mean maximum soil temperature - 01
    MX02: Monthly mean maximum soil temperature - 02
    MX03: Monthly mean maximum soil temperature - 03
    MX04: Monthly mean maximum soil temperature - 04
    MX05: Monthly mean maximum soil temperature - 05
    MX06: Monthly mean maximum soil temperature - 06
    MX07: Monthly mean maximum soil temperature - 07
    MX08: Monthly mean maximum soil temperature - 08
    MX09: Monthly mean maximum soil temperature - 09
    MXPN: Monthly mean maximum evaporation pan water temperature
    PRCP: Precipitation
    PSUN: Percent of possible sunshine
    RHAV: Monthly Average Relative Humidity
    RHMN: Monthly Average of Minimum Relative Humidity
    RHMX: Monthly Average of Maximum Relative Humidity
    SNOW: Total Monthly Snowfall
    TAVG: Average Average Temperature
    TMAX: Average Maximum Temperature
    TMIN: Average Minimum Temperature
    TSUN: Total sunshine
    WDF1: Direction of Maximum 1 Minute Wind Speed
    WDF2: Direction of Maximum 2 Minute Wind Speed
    WDF5: Direction of Maximum 5 Second Wind Speed
    WDFG: Direction of Peak Gust Wind Speed
    WDFM:
    WDMV: Total wind movement over evaporation pan
    WSF1: Maximum 1 Minute Wind Speed
    WSF2: Maximum 2 Minute Wind Speed
    WSF5: Maximum 5 Second Wind Speed
    WSFG: Peak Gust Wind Speed
    WSFM:

    """

    return datatypes



def get_noaa_ncei_stations_by_search(dataset:str=None, lat:float=None, lon:float=None, datatypes:list=None, start_date:str=None, end_date:str=None, verbose:bool=False):
    """
    Using the latest NOAA NCEI API endpoint (as of 2023)

    Uses the NOAA NCEI Search Service API to return a list of (weather) stations along with their GPS coordinates and start/end dates,
    and the computed distance and elevation delta from the target location specified by lat,lon that meet the requirements of:
        dataset: ONE of the following "daily-summaries", "global-hourly", "global-summary-of-the-month"
        lat/lon:  latitude & longitude of the location of interest. 
        datatypes: Ex TMIN, TMAX, PRCP
        start_date: Ex 2010-02-01
        end_date: Ex 2010-02-01

    The search for stations will terminate when:
    - A latitude difference of less than 3.8 degrees or 265 mi and an elevation difference of less than 282 m between the weather location and the target location is achieved.
    - If 30 stations with the data of interest are acquired.
    - No stations are found within a bounding box that has more than 500 miles between it's opposite NW & SE corners.

    A GPS bounding box is generated from the provided target location specified by 'lat' and lon'.  
    It begins with a small latitude/longitude offset inititally, but then it is programmatically increased with each iteration 
    until the search termination criteria is met. 

    The product of the distance between the target and the station and the same for elevation is calculated and used as the sorting criteria for the results. 

    Usage:

    dataset = "daily-summaries"

    # Position of interest specified in decimal degrees.
    latitude = 40.44077
    longitude = -76.12267

    # See datatypes available in Table 4 of: https://www.ncei.noaa.gov/pub/data/cdo/documentation/GHCND_documentation.pdf
    datatypes = ["TMIN","TMAX","PRCP"]

    # For "daily_summaries" the start_date and end-date should be the same day in the past.
    start_date = "2010-02-01"
    end_date = "2010-02-01"

    stations = get_noaa_ncei_stations_by_search(dataset, latitude, longitude, datatypes, start_date, end_date, verbose=True)
    if stations is None:
        print("NO results")
    else:
        print(f"\nThe best station choice is {stations[0][3]} with delta elevation of {round(stations[0][1]*3.281,3)} ft and delta distance of {round(stations[0][2]/1609,3)} mi from the target of {latitude},{longitude} and with data from {stations[0][6]} to {stations[0][7]}\n")
        # All data in stations:
        print("sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd")
        for station in stations:
            print(station)
    
    Output:

    8.685 mi between the bounding box corners of 40.49077,-76.17267 & 40.39077,-76.07267 for lat_lon_deg_offset: 0.05 deg
    https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=daily-summaries&bbox=40.49077,-76.17267,40.39077,-76.07267&dataTypes=TMIN,TMAX,PRCP&startDate=2010-02-01&endDate=2010-02-01&limit=30&offset=0

    95.529 mi between the bounding box corners of 40.99077,-76.67267 & 39.89077,-75.57267 for lat_lon_deg_offset: 0.55 deg
    https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=daily-summaries&bbox=40.99077,-76.67267,39.89077,-75.57267&dataTypes=TMIN,TMAX,PRCP&startDate=2010-02-01&endDate=2010-02-01&limit=30&offset=0

    The best station choice is USC00360785 with delta elevation of 10.171 ft and delta distance of 6.525 mi from the target of 40.44077,-76.12267 and with data from 1978-05-01T00:00:00 to 2025-05-29T23:59:59

    sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd
    [32296.8, 3.1, 10499.3, 'USC00360785', 40.38028, -76.02745, '1978-05-01T00:00:00', '2025-05-29T23:59:59']
    [55580.3, 3.5, 15734.2, 'USW00014712', 40.37342, -75.95924, '1949-01-01T00:00:00', '2025-05-28T23:59:59']
    [59464.1, 3.6, 16602.1, 'USC00363632', 40.55156, -75.99105, '1894-01-01T00:00:00', '2021-11-21T23:59:59']
    [202794.8, 4.6, 44093.1, 'USC00364778', 40.11903, -76.4265, '1952-04-01T00:00:00', '2025-05-27T23:59:59']
    [554403.8, 8.3, 66678.7, 'USC00369464', 39.9708, -75.635, '1893-01-01T00:00:00', '2017-05-31T23:59:59']
    [643188.4, 16.7, 38467.3, 'USW00054737', 40.12061, -76.29446, '1999-03-16T00:00:00', '2025-05-28T23:59:59']
    [722104.5, 15.9, 45325.6, 'USC00364763', 40.0499, -76.2742, '1948-05-01T00:00:00', '2025-05-29T23:59:59']
    [826918.5, 26.7, 30922.9, 'USC00364896', 40.33729, -76.46157, '1948-05-01T00:00:00', '2025-05-28T23:59:59']
    [2290037.5, 63.6, 36031.9, 'USC00367578', 40.5515, -75.7222, '1983-12-01T00:00:00', '2013-03-31T23:59:59']
    [2796948.8, 45.4, 61618.2, 'USC00367732', 39.92534, -76.38903, '1948-05-01T00:00:00', '2025-05-29T23:59:59']
    [3315809.6, 81.1, 40872.2, 'USC00366238', 40.07528, -76.07147, '1992-08-01T00:00:00', '2025-05-28T23:59:59']
    [7362366.8, 118.9, 61902.7, 'USC00360560', 40.862, -75.64291, '1971-09-01T00:00:00', '2025-05-29T23:59:59']
    [10910582.9, 206.5, 52830.9, 'USC00360457', 40.82086, -76.49831, '1944-07-01T00:00:00', '2025-05-27T23:59:59']
    [16211835.7, 370.1, 43800.2, 'USC00365344', 40.83435, -76.14374, '1972-02-01T00:00:00', '2025-05-29T23:59:59']
    
    """

    import operator
    from datetime import datetime

    def validate_date_str_format(date_string):
        """
        Validates if a date string is in "YYYY-MM-DD" format and represents a valid date.

        Args:
            date_string (str): The date string to validate.

        Returns:
            bool: True if the date string is valid, False otherwise.
        """
        from datetime import datetime

        if not len(date_string) == 10: return False

        try:
            # Attempt to parse the string into a datetime object using the specified format.
            # This will raise a ValueError if the string does not match the format
            # or if it represents an invalid date (e.g., "2023-02-30").
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            # If a ValueError is raised, the string is not in the correct format
            # or is not a valid date.
            return False

    def conv_iso8601_str_to_dt(iso_8601_str):
        """
        Convert the ISO 8601 date/time string 'iso_8601_str' to a Python datetime object.
        """
        from datetime import datetime
        if not isinstance(iso_8601_str,str): raise Exception("Argument 'iso_8601_str' is not a string")
        try:
            # A space is a valid separator in some cases.  Below is how to check for when it is a space. 
            if not iso_8601_str.count("T") == 1 and len(iso_8601_str) > 10: raise Exception(f"Invalid ISO 8601 string {iso_8601_str} (T) missing")
            # Convert the ISO8601 datetime string to a Python datetime object.
            dt_iso8601 = datetime.fromisoformat(iso_8601_str)
            #print(f"Parsed '{iso_8601_str}': {dt_iso8601} timezone: {dt_iso8601.tzinfo}")
            return dt_iso8601
        except Exception as e:
                raise Exception(e)


    datasets = ["daily-summaries", "global-hourly", "global-summary-of-the-month"]
    if not dataset in datasets: raise Exception(f"dataset {dataset} is not a member of {datasets}")

    if not lat_lon_is_valid(lat, lon): raise Exception("Arguments lat/lon are invalid")
    if datatypes is None or len(datatypes) == 0: raise Exception("Argument 'datatypes' is invalid")
    if not validate_date_str_format(start_date): raise Exception("Argument 'start_date' is invalid")
    if not validate_date_str_format(end_date): raise Exception("Argument 'end_date' is invalid")
    if not datetime.strptime(start_date, "%Y-%m-%d") <= datetime.strptime(end_date, "%Y-%m-%d"): raise Exception("Argument 'start_date' must be <= 'end_date")

    datatypes_str = ",".join(datatypes)

    lat_lon_deg_offset = 0.05
    iteration_count = 0

    # Loop and increment lat_lon_deg_offset until a sufficient number of stations are acquired. 
    while True:

        station_data = []

        # Derive a GPS bounding box from the latitude/longitude that is offset by 0.8 degrees latitude and 0.8 degrees longitude.
        # 0.5 degree offset yields ~ 87 mi from the NW corner to the SE corner.  1.0 deg yields ~ 174 mi.
        nw_lat, nw_lon, se_lat, se_lon = get_gps_bounding_box(lat, lon, lat_lon_deg_offset, lat_lon_deg_offset, False)
        nw_lat = round(nw_lat,5)
        nw_lon = round(nw_lon,5)
        se_lat = round(se_lat,5)
        se_lon = round(se_lon,5)
        dist_m = haversine_distance(nw_lat, nw_lon, se_lat, se_lon)        
        print(f"\n{round(dist_m/1609,3)} mi between the bounding box corners of {nw_lat},{nw_lon} & {se_lat},{se_lon} for lat_lon_deg_offset: {lat_lon_deg_offset} deg")

        # global-summary-of-the-year, global-summary-of-the-month, daily-summaries
        # TMP

        # WORKS:
        # dataset: global-hourly, global-summary-of-the-month
        # dataTypes: TMIN,TMAX, PRCP
        # &bbox=40.94077,-76.62267,39.94077,-75.62267
        # https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=global-hourly&startDate=2016-01-01T00:00:00&endDate=2017-12-31T23:59:59&dataTypes=TMP&limit=10&offset=0
        # https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=global-hourly&startDate=2024-01-01&endDate=2024-12-31&dataTypes=TMP&limit=10&offset=0
        # https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=daily-summaries&bbox=40.94077,-76.62267,39.94077,-75.62267&startDate=2024-01-01&endDate=2024-01-01&limit=10&offset=0&dataTypes=TMIN,TMAX



        # https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=global-hourly&startDate=2016-01-01&endDate=2017-12-31&dataTypes=TMP&limit=10&offset=0


        # Example from the documentation that does not work:
        # https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=daily-summaries&startDate=2010-01-01T00:00:00&endDate=2016-12-31T23:09:59&boundingBox=35.462327,-82.563951,35.412327,-82.513951&dataTypes=PRCP&stations=USW00003812&limit=10&offset=0

        

        # https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=global-hourly&boundingBox=41.44077,-77.12267,39.44077,-75.12267&dataTypes=TMIN,TMAX,PRCP&limit=30&offset=0&startDate=2016-01-01T00:00:00&endDate=2017-12-31T23:59:59
        # https://www.ncei.noaa.gov/access/services/search/v1/data?dataset=global-hourly&boundingBox=35.462327,-82.563951,35.412327,-82.513951&dataTypes=TMPP&limit=30&offset=0&startDate=2016-01-01T00:00:00&endDate=2017-12-31T23:59:59
        #CREATES QUERY STRING TO BE PLACED IN REQUES/API/ENDPOINT URL
        url = "https://www.ncei.noaa.gov/access/services/search/v1/data"
        url += f"?dataset={dataset}"
        url += "&bbox=" + str(round(nw_lat,5)) + "," + str(round(nw_lon,5)) + "," + str(round(se_lat,5)) + "," + str(round(se_lon,5))
        url += f"&dataTypes={datatypes_str}"
        url += f"&startDate={start_date}"
        url += f"&endDate={end_date}"
        url += "&limit=30&offset=0"
        if verbose: print(url)

        # Get your NOAA NCEI API key/token at: https://www.ncdc.noaa.gov/cdo-web/token
        headers={'token': os.getenv('API_NOAA_NCEI')}
        
        try:
            req = requests.get(url, data=None, json=None, headers=headers)
            #req = savvy_request_get(url=url, headers=headers)
        except Exception as e:
            print('ERROR: ' + repr(e), ' fn()', url)
            print(f"get_noaa_ncei_stations_by_search() experienced a HTTP GET error while executing the request for url {url}")
            print(f"ERROR: {repr(e)}")
            return None
        
        if req is None:
            print(f"get_noaa_ncei_stations_by_search() experienced a HTTP GET error while executing the request for url {url}")
            return None

        # if no results for the bounding box, increment the lat/long offset
        if iteration_count > 1:
            lat_lon_deg_offset += 1.0
        else:
            lat_lon_deg_offset += 0.25

        resp = req.json()
        if len(resp) == 0:
            print("No results from query ", url)
        else:
            # Stations meeting the dataset, datatypes, start_date, and end_date requirements found.

            #print(json.dumps(resp, sort_keys=False, indent=2))
            station_data = []
            min_delta_distance_m = None
            min_delta_elevation_m = None
            #if 'data' in resp.keys():
            if not 'results' in resp.keys(): raise Exception("ERROR: key 'results' not in response")
            station_ids = []
            results = resp['results']
            for result in results:
                if not 'endDate' in result.keys(): raise Exception("ERROR: key 'endDate' not in response (result)")
                if not 'startDate' in result.keys(): raise Exception("ERROR: key 'startDate' not in response (result)")
                if not 'centroid' in result.keys(): raise Exception("ERROR: key 'centroid' not in response (result)")
                if not 'point' in result['centroid'].keys(): raise Exception("ERROR: key 'point' not in response (result['centroid'])")
                centroid = result['centroid']
                longitude = float(centroid['point'][0])
                latitude = float(centroid['point'][1])
                if not 'name' in result.keys(): raise Exception("ERROR: key 'name' not in response (result)")
                if not 'location' in result.keys(): raise Exception("ERROR: key 'location' not in response (result)")
                if not 'id' in result.keys(): raise Exception("ERROR: key 'id' not in response (result)")
                if not 'dataTypesCount' in result.keys(): raise Exception("ERROR: key 'dataTypesCount' not in response (result)")       
                if not 'boundingPoints' in result.keys(): raise Exception("ERROR: key 'boundingPoints' not in response (result)")        
                if not 'stations' in result.keys(): raise Exception("ERROR: key 'stations' not in response (result)")
                stations = result['stations']
                # Check the contents of result['stations'] and build a list of the stations id's. 
                for station in stations:
                    if not 'name' in station.keys(): raise Exception("ERROR: key 'name' not in response (stations)")
                    if not 'id' in station.keys(): raise Exception("ERROR: key 'id' not in response (stations)")        # datatype id
                    if not "dataTypes" in station.keys(): raise Exception("ERROR: key 'dataTypes' not in response (stations)")
                    station_ids.append(station['id'])
                # Iterate over the stations and make sure all of the datatypes exist and the startDate and endDate includes start/end period. 
                for station in stations:
                    stn_datatypes = station['dataTypes']
                    stn_datatypes_count = 0
                    stn_start_end_dates_valid = True
                    for stn_datatype in stn_datatypes:
                        if not "id" in stn_datatype.keys(): raise Exception("ERROR: key 'id' was expected in results/stations/dataTypes")
                        if not "startDate" in stn_datatype.keys(): raise Exception("ERROR: key 'startDate' was expected in results/stations/datatypes")
                        if not "endDate" in stn_datatype.keys(): raise Exception("ERROR: key 'endDate' was expected in results/stations/datatypes")
                        if stn_datatype['id'] in datatypes: 
                            stn_datatypes_count += 1
                            #print(f"Converting {stn_datatype['startDate']} to {conv_iso8601_str_to_dt(stn_datatype['startDate'])}")
                            #print(f"Converting {stn_datatype['endDate']} to {conv_iso8601_str_to_dt(stn_datatype['endDate'])}")
                            stn_start_date = conv_iso8601_str_to_dt(stn_datatype['startDate'])
                            stn_end_date = conv_iso8601_str_to_dt(stn_datatype['endDate'])
                            # stn_start_date <= start_date <= end_date <= stn_end_date
                            if not stn_start_date <= datetime.strptime(start_date, '%Y-%m-%d'): 
                                #print(f"The station {station['id']} startDate: {stn_start_date} > start_date: {datetime.strptime(start_date, '%Y-%m-%d')} ?")
                                stn_start_end_dates_valid = False
                            if not stn_end_date >= datetime.strptime(end_date, '%Y-%m-%d'): 
                                #print(f"The station {station['id']} endDate: {stn_end_date} < end_date: {datetime.strptime(end_date, '%Y-%m-%d')} ?")
                                stn_start_end_dates_valid = False
                    if not stn_datatypes_count == len(datatypes):
                        pass
                        print(f"WARNING: All {len(datatypes)} datatypes of {datatypes_str} were NOT found in the station data for station: {station['id']}")
                    elif stn_start_end_dates_valid == False:
                        pass
                        #print(f"The station {station['id']} startDate: {stn_start_date} and/or endDate: {stn_end_date} doesn't support the start_date: {datetime.strptime(start_date, '%Y-%m-%d')} & end_date {datetime.strptime(end_date, '%Y-%m-%d')} requirements")
                    else:
                        #print(f"\n{len(datatypes)} datatypes of {datatypes_str} were found in the station data for station: {station['id']}")
                        #print(f"The station {station['id']} startDate: {stn_start_date} <= start_date: {datetime.strptime(start_date, '%Y-%m-%d')}")
                        #print(f"The station {station['id']} endDate: {stn_end_date} >= end_date: {datetime.strptime(end_date, '%Y-%m-%d')}")
                        delta_distance_m = haversine_distance(lat, lon, latitude, longitude)
                        delta_elevation_m = abs(elevation_by_lat_lon(lat, lon) - elevation_by_lat_lon(latitude, longitude))
                        if min_delta_distance_m is None or delta_distance_m < min_delta_distance_m:
                            min_delta_distance_m = delta_distance_m
                        if min_delta_elevation_m is None or delta_elevation_m < min_delta_distance_m:
                            min_delta_elevation_m = delta_elevation_m
                        sort = delta_distance_m * delta_elevation_m
                        #if verbose: print(station['id'], "\t", latitude, longitude, "\t", round(delta_distance_m,1), round(delta_elevation_m,1), result['startDate'], "\t", result['endDate'])
                        station_data.append([round(sort,1), round(delta_elevation_m,1), round(delta_distance_m,1), station['id'], latitude, longitude, result['startDate'], result['endDate']])
            
                if not len(station_data) == len(station_ids): print(f"Only {len(station_data)} stations out of {len(station_ids)} meet the date and data type requirements.")
    
            print(f"{len(station_data)} stations found that meet the date and data type requirements")

            # A latitude change of 3.8 degrees or 265 mi (426476 m) ~= 5 F change in temperature
            # An elevation change of 282 m ~= 5 F change in temperature
            if round(dist_m/1609,3) > 500:
                # Abort if no stations found within a bounding box that has a distance of over 500 miles between its corners. 
                print(f"ABORTING SEARCH:  No stations found within {round(dist_m/1609,3)} mi between the bounding box corners of {nw_lat},{nw_lon} & {se_lat},{se_lon} for lat_lon_deg_offset: {lat_lon_deg_offset} deg that meet the search criteria.")
                break
            elif min_delta_elevation_m is None or min_delta_distance_m is None:
                pass
            elif min_delta_elevation_m < 282 and min_delta_distance_m < 426476: 
                break
            elif len(station_data) > 30: 
                print(f"WARNING: {len(station_data)} stations found, but all fail the criteria of delta_elevation_m < 282 and delta_distance_m < 426476")
                break

        iteration_count += 1

    # Sort the data by delta_distance_m * delta_elevation
    station_data.sort(reverse=False, key=operator.itemgetter(0))
    return station_data


def parse_ncei_search_results(dataset:str=None, datatypes:list=None, limit:int=10000, verbose:bool=False):
    """
    Executes a NOAA NCEI Search Service API HTTP GET on 'url' and parses the returned data. 
    Best used as a tool for evaluation of the availability of datatypes. 
    The returned result will tell you the date range of the data for each station.  
    """

    from datetime import datetime

    def validate_date_str_format(date_string):
        """
        Validates if a date string is in "YYYY-MM-DD" format and represents a valid date.

        Args:
            date_string (str): The date string to validate.

        Returns:
            bool: True if the date string is valid, False otherwise.
        """
        from datetime import datetime

        if not len(date_string) == 10: return False

        try:
            # Attempt to parse the string into a datetime object using the specified format.
            # This will raise a ValueError if the string does not match the format
            # or if it represents an invalid date (e.g., "2023-02-30").
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            # If a ValueError is raised, the string is not in the correct format
            # or is not a valid date.
            return False

    def conv_iso8601_str_to_dt(iso_8601_str):
        """
        Convert the ISO 8601 date/time string 'iso_8601_str' to a Python datetime object.
        """
        from datetime import datetime
        if not isinstance(iso_8601_str,str): raise Exception("Argument 'iso_8601_str' is not a string")
        try:
            # A space is a valid separator in some cases.  Below is how to check for when it is a space. 
            if not iso_8601_str.count("T") == 1 and len(iso_8601_str) > 10: raise Exception(f"Invalid ISO 8601 string {iso_8601_str} (T) missing")
            # Convert the ISO8601 datetime string to a Python datetime object.
            dt_iso8601 = datetime.fromisoformat(iso_8601_str)
            #print(f"Parsed '{iso_8601_str}': {dt_iso8601} timezone: {dt_iso8601.tzinfo}")
            return dt_iso8601
        except Exception as e:
                raise Exception(e)


    datasets = ["daily-summaries", "global-hourly", "global-summary-of-the-month"]
    if not dataset in datasets: raise Exception(f"dataset {dataset} is not a member of {datasets}")

    if datatypes is None or len(datatypes) == 0: raise Exception("Argument 'datatypes' is invalid")

    datatypes_str = ",".join(datatypes)

    station_data = []

    url = "https://www.ncei.noaa.gov/access/services/search/v1/data"
    url += f"?dataset={dataset}"
    url += f"&dataTypes={datatypes_str}"
    url += f"&limit={limit}"    # The number of results seem to be limited to 10000 for dataset "daily-summaries".
    url += "&offset=0"       
    print(f"url: {url}")

    # Get your NOAA NCEI API key/token at: https://www.ncdc.noaa.gov/cdo-web/token
    headers={'token': os.getenv('API_NOAA_NCEI')}
    
    try:
        req = requests.get(url=url, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), ' fn()', url)
        print(f"get_noaa_ncei_stations_by_search() experienced a HTTP GET error while executing the request for url {url}")
        print(f"ERROR: {repr(e)}")
        return None
    
    if req is None:
        print(f"get_noaa_ncei_stations_by_search() experienced a HTTP GET error while executing the request for url {url}")
        return None

    resp = req.json()
    if len(resp) == 0:
        print("No results from query ", url)
    else:
        # Stations meeting the dataset, datatypes, start_date, and end_date requirements found.

        #print(json.dumps(resp, sort_keys=False, indent=2))
        station_data = []
        min_delta_distance_m = None
        min_delta_elevation_m = None
        if not 'results' in resp.keys(): raise Exception("ERROR: key 'results' not in response")
        results = resp['results']
        for result in results:
            if not 'endDate' in result.keys(): raise Exception("ERROR: key 'endDate' not in response (result)")
            if not 'startDate' in result.keys(): raise Exception("ERROR: key 'startDate' not in response (result)")
            if not 'centroid' in result.keys(): raise Exception("ERROR: key 'centroid' not in response (result)")
            if not 'point' in result['centroid'].keys(): raise Exception("ERROR: key 'point' not in response (result['centroid'])")
            centroid = result['centroid']
            longitude = float(centroid['point'][0])
            latitude = float(centroid['point'][1])
            if not 'name' in result.keys(): raise Exception("ERROR: key 'name' not in response (result)")
            if not 'location' in result.keys(): raise Exception("ERROR: key 'location' not in response (result)")
            if not 'id' in result.keys(): raise Exception("ERROR: key 'id' not in response (result)")
            if not 'dataTypesCount' in result.keys(): raise Exception("ERROR: key 'dataTypesCount' not in response (result)")       
            if not 'boundingPoints' in result.keys(): raise Exception("ERROR: key 'boundingPoints' not in response (result)")        
            if not 'stations' in result.keys(): raise Exception("ERROR: key 'stations' not in response (result)")
            stations = result['stations']
            for station in stations:
                if not 'name' in station.keys(): raise Exception("ERROR: key 'name' not in response (stations)")
                if not 'id' in station.keys(): raise Exception("ERROR: key 'id' not in response (stations)")
                # Iterate over the dataTypes and make sure all of the datatypes exist and the startDate and endDate includes start/end period. 
                if not "dataTypes" in station.keys(): raise Exception("ERROR: key 'dataTypes' not in response (stations)")
                stn_datatypes = station['dataTypes']
                stn_datatypes_count = 0
                for stn_datatype in stn_datatypes:
                    if not "id" in stn_datatype.keys(): raise Exception("ERROR: key 'id' was expected in results/stations/dataTypes")
                    if not "startDate" in stn_datatype.keys(): raise Exception("ERROR: key 'startDate' was expected in results/stations/datatypes")
                    if not "endDate" in stn_datatype.keys(): raise Exception("ERROR: key 'endDate' was expected in results/stations/datatypes")
                    if stn_datatype['id'] in datatypes: 
                        stn_datatypes_count += 1
                if not stn_datatypes_count == len(datatypes):
                    pass
                    print(f"WARNING: All {len(datatypes)} datatypes of {datatypes_str} were NOT found in the station data for station: {station['id']}")
                else:
                    #print(f"datatypes {datatypes_str} were found in the station data for station: {station['id']}")
                    station_data.append([station['id'], latitude, longitude, result['startDate'], result['endDate']])
        

        print(f"{len(station_data)} stations found that meet the requirements & have all of the datatypes of {datatypes} ")
        return station_data


# ---------------------------------------------------------------------------------------------------------
# NCEI Data Service API


def get_noaa_ncei_data_by_stn(stations:list=None, dataset:str=None, datatypes:list=None, start_date:str=None, end_date:str=None, units:str=None, verbose:bool=False):
    """
    Using the latest NOAA NCEI API endpoint (as of 2023)

    Uses the NOAA NCEI Data Service API to return the weather data of 'datatypes' from the list of 'stations' between 'start_date' and 'end_date'.
    Return a list of dictionaries with each dictionary the data from the station with keys: id, date, and datetypes.
    Returns None if no data was acquired.

    Usage:

    dataset = "daily-summaries"

    # See datatypes available in Table 4 of: https://www.ncei.noaa.gov/pub/data/cdo/documentation/GHCND_documentation.pdf
    datatypes = ["TMIN","TMAX","PRCP"]

    # For "daily_summaries" the start_date and end-date should be the same day in the past.
    start_date = "2010-02-01"
    end_date = "2010-02-01"

    
    Output:

    
    """

    import operator
    from datetime import datetime
    import json

    def validate_date_str_format(date_string):
        """
        Validates if a date string is in "YYYY-MM-DD" format and represents a valid date.

        Args:
            date_string (str): The date string to validate.

        Returns:
            bool: True if the date string is valid, False otherwise.
        """
        from datetime import datetime

        if not len(date_string) == 10: return False

        try:
            # Attempt to parse the string into a datetime object using the specified format.
            # This will raise a ValueError if the string does not match the format
            # or if it represents an invalid date (e.g., "2023-02-30").
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            # If a ValueError is raised, the string is not in the correct format
            # or is not a valid date.
            return False

    if stations is None or len(stations) == 0: raise Exception("Argument 'stations' is invalid")

    datasets = ["daily-summaries", "global-hourly", "global-summary-of-the-month"]
    if not dataset in datasets: raise Exception(f"dataset {dataset} is not a member of {datasets}")

    if datatypes is None or len(datatypes) == 0: raise Exception("Argument 'datatypes' is invalid")
    if not validate_date_str_format(start_date): raise Exception("Argument 'start_date' is invalid")
    if not validate_date_str_format(end_date): raise Exception("Argument 'end_date' is invalid")
    if not datetime.strptime(start_date, "%Y-%m-%d") <= datetime.strptime(end_date, "%Y-%m-%d"): raise Exception("Argument 'start_date' must be <= 'end_date")
    if units is None or not units in ['metric','standard']: raise Exception(f"Argument 'units' not passed or invalid.  Must be one of: {['metric','standard']}")

    if len(stations) == 0:
        stations_str = ",".join(stations)
    else:
        stations_str = stations[0]
    #print(f"stations_str: {stations_str}")

    datatypes_str = ",".join(datatypes)

    # WORKS:
    # dataset: global-hourly, global-summary-of-the-month, daily-summaries
    # dataTypes: TMIN,TMAX, PRCP
    # &bbox=40.94077,-76.62267,39.94077,-75.62267
    # https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-summary-of-the-year&dataTypes=DP01,DP05,DP10,DSND,DSNW,DT00,DT32,DX32,DX70,DX90,SNOW,PRCP&stations=ASN00084027&startDate=1952-01-01&endDate=1970-12-31&includeAttributes=true&format=json
    # https://www.ncei.noaa.gov/access/services/data/v1?dataset=daily-summaries&dataTypes=TMIN,TMAX,PRCP&stations=USC00081306&startDate=2010-02-01&endDate=2010-02-01&includeAttributes=true&format=json


    url = "https://www.ncei.noaa.gov/access/services/data/v1"
    url += f"?dataset={dataset}"
    url += f"&dataTypes={datatypes_str}"
    url += f"&startDate={start_date}"
    url += f"&endDate={end_date}"
    url += f"&stations={stations_str}"
    url += f"&format=json"
    url += f"&units={units}"
    if verbose: print(url)

    # Get your NOAA NCEI API key/token at: https://www.ncdc.noaa.gov/cdo-web/token
    headers={'token': os.getenv('API_NOAA_NCEI')}
    
    try:
        #req = requests.get(url, data=None, json=None, headers=None)
        req = savvy_request_get(url=url, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), ' fn()', url)
        print(f"get_noaa_ncei_data_by_stn() experienced a HTTP GET error while executing the request for url {url}")
        print(f"ERROR: {repr(e)}")
        return None
    
    if req is None:
        print(f"get_noaa_ncei_data_by_stn() experienced a HTTP GET error while executing the request for url {url}")
        return None

    resp = req.json()
    """
    [
        {
            "DATE": "2010-02-01",
            "STATION": "USC00081306",
            "TMAX": "  233",
            "TMIN": "  200",
            "PRCP": "    0"
        }
        ..
    ]
    """
    if len(resp) == 0:
        print("No results from query ", url)
        return None
    else:
        pass
        #print(json.dumps(resp, sort_keys=False, indent=2))

        # First level keys of interest:  DATE, STATION and the datatypes

        if len(resp) == 0:
            raise Exception(f"Unexpected response content. len(resp) = {len(resp)}")

        #results = resp[0]
        #print(f"results: {results}")
        # results: {'DATE': '2010-02-01', 'STATION': 'USC00081306', 'TMAX': '  74', 'TMIN': '  68', 'PRCP': '0.00'}

        results = []

        for stn in resp:

            stn_data = {}

            if not "DATE" in stn.keys(): raise Exception("ERROR: key 'DATE' not in the JSON response")
            if not "STATION" in stn.keys(): raise Exception("ERROR: key 'STATION' not in the JSON response")

            stn_data['date'] = stn['DATE']
            stn_data['station'] = stn['STATION']

            for datatype in datatypes:
                if not datatype in stn.keys(): raise Exception(f"ERROR: key '{datatype}' not found in the JSON response")
                stn_data[datatype] = stn[datatype]
                # temperature in F, precipation in inches

            #print(f"stn_data: {stn_data}")

            results.append(stn_data)

        return results


def get_noaa_ncei_units_by_datatype(datatype:str=None, units:str=None):
    """
    Returns the engineering unit (standard or metric) per 'units' and 'datatype'.

    """
    # Data types and units can be found in:  https://www.ncei.noaa.gov/pub/data/cdo/documentation/GHCND_documentation.pdf
    # or http://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt

    if datatype is None: raise Exception("Argument 'datatype' was not passed to the fn")
    if units is None: raise Exception("Argument 'datatype' not passed to the fn")
    if not units in ["standard","metric"]: raise Exception(f"The value for argument 'units' is invalid.  Must be one of {['standard','metric']}")

    datatype = str(datatype).upper()
    units = str(units).lower()

    match datatype:
        case "TOBS" | "TMIN" | "TMAX" | "MDTN" | "MDTX":
            if units == "standard":
                return "F"
            else:
                # metric
                return "C"
        case "PRCP" | "SNOW" | "SNWD" | "MDPR" | "MDSF":
            if units == "standard":
                return "in"
            else:
                # metric
                return "mm"
        
        case "WSF1" | "WSF5" | "WSFG":
            if units == "standard":
                return "mph"
            else:
                # metric
                return "meters/s"
        
        case "WDF1" | "WDF5" | "WDFG":
            return "degrees"
        
        case "WT01" | "WT02"|"WT04"|"WT05"|"WT06"|"WT07"|"WT08"|"WT10"|"WT11"|"WT17"|"WT18"|"WT21"|"WT22"|"WV01"|"WV07"|"WV18"|"WV20":
            return ""
        
        case _:
            raise Exception(f"datatype of '{datatype}' has not been defined yet")

# ---------------------------------------------------------------------------------------------------------
# Examples & Tests

def ex_get_gps_bounding_box():
    bbox_coords = [
        {"latitude": -88.77425, "longitude": 37.05635},
        {"latitude": 40.44077, "longitude": -76.12267},      # From the medium.com article
    ]
    bbox_coord = bbox_coords[1]
    latitude = bbox_coord['latitude']
    longitude = bbox_coord['longitude']
    deg_lat = 0.1
    deg_lon = 0.1
    n, w, s, e = get_gps_bounding_box(latitude, longitude, deg_lat, deg_lon, False)
    print(f"The bounding box for {latitude},{longitude} offset by {deg_lat},{deg_lon} degrees is {n}, {w}, {s}, {e}")

    midpoint = midpoint_euclidean(n, w, s, e)
    print(f"The midpoint of the bounding box {n}, {w}, {s}, {e} is {midpoint}")

    #dist_m = haversine_distance(northwest_coord[0], northwest_coord[1], southeast_coord[0], southeast_coord[1])
    dist_m = haversine_distance(n, w, s, e)
    print(f"The distance between the corners of the bounding box is {round(dist_m,3)} m  = {round(dist_m*3.281,3)} ft = {round(dist_m/1609,3)} mi")


def ex_get_noaa_ncei_units_by_datatype():
    """Demonstrate & test the use of get_noaa_ncei_units_by_datatype()."""

    datatypes = ["TMIN","TMAX","TOBS","PRCP","SNOW","SNWD","MDPR","MDSF","MDTN","MDTX","WDF1","WSF1","WDF5","WSF5","WSFG","WDFG","WT01","WT02","WT04","WT05","WT06","WT07","WT08","WT10","WT11","WT17","WT18","WT21","WT22","WV01","WV07","WV18","WV20"]
    #datatypes.append("UNKNOWN")

    for datatype in datatypes:
        std = get_noaa_ncei_units_by_datatype(datatype, 'standard')
        metric = get_noaa_ncei_units_by_datatype(datatype, 'metric')
        if len(std) == 0:
            print(f"Units for {datatype}: ''")
        elif std == metric:
            print(f"Units for {datatype}: {std}")
        else:
            # std != metric
                print(f"Units for {datatype}: {std} or {metric}")


def ex_get_noaa_ncei_datatypes_by_dataset():
    """Test & demonstrate use of get_noaa_ncei_datatypes_by_dataset()"""

    # "global-hourly", "daily-summaries", "global-summary-of-the-month"
    #dataset = "global-hourly"
    dataset = "daily-summaries"
    #dataset = "global-summary-of-the-month"

    datatypes = get_noaa_ncei_datatypes_by_dataset(dataset)


def ex_get_noaa_ncei_stations_by_search(inputs_idx:int=None):
    """
    Demonstrate the use of get_noaa_ncei_stations_by_search().
    """

    from random import randint

    # id's 0 - 4 are for testing the identification of (weather) stations for various tricky locations in terms of station and dataset/datatype availability.
    # id's 5 - 7 test each of the datasets "global-summary-of-the-month", "daily-summaries", "global-hourly"
    inputs = [
        {"id": "Shenandoah National Park, VA", "dataset": "global-summary-of-the-month", "latitude": 38.5288, "longitude": -78.4383, "datatypes": ["TMIN","TMAX","PRCP"], "start_date": "2010-02-01", "end_date": "2010-12-31"},
        {"id": "CNH Technical Center, New Holland PA", "dataset": "global-summary-of-the-month", "latitude": 40.0900, "longitude": -76.1042, "datatypes": ["TMIN","TMAX","PRCP"], "start_date": "2010-02-01", "end_date": "2010-12-31"},
        {"id": "Ozark Mountains", "dataset": "global-summary-of-the-month", "latitude": 35.800, "longitude": -93.246, "datatypes": ["TMIN","TMAX","PRCP"], "start_date": "2010-02-01", "end_date": "2010-12-31"},
        {"id": "Adirondack Mountains", "dataset": "global-summary-of-the-month", "latitude": 44.1247154, "longitude": -73.8693043, "datatypes": ["TMIN","TMAX","PRCP"], "start_date": "2010-02-01", "end_date": "2010-12-31"},
        {"id": "Alcatraz Main Cell House", "dataset": "daily-summaries", "latitude": 37.82676234, "longitude": -122.4230206, "datatypes": ["TMIN","TMAX","PRCP"], "start_date": "2010-02-01", "end_date": "2010-12-31"},
        
        {"id": "Boot Key Harbor, Marathon FL (10 Sep 2017 Hurricane Irma)", "dataset": "global-hourly", "latitude": 24.7063, "longitude": -81.0918, "datatypes": ["TMP","WND"], "start_date": "2017-09-10", "end_date": "2017-09-10"},
        {"id": "wamy.com", "dataset": "daily-summaries", "latitude": 25.78320, "longitude": -80.18930, "datatypes": ["TMIN","TMAX","PRCP"], "start_date": "2019-02-01", "end_date": "2019-02-01"},
        {"id": "16 Solly Ln", "dataset": "global-summary-of-the-month", "latitude": 40.4407, "longitude": -76.12267, "datatypes": ["TMIN","TMAX","PRCP"], "start_date": "2010-02-01", "end_date": "2010-12-31"},

        {"id": "Boot Key Harbor, Marathon FL (10 Sep 2017 Hurricane Irma)", "dataset": "daily-summaries", "latitude": 24.7063, "longitude": -81.0918, "datatypes": ["WSF5","WDF5"], "start_date": "2017-09-09", "end_date": "2017-09-09"},
        {"id": "wamy.com", "dataset": "daily-summaries", "latitude": 25.78320, "longitude": -80.18930, "datatypes": ["TMIN","TMAX","WSF2","WDF2","WSF5","WDF5"], "start_date": "2025-02-01", "end_date": "2025-02-01"},
    ]

    # For global-hourly, the datatypes are not the same as for daily-summaries and global-summary-of-the-month.
    # See get_noaa_ncei_datatypes_by_dataset() for a list of datatypes, but don't be surprised when many of them don't provide any data. 

    if inputs_idx is None:
        #input = inputs[randint(0,len(inputs))]     # Randomly select an item from inputs
        input = inputs[6]                           # Manually select an item by index from the inputs
    else:
        if inputs_idx > len(inputs): raise Exception(f"Argument 'inputs_idx' is out of range. [{0}:{len(inputs)}]")
        input = inputs[inputs_idx]

    id = input['id']
    
    # dataset: global-hourly, daily-summaries, global-summary-of-the-month
    dataset = input['dataset']  
    
    latitude = input['latitude']
    longitude = input['longitude']

    # Examples:  ["TMIN","TMAX" "WND"]
    datatypes = input['datatypes']

    start_date = input['start_date']
    end_date = input['end_date']

    print(f"\nSearching NOAA NCEI for stations close to {id} @ {latitude},{longitude} for dataset '{dataset}':")
    t_lap_start = perf_counter()
    stations = get_noaa_ncei_stations_by_search(dataset, latitude, longitude, datatypes, start_date, end_date, verbose=True)
    if stations is None or len(stations) == 0:
        print("NO results")
    else:
        print(f"\nThe best station choice is {stations[0][3]} with delta elevation of {round(stations[0][1]*3.281,1)} ft and delta distance of {round(stations[0][2]/1609,2)} mi from the target of {latitude},{longitude} and with data from {stations[0][6]} to {stations[0][7]}\n")
        # All data in stations:
        print("sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd")
        for station in stations:
            print(station)
    print(f"{round(perf_counter()-t_lap_start,1)} sec elapsed")

    """
    Sample Results

    input = inputs[5]
    Searching NOAA NCEI for stations close to Boot Key Harbor, Marathon FL @ 24.7063,-81.0918 for dataset 'global-hourly':
    The best station choice is 99735699999 with delta elevation of 5.906 ft and delta distance of 1.078 mi from the target of 24.7063,-81.0918 and with data from 2018-01-01T00:00:00 to 2018-12-31T23:59:59
    sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd
    [3097.1, 1.8, 1734.0, '99735699999', 24.72, -81.1, '2018-01-01T00:00:00', '2018-12-31T23:59:59']
    2.1 sec elapsed

    
    input = inputs[6]
    Searching NOAA NCEI for stations close to wamy.com @ 25.7832,-80.1893 for dataset 'daily-summaries':
    The best station choice is USC00081306 with delta elevation of 0.0 ft and delta distance of 7.957 mi from the target of 25.7832,-80.1893 and with data from 1997-08-01T00:00:00 to 2025-05-30T23:59:59
    sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd
    [138.6, 0.0, 12802.1, 'USC00081306', 25.6719, -80.1566, '1997-08-01T00:00:00', '2025-05-30T23:59:59']
    [659.3, 0.0, 29152.9, 'USW00012888', 25.64226, -80.43467, '1998-06-15T00:00:00', '2025-05-31T23:59:59']
    [5081.8, 0.4, 12791.1, 'USW00012839', 25.78805, -80.31694, '1948-01-01T00:00:00', '2025-05-31T23:59:59']
    [6642.4, 0.2, 27785.7, 'USC00084050', 26.0281, -80.1341, '2002-11-01T00:00:00', '2025-06-01T23:59:59']
    [9398.6, 0.4, 24611.7, 'USW00092809', 25.99956, -80.24119, '1999-04-20T00:00:00', '2025-05-31T23:59:59']
    [11161.1, 1.8, 6157.8, 'USW00092811', 25.8063, -80.1334, '1927-01-05T00:00:00', '2025-03-31T23:59:59']
    [12638.0, 0.7, 16939.1, 'USW00012882', 25.91017, -80.28283, '1998-05-21T00:00:00', '2025-05-31T23:59:59']
    [16974.1, 0.9, 19702.4, 'USC00085667', 25.7553, -80.3836, '1999-05-01T00:00:00', '2025-06-01T23:59:59']
    [22274.4, 0.7, 32975.0, 'USW00012849', 26.07875, -80.16223, '1945-03-01T00:00:00', '2025-05-31T23:59:59']
    [22474.9, 2.1, 10842.3, 'USC00083909', 25.82726, -80.28592, '1940-06-29T00:00:00', '2025-06-01T23:59:59']
    [34619.0, 1.8, 18735.9, 'USC00086315', 25.95, -80.2158, '2001-07-01T00:00:00', '2025-05-31T23:59:59']
    [46701.1, 1.4, 33356.9, 'USC00087020', 25.5819, -80.4361, '1958-12-01T00:00:00', '2025-05-07T23:59:59']
    11.7 sec elapsed

    
    input = inputs[7]
    Searching NOAA NCEI for stations close to 16 Solly Ln @ 40.4407,-76.12267 for dataset 'global-summary-of-the-month':
    The best station choice is USC00360785 with delta elevation of 11.484 ft and delta distance of 6.522 mi from the target of 40.4407,-76.12267 and with data from 1978-05-01T00:00:00 to 2025-04-30T23:59:59
    sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd
    [37246.8, 3.5, 10494.3, 'USC00360785', 40.38028, -76.02745, '1978-05-01T00:00:00', '2025-04-30T23:59:59']
    [48124.4, 3.1, 15730.5, 'USW00014712', 40.37342, -75.95924, '1949-01-01T00:00:00', '2025-05-31T23:59:59']
    [67342.7, 4.1, 16607.9, 'USC00363632', 40.55156, -75.99105, '1894-01-01T00:00:00', '2021-09-30T23:59:59']
    5.3 sec elapsed

    
    This location is a particular challenge because of the location relative to nearby stations. 
    The long distance between the target location and available stations causes the script to continue until at least 30 stations are found. 
    input = inputs[3]
    Searching NOAA NCEI for stations close to Adirondack Mountains @ 44.1247154,-73.8693043 for dataset 'global-summary-of-the-month':
    The best station choice is USW00014742 with delta elevation of 3826.6 ft and delta distance of 42.777 mi from the target of 44.1247154,-73.8693043 and with data from 1940-12-01T00:00:00 to 2025-05-31T23:59:59
    sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd
    [80274838.9, 1166.3, 68827.5, 'USW00014742', 44.46825, -73.1499, '1940-12-01T00:00:00', '2025-05-31T23:59:59']
    [97254083.0, 931.7, 104382.7, 'USW00094705', 44.20503, -72.56545, '1948-06-01T00:00:00', '2025-05-31T23:59:59']
    [105118922.4, 1169.7, 89868.0, 'USW00014750', 43.33849, -73.61024, '1944-05-01T00:00:00', '2025-05-31T23:59:59']
    ...
    [490208590.5, 1264.5, 387673.8, 'USW00094789', 40.63915, -73.7639, '1948-07-01T00:00:00', '2025-05-31T23:59:59']
    82.4 sec elapsed

    """

    return input, stations


def ex_get_nooa_ncei_data_by_stn(input:list=None, stations:list=None):
    """
    Demonstrate & test the get_nooa_ncei_data_by_stn()

    Arguments 'input' and 'stations' are optional.  If none provided, defaults will be supplied.
    """

    from random import randint
    station_ids= "USC00081306"
    if not stations is None and len(stations) == 0: raise Exception(f"Argument 'stations' has no data.  {stations}")
    
    if input is None and stations is None:
        # You must manuall make assignments below.
        # sort, delta_elevation_m, delta_distance_m, ID, latitude, longitude, dateStart, dateEnd
        #station = [138.6, 0.0, 12802.1, 'USC00081306', 25.6719, -80.1566, '1997-08-01T00:00:00', '2025-05-28T23:59:59']

        # Below is actual station data output from get_noaa_ncei_stations_by_search()
        stations = [
            [138.6, 0.0, 12802.1, 'USC00081306', 25.6719, -80.1566, '1997-08-01T00:00:00', '2025-05-28T23:59:59'],
            [659.3, 0.0, 29152.9, 'USW00012888', 25.64226, -80.43467, '1998-06-15T00:00:00', '2025-05-28T23:59:59'],
            [5081.8, 0.4, 12791.1, 'USW00012839', 25.78805, -80.31694, '1948-01-01T00:00:00', '2025-05-29T23:59:59'],
            [6642.4, 0.2, 27785.7, 'USC00084050', 26.0281, -80.1341, '2002-11-01T00:00:00', '2025-05-29T23:59:59'],
            [9398.6, 0.4, 24611.7, 'USW00092809', 25.99956, -80.24119, '1999-04-20T00:00:00', '2025-05-28T23:59:59'],
            [11161.1, 1.8, 6157.8, 'USW00092811', 25.8063, -80.1334, '1927-01-05T00:00:00', '2025-03-31T23:59:59'],
            [12638.0, 0.7, 16939.1, 'USW00012882', 25.91017, -80.28283, '1998-05-21T00:00:00', '2025-05-28T23:59:59'],
            [16974.1, 0.9, 19702.4, 'USC00085667', 25.7553, -80.3836, '1999-05-01T00:00:00', '2025-05-29T23:59:59'],
            [22274.4, 0.7, 32975.0, 'USW00012849', 26.07875, -80.16223, '1945-03-01T00:00:00', '2025-05-29T23:59:59'],
            [22474.9, 2.1, 10842.3, 'USC00083909', 25.82726, -80.28592, '1940-06-29T00:00:00', '2025-05-29T23:59:59'],
            [34619.0, 1.8, 18735.9, 'USC00086315', 25.95, -80.2158, '2001-07-01T00:00:00', '2025-05-29T23:59:59'],
            [46701.1, 1.4, 33356.9, 'USC00087020', 25.5819, -80.4361, '1958-12-01T00:00:00', '2025-05-07T23:59:59'],
        ]
        stations = stations[0][3]     # USC00081306
        #stations = stations[0][3] # stations[1][3]]        # "USC00081306","USW00012888"
        station_id= stations
        print(f"Stations if   {stations}")
        dataset = "daily-summaries"
        start_date = "2010-02-01"
        end_date = "2010-02-01"
        datatypes = ["TMIN","TMAX","PRCP"]

    else:
        # Get the first station id from 'stations'.
        station_ids = stations[0][3]
        """
        # Get the station ids from 'stations'.
        station_ids = []
        for station in stations:
            station_ids.append(station[3])
        """
        # Get the inputs from argument 'input'.
        dataset = input['dataset']
        start_date = input['start_date']
        end_date = input['end_date']
        datatypes = input['datatypes']
        


    t_lap_start = perf_counter()

    print(f"\nFetching {datatypes} from dataset {dataset} for stations {station_ids} between {start_date} and {end_date}..")
    data = get_noaa_ncei_data_by_stn(station_ids, dataset, datatypes, start_date, end_date, units="standard", verbose=True)
    if data is None:
        print(f"ERROR: No data ({datatypes} from dataset {dataset} could be found for stations {station_ids} between {start_date} and {end_date}.")
    else:
        #print(data)
        for stn in data:
            print(f"{stn}")

    print(f"{round(perf_counter()-t_lap_start,1)} sec elapsed")

    """
    Output for daily_summaries:
    {'date': '2019-02-01', 'station': 'USW00012888', 'TMIN': '60', 'TMAX': '80', 'PRCP': '0.00'}

    """


def ex_parse_ncei_search_results():
    """
    Demonstrates the use of parse_ncei_search_results().
    Plots the results to a HTML map so you can visualize the station locations. 

    parse_ncei_search_results() executes a NOAA NCEI Search Service API HTTP GET and parses the returned data. 
    Best used as a tool for evaluation of the availability of datatypes.
    The returned result will tell you the date range of the data for each station.  

    """

    def plot_stns_on_map(stations:list=None, filename:str=None):
        """
        Arguments:

        filename:  filename without the extension

        """
        import folium
        from pathlib import Path

        path_file_map = Path(Path.cwd()).joinpath(f"{filename}.html")

        # topographic with political borders
        tiles = "https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}"
        attr = 'Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'
        map_osm = folium.Map(location=[38.0, -97.0], zoom_start=4, 
                            tiles=tiles, 
                            attr=attr
                            )
        for station in stations:
            #print(f"{station[0]}  {station[1]},{station[2]}  {station[3]} .. {station[4]}")
        
            # popup is shown when you click on it
            popup = f"{station[0]} @ {station[1]},{station[2]}  {station[3]} .. {station[4]}"
            
            # tooltip is shown when the mouse hovers over the icon
            tooltip = f"{station[0]} @ {station[1]},{station[2]}  {station[3]} .. {station[4]}"
            
            # icon_color = 'blue', 'green', 'orange', 'red', 
            # icon_shape = "pushpin", "tree-conifer", "camera", "star-empty, "asterisk"
            #icon = folium.Icon(color="red", icon="asterisk")
            icon = folium.Icon(color="blue", icon="asterisk")
            
            folium.Marker([station[1], station[2]], popup=popup, tooltip=tooltip, icon=icon,).add_to(map_osm) 

        # Save the map as an HTML file
        map_osm.save(path_file_map)
        print(f"\nStatic map of {len(stations)} station locations saved to {path_file_map}")


    dataset = "daily-summaries"        # dataset: global-hourly, global-summary-of-the-month, daily-summaries
    
    #datatypes = ["TMIN","TMAX"]     # Over 10,000 stations
    datatypes = ["WSF1", "WDF1"]   #  335 stations for avg wind speed and direction
    #datatypes = ["WSF5", "WDF5"]   #  1181 stations for wind gust and direction
    #datatypes = ["WT04", "WT05"]       #  Over 10,000 stations for hail, ice pellets, sleet, snow pellets, small hail.
    #datatypes = ["WT10"]              #  1382 stations for tornado, waterspout, or funnel cloud
    #datatypes = ["TMIN","TMAX", "WSF1", "WDF1", "WSF5", "WDF5"]  #  stations

    stations = parse_ncei_search_results(dataset, datatypes, limit=10)

    if stations is None or len(stations) == 0:
        print("NO results")
    else:
        print(f"{len(stations)} stations returned for {dataset} and {datatypes}")
        if len(stations) < 50:
            print("station ID, latitude, longitude, dateStart, dateEnd")
            for station in stations:
                print(station)

    # Generate a plot of the stations to help visualize the data
    filename = f"map_of_stations_for_{dataset}_and_datatype_" + "_".join(datatypes)
    plot_stns_on_map(stations, filename)


if __name__ == '__main__':


    ex_get_gps_bounding_box()

    ex_get_noaa_ncei_units_by_datatype()

    ex_get_noaa_ncei_datatypes_by_dataset()

    input, stations = ex_get_noaa_ncei_stations_by_search()

    ex_get_nooa_ncei_data_by_stn()

    # Get DAILY summary data for a specific location identified by inputs_idx=6.  See ex_get_noaa_ncei_stations_by_search()
    #input, stations = ex_get_noaa_ncei_stations_by_search(inputs_idx=6)
    #ex_get_nooa_ncei_data_by_stn(input, stations)
    """
    """

    # Get HOURLY summary data for a specific location identified by inputs_idx=5.  See ex_get_noaa_ncei_stations_by_search() 
    """
    input, stations = ex_get_noaa_ncei_stations_by_search(inputs_idx=5)
    ex_get_nooa_ncei_data_by_stn(input, stations)
    """

    # Get MONTHLY summary data for a specific location identified by inputs_idx=5.  See ex_get_noaa_ncei_stations_by_search()  
    """
    input, stations = ex_get_noaa_ncei_stations_by_search(inputs_idx=7)
    ex_get_nooa_ncei_data_by_stn(input, stations)
    """

    # Test and visualize how many stations support data by dataset and datatype. 
    #ex_parse_ncei_search_results()

    # Report the script execution time
    print(f"\nElapsed time {round(perf_counter()-t_start_sec,3)} s")

