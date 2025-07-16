#
#   Written by:  Mark W Kiehl
#   http://mechatronicsolutionsllc.com/
#   http://www.savvysolutions.info/savvycodesolutions/

"""
Functions relating to GPS coordinates and places/locations

lat_lon_is_valid(lat1, lon1, verbose)
distance(origin, destination)
haversine_distance(lat1, lon1, lat2, lon2)
distance_to_geofence(point, geofence_start, geofence_end)
midpoint_euclidean(x1,y1,x2,y2)
get_gps_bounding_box(latitude, longitude, deg_lat, deg_lon, verbose)
elevation_by_lat_lon(lat1, lon1)
get_lat_lon_by_address(**kwargs)
get_address_by_lat_lon(latitude, longitude)
get_place_rating(place, verbose)

get_fips_code_by_lat_lon(lat1, lon1, verbose)
    get_fips_codes_by_lat_lon_geocodio(lat1, lon1, verbose)
    get_fips_code_by_lat_lon_fcc(lat1, lon1, verbose)


*** SOURCE RESIDES IN FOLDER: savvy ***

"""

# Define the script version in terms of Semantic Versioning (SemVer)
# when Git or other versioning systems are not employed.
__version__ = "0.0.3"
from pathlib import Path
print("'" + Path(__file__).stem + ".py'  v" + __version__)
# 0.0.0 
# 0.0.1     Added get_ip_gps_coordinates_geocoder() & get_ip_gps_coordinates_ip_api()
# 0.0.2     Added savvy_get_extreme_lat_long_in_set()
# 0.0.3     Revised distance() to use haversine_distance() & completely revised the API key system. 

"""
pip install usaddress
pip install -U googlemaps
pip install geopy

pip install fake-useragent

pip install folium

"""


# Configure the required API keys to be retrieved from either the module savvy_secrets or the local .env file.
import os
import sys
from pathlib import Path

# Retrieve API Keys stored in the local .env file (if it exists).
import os
try:
    from dotenv import load_dotenv
except Exception as e:
    raise Exception(f"{e} \t Is dotenv module installed?  pip install python-dotenv")
# Load environment variables from the .env file
load_dotenv()

# Add path 'savvy' so it can be found for library imports, including the module savvy_secrets
from pathlib import Path
import sys
sys.path.insert(1, str(Path(Path.cwd().parent).joinpath('savvy')))      

# GOOGLE_MAPS_API_KEY
if Path.cwd().parts[len(Path.cwd().parts)-1]=="savvy" or str(Path(Path.cwd().parent).joinpath('savvy')) in sys.path:
    # The folder 'savvy' is the current project path OR it exists in the Python interpreter's search path for modules.
    # Get the API Key from the module savvy_secrets and define the OS environment variable.
    #try:
    #    from savvy_secrets import api_secrets
    #except Exception as e:
    #    raise Exception(f"{e}\nThe folder 'savvy' is not the current project folder NOR does it exist in the Python interpreter's search path for modules (sys.path). Try: sys.path.insert(1, str(Path(Path.cwd().parent).joinpath('savvy')))")
    #if not "api_google_maps" in api_secrets.keys(): raise Exception("ERROR: api_secrets from savvy_secrets.py doesn't have the key 'api_google_maps'.")
    os.environ['GOOGLE_MAPS_API_KEY']# = 'AIzaSyDWihLFg-kzgyEWKFDd-j6lNj3Wl6TH924'
# Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
if not os.getenv('GOOGLE_MAPS_API_KEY'): 
    raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

# API_GEOCODIO_KEY
if Path.cwd().parts[len(Path.cwd().parts)-1]=="savvy" or str(Path(Path.cwd().parent).joinpath("savvy")) in sys.path:
    # The folder 'savvy' is the current project path OR it exists in the Python interpreter's search path for modules.
    # Get the API Key from the module savvy_secrets and define the OS environment variable.
    #try:
    #    from savvy_secrets import api_secrets
    #except Exception as e:
    #    raise Exception(f"{e}\nThe folder 'savvy' is not the current project folder NOR does it exist in the Python interpreter's search path for modules (sys.path). Try: sys.path.insert(1, str(Path(Path.cwd().parent).joinpath('savvy')))")
    #if not "api_geocodio" in api_secrets.keys(): raise Exception("ERROR: api_secrets from savvy_secrets.py doesn't have the key 'api_geocodio'.")
    os.environ['API_GEOCODIO_KEY']# ='cfee7280eef067860f682e6b6b8ac98e8b6bc72'
# Verify the Windows environment variable API_GEOCODIO_KEY is set & demonstrate how to access it.
if not os.getenv('API_GEOCODIO_KEY'): 
    raise Exception("Windows environment variable 'API_GEOCODIO_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")



"""
Geospatial Indexing

Geospatial indexing, or Geocoding, is the process of indexing latitude-longitude pairs to small subdivisions of geographical space.
Currently the most popular geospatial indexing techniques are:  Geohash, Google S2, and Uber H3.


Google S2

S2 provides locality-sensitive hashing (alleviating the issues with Geohash).


Uber H3

H3 has two key innovations: (1) the use of hexagons in place of squares, and (2) the use of an icosahedron projection onto Earth.
Note however that that the strict spatial hierarchy discussed above regarding Geohash — that if a latitude-longitude point is contained in a cell then it is guaranteed to be contained in that cell’s parent — is not maintained in H3.




Geohash

Geohash enables the mapping of latitude-longitude pairs to Geohash squares of arbitrary user-defined resolution.
The squares are uniquely identified by a signature string, such as "drt".
Geohash is simple, fast, and the geohash strings preserve spatial hierarchy.
Geohash has two major shortcomings:
    1)  Two locations that are close in physical distance are not guaranteed to be close in their computed geohash strings,
        AND two locations that are close in their geohash string might not be close in physical distance.
    2)  The equirectangular projection of the globe that is used by Geohash leads to high variability in the size of the geohash squares.


Related Links:
    Geospatial Indexing Explained: A Comparison of Geohash, S2, and H3
    https://towardsdatascience.com/geospatial-indexing-explained-a-comparison-of-geohash-s2-and-h3-68d4ed7e366d

    Geospatial Indexing Explained: A Comparison of Geohash, S2, and H3
    https://towardsdatascience.com/geospatial-indexing-explained-a-comparison-of-geohash-s2-and-h3-68d4ed7e366d

"""


"""
Google Maps API:
    max 100 requests/s
    $200 credit/mo = ($200/5*1000) = 40,000 requests/month


"""

"""
GeoPy
a Python library that is a wrapper for several geocoding web services, such as 
Google Maps, Bing Maps, MapQuest, Baidu, and many more that will clean raw
address data. 
https://geopy.readthedocs.io/en/stable/
Tutorial: https://medium.com/towards-data-science/transform-messy-address-into-clean-data-effortlessly-using-geopy-and-python-d3f726461225
"""


"""
# pip install us
# US - A package for easily working with US and state metadata.
# https://pypi.org/project/us/
import us
print(us.states.STATES)   # [<State:Alabama>, <State:Alaska>,  .., <State:Wyoming>]
print(us.states.lookup('MD'))   # Maryland
print(us.states.lookup('maryland'))   # Maryland
print(us.states.lookup('MD').abbr)   # MD
print(us.states.lookup('MD').fips)   # 24
# Shapefiles are also available
"""


import requests
import json
import math
from random import randint
from time import sleep
import urllib.parse


# pip install geopy
# Google Maps Paid API
#from geopy.geocoders import GoogleV3, Geocodio
#geolocator = GoogleV3(api_key = os.getenv('GOOGLE_MAPS_API_KEY'))
#geolocator = Geocodio(api_key = os.getenv('API_GEOCODIO_KEY'))


# pip install -U googlemaps


# ---------------------------------------------------------------------------------------------------------
# Get user's GPS coordinates (approximate, based on user's IP address)


def get_ip_gps_coordinates_geocoder():
    """
    Returns GPS coordinates in decimal degrees for the PC calling this function based on the IP address.


    coordinates = get_ip_gps_coordinates_geocoder()
    if coordinates is not None:
        latitude, longitude = coordinates
        print(f"Your current GPS coordinates (based on IP address) are:")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"{latitude},{longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")

    """
    # https://geocoder.readthedocs.io/providers/IPInfo.html
    # https://medium.com/@omraghuvanshi1010/unveiling-your-location-a-python-guide-to-retrieve-current-gps-coordinates-d1ba282b44fd

    # pip install geocoder
    import geocoder

    g = geocoder.ip('me')#this function is used to find the current information using our IP Add
    if g.latlng is not None: #g.latlng tells if the coordiates are found or not
        return g.latlng
    else:
        return None


def get_ip_gps_coordinates_ip_api():
    """
    Returns GPS coordinates in decimal degrees for the PC calling this function based on the IP address.


    coordinates = get_ip_gps_coordinates_ip_api()
    if coordinates is not None:
        latitude, longitude = coordinates
        print(f"Your current GPS coordinates (based on IP address) are:")
        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"{latitude},{longitude}")
    else:
        print("Unable to retrieve your GPS coordinates.")

    """

    import requests
    import json

    try:
        #geolocates your location long and lat and city.
        response = requests.get('http://ip-api.com/json/')
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data['status'] == 'success':
            latitude = data['lat']
            longitude = data['lon']
            return latitude, longitude
        else:
            print(f"Error: {data['message']}")
    except requests.exceptions.RequestException as e:
        print(f"Error during IP geolocation: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        return None


# ---------------------------------------------------------------------------------------------------------
# GPS coordinates (latitude/longitude), distance between lat/lon, etc.

def lat_lon_is_valid(lat1, lon1, verbose=False):
    """
    Returns true if the passed latitude/longitude are valid

    
    #print(lat_lon_is_valid(34.736945, -92.29987, True))
    #print(lat_lon_is_valid(None, -92.29987, True))
    #print(lat_lon_is_valid(34.736945, None, True))
    #print(lat_lon_is_valid(91.123, -92.29987, True))
    #print(lat_lon_is_valid(-91.123, -92.29987, True))
    #print(lat_lon_is_valid(34.736945, -180.123, True))
    #print(lat_lon_is_valid(34.736945, 180.123, True))

    """
    
    if lat1 is None:
        #raise Exception('ERROR: argument "lat1" is missing.  lat_long_valid()')
        if verbose: print('ERROR: argument "lat1" is missing.  lat_long_valid()')
        return False
    if lon1 is None:
        #raise Exception('ERROR: argument "lon1" is missing.  lat_long_valid()')
        if verbose: print('ERROR: argument "lon1" is missing.  lat_long_valid()')
        return False
    if not isinstance(lat1, float):
        #raise Exception('ERROR: argument "lat1" is the wrong data type of ' + str(type(lat1)) + ', float expected.  lat_long_valid()')
        print('ERROR: argument "lat1" is the wrong data type of ' + str(type(lat1)) + ', float expected.  lat_long_valid()')
        return False
    if not isinstance(lon1,float):
        #raise Exception('ERROR: argument "lon1" is the wrong data type of ' + str(type(lon1)) + ', float expected.  lat_long_valid()')
        print('ERROR: argument "lon1" is the wrong data type of ' + str(type(lon1)) + ', float expected.  lat_long_valid()')
        return False
    #  -90 to 90 for latitude and -180 to 180 for longitude.
    if lat1 < -90 or lat1 > 90:
        #raise Exception('ERROR: argument "lat1" has a value of ' + str(lat1) + ' that is out of range (-90 to 90)  lat_long_valid()')
        print('ERROR: argument "lat1" has a value of ' + str(lat1) + ' that is out of range (-90 to 90)  lat_long_valid()')
        return False
    if lon1 < -180 or lon1 > 180:
        #raise Exception('ERROR: argument "lon1" has a value of ' + str(lon1) + ' that is out of range (-180 to 180)  lat_long_valid()')
        print('ERROR: argument "lon1" has a value of ' + str(lon1) + ' that is out of range (-180 to 180)  lat_long_valid()')
        return False
    
    return True


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Returns the distance in meters between the two GPS coordinates in decimal degrees.

    Usage:

        dist_m = haversine_distance(40.440363, -76.126746, 40.440406, -76.121293)
        print("dist_m: ", dist_m)
        # Result is 461.5 m.  The correct result is 461.5 m. 

        dist_m = haversine_distance(38.5288,-78.4383, 38.3683,-78.2503)
        print("dist_m: ", dist_m)
        # The correct answer is 24218.67 meters

    """

    import math

    # Radius of the Earth in meters
    earth_radius_m = 6371000.0
    
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences between the latitudes and longitudes
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Calculate the distance
    distance = earth_radius_m * c
    
    return distance


# USE haversine_distance() rather than distance()
def distance(origin, destination):
    """
    Calculate the Haversine distance.

    Parameters
    ----------
    origin : tuple of float
        (lat, long)
    destination : tuple of float
        (lat, long)

    Returns
    -------
    distance_in_km : float

    Examples
    --------
    dist_km = distance((lat1,lon1), (lat2,lon2))
    >>> origin = (48.1372, 11.5756)  # Munich
    >>> destination = (52.5186, 13.4083)  # Berlin
    >>> round(distance(origin, destination), 1)
    504.2
    """

    print("\nNOTE: Using haversine_distance() instead!!! \t distance((lat1,lon1),(lat2,lon2)) =>  haversine_distance(lat1, lon1, lat2, lon2)\n")
    #raise Exception("Revise code to use haversine_distance() in place of distance()")

    if origin is None: raise Exception('ERROR: missing arguments not passed to distance()')
    if destination is None: raise Exception('ERROR: missing arguments not passed to distance()')
    lat1, lon1 = origin
    lat2, lon2 = destination
    if not lat_lon_is_valid(lat1, lon1, True): raise Exception('ERROR: invalid arguments passed to distance()')
    if not lat_lon_is_valid(lat2, lon2, True): raise Exception('ERROR: invalid arguments passed to distance()')

    # Use function haversine_distance() instead of the distance() formula that follows after return.
    distance_m = haversine_distance(lat1, lon1, lat2, lon2)
    return distance_m / 1000.0


    # Get the distance between the requested lat/lon and the reverse geocoded lat/lon.
    # 38.5288, -78.4383 -> 38.5288751, -78.43669133995353
    # Delta: 0.0871 mi = 140.2 m = 0.14018 km = 153.3 yd = 0.07569 nm = 459.9 ft
    #dist_km = distance((38.5288, -78.4383), (38.5288751, -78.43669133995353))
    #dist_ft = dist_km*3281

    radius = 6371  # km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c
    return d    # km


def distance_to_geofence(point, geofence_start, geofence_end):
    """
    Calculates the distance in meters from one GPS location (point) to a geofence border (line)
    defined by the GPS coordinates of geofence_start and geofence_end.

    Usage:

    point = (40.440363, -76.126746)
    line_start = (40.440406, -76.121293)
    line_end = (40.443217, -76.124517)
    dist_m = distance_to_geofence(point, line_start, line_end)
    print("dist_m: ", dist_m)   # result: 362.8 m.  Correct result is 365 m (graphical estimate using Google Maps)

    """

    lat, lon = point
    lat1, lon1 = geofence_start
    lat2, lon2 = geofence_end

    # for cartesion systems 
    x = lon
    y = lat
    x1 = lon1
    y1 = lat1
    x2 = lon2
    y2 = lat2
    
    # dist_point_to_line(x, y, x1, y1, x2, y2):
    distance_to_line_cartesion = dist_point_to_line(x, y, x1, y1, x2, y2) * 111320      # 1 decimal degree = 111320 m
    print("distance_to_line_cartesion: ", round(distance_to_line_cartesion,1))

    distance_to_line_start = haversine_distance(lat, lon, lat1, lon1)
    print("distance_to_line_start: ", round(distance_to_line_start,1))
    
    """
    # Calculate the midpoint between the geofence line end points.
    lat_lon_mid = midpoint_euclidean(line_lat1, line_lon1,line_lat2, line_lon2)
    # Calculate the distance from the geofence line mid point and point. 
    distance_to_mid = haversine_distance(lat_lon_mid[0], lat_lon_mid[1], point_lat, point_lon)
    print(distance_to_mid, lat_lon_mid[0], lat_lon_mid[1])
    """
    
    distance_to_line_end = haversine_distance(lat, lon, lat2, lon2)     # meters
    print("distance_to_line_end: ", round(distance_to_line_end,1))
    
    # Calculate the distance in meters to the geofence line as the minimum of the distances to the start and end points
    distance_m = min(distance_to_line_start, distance_to_line_cartesion, distance_to_line_end)
    
    return distance_m


def midpoint_euclidean(x1,y1,x2,y2):
    """
    Returns the midpoint between two latitude/longitude coordinates in
    decimal degrees as a list where [0] is the latitude, and [1] is the
    longitude in decimal degrees. 

    # 40.44080081126309, -76.12260726282771 16 Solly Ln
    # 40.436759, -76.122597  nearby
    lat_lon = midpoint_euclidean(40.4408008, -76.122607, 40.436759, -76.122597)
    print('midpoint: ', lat_lon[0],',',lat_lon[1])
    #midpoint:  40.4387799 , -76.122602

    """
    if not lat_lon_is_valid(x1,y1,True):
        print(x1, y1, type(x1), type(y1))
        raise Exception('ERROR: arguments x1,y1 passed to midpoint_euclidean() is invalid')
    
    if not lat_lon_is_valid(x2,y2,True):
        print(x2, y2, type(x2), type(y2))
        raise Exception('ERROR: arguments x2,y2 passed to midpoint_euclidean() is invalid')

    dist_x = abs(x1-x2) / 2.
    dist_y = abs(y1-y2) / 2.
    res_x = x1 - dist_x if x1 > x2 else x2 - dist_x
    res_y = y1 - dist_y if y1 > y2 else y2 - dist_y
    return [res_x, res_y]


def savvy_get_extreme_lat_long_in_set(coordinates:list=None):
    """
    Finds the most northwest and southeast coordinates from a list of (latitude, longitude) tuples.

    Args:
        coordinates: A list of tuples, where each tuple is (latitude, longitude) in decimal degrees.

    Returns:
        A tuple containing two tuples: (northwest_coordinate, southeast_coordinate).
        Returns (None, None) if the input list is empty.

    Example:
        gps_coords = [
            (34.0522, -118.2437),  # Los Angeles
            (40.7128, -74.0060),   # New York City
            (39.9526, -75.1652),   # Philadelphia
            (37.7749, -122.4194),  # San Francisco
            (33.7490, -84.3880)    # Atlanta
        ]
        northwest_coord, southeast_coord = savvy_get_extreme_lat_long_in_set(gps_coords)
        if northwest_coord and southeast_coord:
            print(f"Most Northwest Coordinate: Latitude {northwest_coord[0]}, Longitude {northwest_coord[1]}")
            print(f"Most Southeast Coordinate: Latitude {southeast_coord[0]}, Longitude {southeast_coord[1]}")
        else:
            print("No coordinates provided.")

    """
    if not coordinates:
        return None, None
    
    for c in coordinates:
        if not isinstance(c, tuple): raise Exception("Argument 'corrdinates' item is not a tuple")

    # Initialize with the first coordinate
    most_north = coordinates[0][0]
    most_west = coordinates[0][1]
    most_south = coordinates[0][0]
    most_east = coordinates[0][1]

    northwest = coordinates[0]
    southeast = coordinates[0]

    for lat, lon in coordinates[1:]:
        if lat > most_north:
            most_north = lat
            northwest = (lat, lon)
        if lon < most_west:
            most_west = lon
            northwest = (lat, lon)
        if lat < most_south:
            most_south = lat
            southeast = (lat, lon)
        if lon > most_east:
            most_east = lon
            southeast = (lat, lon)

    return northwest, southeast


def test_savvy_get_extreme_lat_long_in_set():
    # Example usage:
    gps_coords = [
        (34.0522, -118.2437),  # Los Angeles
        (40.7128, -74.0060),   # New York City
        (39.9526, -75.1652),   # Philadelphia
        (37.7749, -122.4194),  # San Francisco
        (33.7490, -84.3880)    # Atlanta
    ]

    northwest_coord, southeast_coord = savvy_get_extreme_lat_long_in_set(gps_coords)

    if northwest_coord and southeast_coord:
        print(f"Most Northwest Coordinate: Latitude {northwest_coord[0]}, Longitude {northwest_coord[1]}")
        print(f"Most Southeast Coordinate: Latitude {southeast_coord[0]}, Longitude {southeast_coord[1]}")
    else:
        print("No coordinates provided.")


def get_gps_bounding_box(latitude:float=None, longitude:float=None, deg_lat:float=None, deg_lon:float=None, verbose:bool=False):
    """
    Returns a bounding box derived from latitude/longitude deviated by 
    deg_lat and deg_lon as GPS coordinates: n_lat, w_lon, s_lat, e_lon
    All coordinates in decimal degrees. 

    Usage:

    n, w, s, e = get_gps_bounding_box(-88.77425, 37.05635, 1.0, 1.0, False)
    print(f"NorthWest: {n},{w}  SouthEast: {s},{e}")

    Returns:
        n: North latitude (of the northwest corner)
        w: West longitude (of the northwest corner)
        s: South latitude (of the southeast corner)
        e: East longitude (of the southeast corner)

    """
    # lat1 < -90 or lat1 > 90   0 deg @ equator to +90 at N pole
    # lon1 < -180 or lon1 > 180     0 deg at Greenwich to +180 deg E

    import numpy

    #from savvy_gps import lat_lon_is_valid
    if not lat_lon_is_valid(latitude, longitude, True): raise Exception("ERROR: latitude and/or longitude passed to get_gps_bounding_box is invalid")

    if deg_lat < 0: raise Exception("ERROR: deg_lat passed to get_gps_bounding_box is invalid")
    if not isinstance(deg_lat, float): raise Exception("ERROR: deg_lat passed to get_gps_bounding_box is invalid")
    if deg_lon < 0: raise Exception("ERROR: deg_lon passed to get_gps_bounding_box is invalid")
    if not isinstance(deg_lon, float): raise Exception("ERROR: deg_lon passed to get_gps_bounding_box is invalid")

    # Calculate North and South Latitudes
    # The north latitude is latitude + deg_lat, clamped at 90.
    # The south latitude is latitude - deg_lat, clamped at -90.
    n_lat = min(90.0, latitude + deg_lat)
    s_lat = max(-90.0, latitude - deg_lat)

    # Calculate West and East Longitudes
    # This is where the original error was.
    # We need the true westernmost and easternmost points.
    
    # Calculate the two potential longitude boundaries
    lon_left = longitude - deg_lon
    lon_right = longitude + deg_lon

    # Normalize longitudes to the range [-180, 180) for consistent comparison
    # (x + 540) % 360 - 180 handles wrap-around correctly for both positive and negative values
    # For example, -190 becomes 170, 190 becomes -170.
    lon_left_norm = (lon_left + 540) % 360 - 180
    lon_right_norm = (lon_right + 540) % 360 - 180

    # Determine the true westernmost (w_lon) and easternmost (e_lon) longitudes.
    # If lon_left_norm is less than or equal to lon_right_norm, the box does not cross the anti-meridian.
    if lon_left_norm <= lon_right_norm:
        w_lon = lon_left_norm
        e_lon = lon_right_norm
    else:
        # The box crosses the anti-meridian (e.g., from 170 E to -170 W).
        # In this case, the 'western' boundary is the numerically larger value (e.g., 170),
        # and the 'eastern' boundary is the numerically smaller value (e.g., -170).
        w_lon = lon_left_norm
        e_lon = lon_right_norm

    if verbose:
        print(f"Original: {latitude},{longitude}")
        print(f"Calculated: North: {n_lat:.6f}, South: {s_lat:.6f}")
        print(f"            West: {w_lon:.6f}, East: {e_lon:.6f}")
        print(f"Result (n,w,s,e): {n_lat:.6f},{w_lon:.6f}   {s_lat:.6f},{e_lon:.6f}")

    return n_lat, w_lon, s_lat, e_lon


def test_get_gps_bounding_box():

    """
    get_gps_bounding_box(88.0, 178.0, 1.0, 1.0, False)      # 89.0 88.0 87.0   179.0 178.0 177.0
    get_gps_bounding_box(89.0, 179.0, 1.0, 1.0, False)      # 90.0 89.0 88.0   180.0 179.0 178.0
    get_gps_bounding_box(90.0, 180.0, 1.0, 1.0, False)      # 90.0 90.0 89.0   180.0 180.0 179.0
    get_gps_bounding_box(-88.0, -178.0, 1.0, 1.0, False)    # -87.0 -88.0 -89.0        -177.0 -178.0 -179.0
    get_gps_bounding_box(-89.0, -179.0, 1.0, 1.0, False)    # -90.0 -89.0 -88.0        -180.0 -179.0 -178.0
    get_gps_bounding_box(-90.0, -180.0, 1.0, 1.0, False)    # -90.0 -90.0 -89.0        -180.0 -180.0 -179.0
    get_gps_bounding_box(0.0, 0.0, 1.0, 1.0, False)         # 1.0 0.0 -1.0     1.0 0.0 -1.0
    get_gps_bounding_box(1.0, 1.0, 1.0, 1.0, False)         # 2.0 1.0 0.0      2.0 1.0 0.0
    get_gps_bounding_box(2.0, 2.0, 1.0, 1.0, False)         # 3.0 2.0 1.0      3.0 2.0 1.0
    get_gps_bounding_box(-1.0, -1.0, 1.0, 1.0, False)       # 0.0 -1.0 -2.0    0.0 -1.0 -2.0
    get_gps_bounding_box(-2.0, -2.0, 1.0, 1.0, False)       # -1.0 -2.0 -3.0   -1.0 -2.0 -3.0            
    """
    # n, e, s, w

    def generate_map_for_bounding_box(nw_lat, nw_lon, se_lat, se_lon, filename:str=None):
        # pip install folium
        import folium
        from pathlib import Path

        # Define the map file to save
        path_file_map = Path(Path.cwd()).joinpath(filename)
        if path_file_map.is_file(): path_file_map.unlink()

        # Folium's Rectangle expects the bounds as [[southwest_lat, southwest_lon], [northeast_lat, northeast_lon]]
        # So, we need to extract the min/max latitudes and longitudes
        min_lat = min(nw_lat, se_lat)
        max_lat = max(nw_lat, se_lat)
        min_lon = min(nw_lon, se_lon)
        max_lon = max(nw_lon, se_lon)

        # The bounds for folium.Rectangle should be [[southwest_latitude, southwest_longitude], [northeast_latitude, northeast_longitude]]
        # Therefore, southwest corner is (min_lat, min_lon)
        # And northeast corner is (max_lat, max_lon)
        bounds = [[min_lat, min_lon], [max_lat, max_lon]]

        # Create a map centered roughly within the bounding box
        center_lat = (nw_lat + se_lat) / 2
        center_lon = (nw_lon + se_lon) / 2

        m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        # Add the bounding box (rectangle) to the map
        folium.Rectangle(
            bounds=bounds,
            color="blue",  # Color of the border
            weight=3,      # Thickness of the border
            fill=True,
            fill_color="red",  # Fill color of the rectangle
            fill_opacity=0.2,  # Opacity of the fill
            popup="My Bounding Box",
            tooltip="This is a bounding box"
        ).add_to(m)

        # Optional: Add markers for the northwest and southeast corners to confirm
        folium.Marker(
            location=[nw_lat, nw_lon],
            popup="Northwest Corner",
            icon=folium.Icon(color='green')
        ).add_to(m)

        folium.Marker(
            location=[se_lat, se_lon],
            popup="Southeast Corner",
            icon=folium.Icon(color='purple')
        ).add_to(m)

        # Fit the map to the bounds of the rectangle
        # This will automatically set the zoom level to show the entire rectangle
        m.fit_bounds(bounds)

        # Save the map to an HTML file
        m.save(path_file_map)

        print(f"Map saved to {path_file_map}")

        return path_file_map


    def show_map_in_browser(path_file:Path=None):
        import webbrowser
        import os

        import subprocess # New import
        import time # To give some time for processes to start

        # --- Launch the HTML file in Chrome ---
        # Your exact Chrome executable path
        chrome_executable_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        # Ensure the path is correct and accessible
        if not os.path.exists(chrome_executable_path):
            print(f"ERROR: Chrome executable not found at: {chrome_executable_path}")
            print("Please double-check the path. It must be exact.")
        else:
            try:
                # Construct the command to open the HTML file with Chrome
                # The file path needs to be prefixed with 'file://' and be a URL
                file_url = f'file:///{str(path_file)}'
                # Convert backslashes to forward slashes for URL
                file_url = file_url.replace("\\", "/")
                print(f"file_url: {file_url}")

                # Use subprocess.Popen to launch Chrome
                # shell=True can be convenient but is less secure; for simple launches like this it's usually fine.
                # If issues, try shell=False and pass command as a list: [chrome_executable_path, file_url]
                subprocess.Popen([chrome_executable_path, file_url], shell=False)

                print(f"Attempted to launch Chrome: {chrome_executable_path}")
                print(f"Opening URL: {file_url}")

                # Give the browser a moment to open
                time.sleep(1)

            except FileNotFoundError:
                print(f"Error: Chrome executable not found at '{chrome_executable_path}'.")
                print("Please verify the path.")
            except Exception as e:
                print(f"An unexpected error occurred while trying to launch Chrome: {e}")



    coords = [
        [40.44077, -76.12267, "16 Solly Ln"],
        [50.11564, 8.67088, "Frankfurt, Germany"],
        [-22.20867, 23.33384, "Botswana, Africa"],
        [-23.28083, -58.22808, "Paraguay"],
        [-23.69801, 133.88137, "Alice Springs, Northern Territory 0870, Australia"],
    ]


    coord = coords[0]
    latitude = coord[0]
    longitude = coord[1]
    
    nw_lat, nw_lon, se_lat, se_lon = get_gps_bounding_box(latitude, longitude, 1.0, 1.0, False)

    dist_m = haversine_distance(nw_lat, nw_lon, se_lat, se_lon)
    
    print(f"{round(dist_m/1609,3)} mi between {nw_lat},{nw_lon} & {se_lat},{se_lon}")
    
    # Plot the bounding box
    # Define the HTML filename for the map
    filename = "ex_map_bounding_box.html"
    path_file_map = generate_map_for_bounding_box(nw_lat, nw_lon, se_lat, se_lon, filename)

    # Show the map in the default browser
    show_map_in_browser(path_file_map)

    return None

    i = 0
    for coord in coords:
        #coord = coords[4]
        latitude = coord[0]
        longitude = coord[1]
        n, w, s, e = get_gps_bounding_box(latitude, longitude, 0.5, 0.5, False)
        print(round(n,5),round(w,5), round(s,5), round(e,5))   
        # Plot the bounding box
        # Define the HTML filename for the map
        filename = "ex_map_bounding_box" + str(i) + ".html"
        path_file_map = generate_map_for_bounding_box(n, w, s, e, filename)

        # Show the map in the default browser
        show_map_in_browser(path_file_map)

        i += 1


def elevation_by_lat_lon(lat1, lon1):
    """
    Returns the elevation in meters for the specified latitude/longitude, or None
    if the service could not determine the elevation. 

    Uses Google Maps API for elevation, or Open-Elevation if no result.  

    Open-Elevation
    website: https://open-elevation.com/
    docs: https://github.com/Jorl17/open-elevation/blob/master/docs/api.md
    endpoint: curl 'https://api.open-elevation.com/api/v1/lookup?locations=10,10|20,20|41.161758,-8.583933'

    Other API alternatives:
        TessaDEM (https://tessadem.com/) has a free API.  
        GPXZ API is free at 100 requests per day, otherwised $49/mo.  https://www.gpxz.io/#pricing

    """

    # elevation_by_lat_lon()
    """
    elevation_m = elevation_by_lat_lon(38.5288, -78.4383)
    print('Elevation for 38.5288, -78.4383: ', elevation_m, 'meters')
    """

    if not lat_lon_is_valid(lat1, lon1, True): raise Exception('ERROR: invalid arguments passed to elevation_by_lat_lon()')

    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    # Try using Google Maps API for elevation
    url = "https://maps.googleapis.com/maps/api/elevation/json?locations=" + str(lat1) + "," + str(lon1) + "&" + "key" + "=" + os.getenv('GOOGLE_MAPS_API_KEY') + ""
    resp = None
    #sleep(randint(1,3))     # random pause between 1 and 3 seconds
    try:
        resp = requests.get(url).json() 
    except Exception as e:
        print('ERROR: ' + repr(e), url)

    if resp is None:
        print('maps.googleapis.com failed.  Trying api.open-elevation.com..')
        url = 'https://api.open-elevation.com/api/v1/lookup?locations=' + str(lat1) + ',' + str(lon1)
        sleep(randint(2,5))     # random pause between 2 and 5 seconds
        try:
            resp = requests.get(url).json() 
        except Exception as e:
            print('ERROR: ' + repr(e), url)

    #print(json.dumps(data, sort_keys=True, indent=2))
    """
    api.open-elevation.com
    {
    "results": [
        {
        "elevation": 1093.0,
        "latitude": 38.5288,
        "longitude": -78.4383
        }
    ]
    }

    maps.googleapis.com
    {
    "results" : [
        {
            "elevation" : 101,
            "location" : {
                "lat" : 41.161758,
                "lng" : -8.583933
            },
            "resolution" : 9.543951988220215
        }
    ],
    "status" : "OK"
    }
    """
    if not 'results' in resp.keys(): 
        print(json.dumps(resp, sort_keys=True, indent=2))
        return None
    if len(resp['results']) == 0:
        print(json.dumps(resp, sort_keys=True, indent=2))
        return None
    results = resp['results'][0]
    if not 'elevation' in results.keys(): return None
    elevation = float(results['elevation'])
    return elevation


def get_lat_lon_by_address(**kwargs):
    """
    Returns latitude & longitude for country, state, lat, lon as a dictionary usiing Google Maps API

    Google Maps API: 
    https://developers.google.com/maps/documentation/geocoding/start
    https://www.w3resource.com/python-exercises/web-scraping/web-scraping-exercise-4.php
    
    Difficult address: 501 South Abbott Street, Marfa, TX, 79843
    address=501+South+Abbott+Street,+Marfa,+TX,+79843

    Example:

    lat_lon = get_lat_lon_by_address(address='501 South Abbott Street, Marfa, TX, 79843')
    print('latitude: ', lat_lon['latitude'], '\tlongitude:', lat_lon['longitude'])

    lat_lon = get_lat_lon_by_address(street="501 South Abbott Street",city="Marfa",state="TX",zip="79843",country="US")
    print('latitude: ', lat_lon['latitude'], '\tlongitude:', lat_lon['longitude'])

    """

    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    url = "https://maps.googleapis.com/maps/api/geocode/json?" + "key" + "=" + os.getenv('GOOGLE_MAPS_API_KEY') + ""

    if 'address' in kwargs:
        addr = {'address': kwargs['address'], 'language': 'en'}
        resp = requests.get(url, params=addr).json() 
    else:
        s = ''
        for item in kwargs:
            s += kwargs[item] + ','
        s = s.rstrip(s[-1])
        addr = {'address': s, 'language': 'en'}
        resp = requests.get(url, params=addr).json() 

    #print(json.dumps(resp, sort_keys=False, indent=2))

    # Method below works too
    #url = 'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=os.getenv('GOOGLE_MAPS_API_KEY')'
    #url = 'https://maps.googleapis.com/maps/api/geocode/json?address=501+South+Abbott+Street,+Marfa,+TX,+79843&key=os.getenv('GOOGLE_MAPS_API_KEY')'
    #resp = requests.get(url).json() 
    #print(json.dumps(resp, sort_keys=False, indent=2))
    """
    {
    "results": [
        {
        "address_components": [
            {
            "long_name": "501",
            "short_name": "501",
            "types": [
                "street_number"
            ]
            },
            {
            "long_name": "South Abbot Street",
            "short_name": "S Abbot St",
            "types": [
                "route"
            ]
            },
            {
            "long_name": "Marfa",
            "short_name": "Marfa",
            "types": [
                "locality",
                "political"
            ]
            },
            {
            "long_name": "Presidio County",
            "short_name": "Presidio County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
            },
            {
            "long_name": "Texas",
            "short_name": "TX",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            },
            {
            "long_name": "79843",
            "short_name": "79843",
            "types": [
                "postal_code"
            ]
            }
        ],
        "formatted_address": "501 S Abbot St, Marfa, TX 79843, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 30.3059217,
                "lng": -104.0222882
            },
            "southwest": {
                "lat": 30.3056907,
                "lng": -104.0225915
            }
            },
            "location": {
            "lat": 30.3058196,
            "lng": -104.0224489
            },
            "location_type": "ROOFTOP",
            "viewport": {
            "northeast": {
                "lat": 30.3071551802915,
                "lng": -104.0209820697085
            },
            "southwest": {
                "lat": 30.3044572197085,
                "lng": -104.0236800302915
            }
            }
        },
        "place_id": "ChIJU7CpIruw74YRBGGWDNkMVd8",
        "types": [
            "premise"
        ]
        }
    ],
    "status": "OK"
    }    """
    status = resp['status']
    if status != 'OK': return None
    results = resp['results'][0]
    formatted_address = results['formatted_address']
    place_id = results['place_id']
    geometry = results['geometry']
    location = geometry['location']
    rtn_dic = {'latitude': location['lat'], 'longitude': location['lng']}
    return rtn_dic


def get_address_by_lat_lon(latitude, longitude, verbose=False):
    """
    Returns a dictionary with keys formatted_address, name, addr, state, zip, county, country
    for the supplied latitude & longitude using Google Maps API

    Google Maps API: os.getenv('GOOGLE_MAPS_API_KEY')
    https://developers.google.com/maps/documentation/geocoding/start
    https://www.w3resource.com/python-exercises/web-scraping/web-scraping-exercise-4.php
    Endpoint: https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=YOUR_API_KEY
    

    Usage:

    addr = get_address_by_lat_lon(37.82676234, -122.4230206, False)
    #formatted_address, name, addr, state, zip, county, country
    print(addr['formatted_address'])

    """

    if verbose: print("get_address_by_lat_lon()")

    if not lat_lon_is_valid(latitude, longitude, False):
        print("ERROR: latitude and/or longitude is invalid", latitude, longitude)
        return {}

    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    # Endpoint: https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.961452&key=YOUR_API_KEY
    url = "https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(latitude) + "," + str(longitude) + "&" + "key" + "=" + os.getenv('GOOGLE_MAPS_API_KEY') + ""
    if verbose: print(url)

    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9"})   # Optionally add an API key, etc.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #sleep(randint(0,3))     # random pause between 0 and 3 seconds
    try:
        req = requests.get(url, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), 'get_nps_count_parks()', url)
        return None
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        return None

    resp = req.json()
    if len(resp) == 0:
        print("\tNo results from query ", url)
        return None
    
    #print(json.dumps(resp, sort_keys=False, indent=2))

    # Method below works too
    #url = 'https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=os.getenv('GOOGLE_MAPS_API_KEY')'
    #url = 'https://maps.googleapis.com/maps/api/geocode/json?address=501+South+Abbott+Street,+Marfa,+TX,+79843&key=os.getenv('GOOGLE_MAPS_API_KEY')'
    #resp = requests.get(url).json() 
    #print(json.dumps(resp, sort_keys=False, indent=2))
    """
    {
    "plus_code": {
        "compound_code": "RHGG+PQ5 Belvedere Tiburon, Tiburon, CA, USA",
        "global_code": "849VRHGG+PQ5"
    },
    "results": [
        {
        "address_components": [
            {
            "long_name": "Alcatraz Main Cell House",
            "short_name": "Alcatraz Main Cell House",
            "types": [
                "premise"
            ]
            },
            {
            "long_name": "Pier 39",
            "short_name": "Pier 39",
            "types": [
                "route"
            ]
            },
            {
            "long_name": "San Francisco",
            "short_name": "SF",
            "types": [
                "locality",
                "political"
            ]
            },
            {
            "long_name": "San Francisco County",
            "short_name": "San Francisco County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
            },
            {
            "long_name": "California",
            "short_name": "CA",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            },
            {
            "long_name": "94133",
            "short_name": "94133",
            "types": [
                "postal_code"
            ]
            }
        ],
        "formatted_address": "Alcatraz Main Cell House, Pier 39, San Francisco, CA 94133, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 37.8274373,
                "lng": -122.4222463
            },
            "southwest": {
                "lat": 37.8262294,
                "lng": -122.4241263
            }
            },
            "location": {
            "lat": 37.8266165,
            "lng": -122.4229237
            },
            "location_type": "ROOFTOP",
            "viewport": {
            "northeast": {
                "lat": 37.8281823302915,
                "lng": -122.4218373197085
            },
            "southwest": {
                "lat": 37.82548436970851,
                "lng": -122.4245352802915
            }
            }
        },
        "place_id": "ChIJHTR2bBWBhYAR_xgjuMyzrG8",
        "types": [
            "premise"
        ]
        },
        {
        "address_components": [
            {
            "long_name": "RHGG+PQ",
            "short_name": "RHGG+PQ",
            "types": [
                "plus_code"
            ]
            },
            {
            "long_name": "Belvedere Tiburon",
            "short_name": "Belvedere Tiburon",
            "types": [
                "neighborhood",
                "political"
            ]
            },
            {
            "long_name": "Tiburon",
            "short_name": "Tiburon",
            "types": [
                "locality",
                "political"
            ]
            },
            {
            "long_name": "Marin County",
            "short_name": "Marin County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
            },
            {
            "long_name": "California",
            "short_name": "CA",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            }
        ],
        "formatted_address": "RHGG+PQ Belvedere Tiburon, Tiburon, CA, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 37.826875,
                "lng": -122.423
            },
            "southwest": {
                "lat": 37.82675,
                "lng": -122.423125
            }
            },
            "location": {
            "lat": 37.82676230000001,
            "lng": -122.4230206
            },
            "location_type": "GEOMETRIC_CENTER",
            "viewport": {
            "northeast": {
                "lat": 37.82816148029151,
                "lng": -122.4217135197085
            },
            "southwest": {
                "lat": 37.82546351970851,
                "lng": -122.4244114802915
            }
            }
        },
        "place_id": "GhIJawjYWNPpQkARM6L-xBKbXsA",
        "plus_code": {
            "compound_code": "RHGG+PQ Belvedere Tiburon, Tiburon, CA, USA",
            "global_code": "849VRHGG+PQ"
        },
        "types": [
            "plus_code"
        ]
        },
        {
        "address_components": [
            {
            "long_name": "Unnamed Road",
            "short_name": "Unnamed Road",
            "types": [
                "route"
            ]
            },
            {
            "long_name": "San Francisco",
            "short_name": "SF",
            "types": [
                "locality",
                "political"
            ]
            },
            {
            "long_name": "San Francisco County",
            "short_name": "San Francisco County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
            },
            {
            "long_name": "California",
            "short_name": "CA",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            },
            {
            "long_name": "94133",
            "short_name": "94133",
            "types": [
                "postal_code"
            ]
            }
        ],
        "formatted_address": "Unnamed Road, San Francisco, CA 94133, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 37.8268541,
                "lng": -122.4232275
            },
            "southwest": {
                "lat": 37.8267706,
                "lng": -122.4233437
            }
            },
            "location": {
            "lat": 37.8268138,
            "lng": -122.4232842
            },
            "location_type": "GEOMETRIC_CENTER",
            "viewport": {
            "northeast": {
                "lat": 37.82816133029149,
                "lng": -122.4219366197085
            },
            "southwest": {
                "lat": 37.82546336970849,
                "lng": -122.4246345802915
            }
            }
        },
        "place_id": "ChIJ-QEMaBWBhYARLu04iHSpAIs",
        "types": [
            "route"
        ]
        },
        {
        "address_components": [
            {
            "long_name": "94133",
            "short_name": "94133",
            "types": [
                "postal_code"
            ]
            },
            {
            "long_name": "San Francisco",
            "short_name": "SF",
            "types": [
                "locality",
                "political"
            ]
            },
            {
            "long_name": "San Francisco County",
            "short_name": "San Francisco County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
            },
            {
            "long_name": "California",
            "short_name": "CA",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            }
        ],
        "formatted_address": "San Francisco, CA 94133, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 37.863203,
                "lng": -122.392499
            },
            "southwest": {
                "lat": 37.793769,
                "lng": -122.4256409
            }
            },
            "location": {
            "lat": 37.8059887,
            "lng": -122.4099154
            },
            "location_type": "APPROXIMATE",
            "viewport": {
            "northeast": {
                "lat": 37.863203,
                "lng": -122.392499
            },
            "southwest": {
                "lat": 37.793769,
                "lng": -122.4256409
            }
            }
        },
        "place_id": "ChIJ61hhQeGAhYARo_x_aAlCar8",
        "types": [
            "postal_code"
        ]
        },
        {
        "address_components": [
            {
            "long_name": "San Francisco",
            "short_name": "SF",
            "types": [
                "locality",
                "political"
            ]
            },
            {
            "long_name": "San Francisco County",
            "short_name": "San Francisco County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
            },
            {
            "long_name": "California",
            "short_name": "CA",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            }
        ],
        "formatted_address": "San Francisco, CA, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 37.9298239,
                "lng": -122.28178
            },
            "southwest": {
                "lat": 37.6398299,
                "lng": -123.1328309
            }
            },
            "location": {
            "lat": 37.7749295,
            "lng": -122.4194155
            },
            "location_type": "APPROXIMATE",
            "viewport": {
            "northeast": {
                "lat": 37.9298239,
                "lng": -122.28178
            },
            "southwest": {
                "lat": 37.6398299,
                "lng": -123.1328309
            }
            }
        },
        "place_id": "ChIJIQBpAG2ahYAR_6128GcTUEo",
        "types": [
            "locality",
            "political"
        ]
        },
        {
        "address_components": [
            {
            "long_name": "San Francisco County",
            "short_name": "San Francisco County",
            "types": [
                "administrative_area_level_2",
                "political"
            ]
            },
            {
            "long_name": "San Francisco",
            "short_name": "SF",
            "types": [
                "locality",
                "political"
            ]
            },
            {
            "long_name": "California",
            "short_name": "CA",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            }
        ],
        "formatted_address": "San Francisco County, San Francisco, CA, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 37.929824,
                "lng": -122.28178
            },
            "southwest": {
                "lat": 37.63983,
                "lng": -123.1328309
            }
            },
            "location": {
            "lat": 37.7618219,
            "lng": -122.5146439
            },
            "location_type": "APPROXIMATE",
            "viewport": {
            "northeast": {
                "lat": 37.929824,
                "lng": -122.28178
            },
            "southwest": {
                "lat": 37.63983,
                "lng": -123.1328309
            }
            }
        },
        "place_id": "ChIJIQBpAG2ahYARUksNqd0_1h8",
        "types": [
            "administrative_area_level_2",
            "political"
        ]
        },
        {
        "address_components": [
            {
            "long_name": "California",
            "short_name": "CA",
            "types": [
                "administrative_area_level_1",
                "political"
            ]
            },
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            }
        ],
        "formatted_address": "California, USA",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 42.009503,
                "lng": -114.131211
            },
            "southwest": {
                "lat": 32.528832,
                "lng": -124.482003
            }
            },
            "location": {
            "lat": 36.778261,
            "lng": -119.4179324
            },
            "location_type": "APPROXIMATE",
            "viewport": {
            "northeast": {
                "lat": 42.009503,
                "lng": -114.131211
            },
            "southwest": {
                "lat": 32.528832,
                "lng": -124.482003
            }
            }
        },
        "place_id": "ChIJPV4oX_65j4ARVW8IJ6IJUYs",
        "types": [
            "administrative_area_level_1",
            "political"
        ]
        },
        {
        "address_components": [
            {
            "long_name": "United States",
            "short_name": "US",
            "types": [
                "country",
                "political"
            ]
            }
        ],
        "formatted_address": "United States",
        "geometry": {
            "bounds": {
            "northeast": {
                "lat": 74.071038,
                "lng": -66.885417
            },
            "southwest": {
                "lat": 18.7763,
                "lng": 166.9999999
            }
            },
            "location": {
            "lat": 37.09024,
            "lng": -95.712891
            },
            "location_type": "APPROXIMATE",
            "viewport": {
            "northeast": {
                "lat": 74.071038,
                "lng": -66.885417
            },
            "southwest": {
                "lat": 18.7763,
                "lng": 166.9999999
            }
            }
        },
        "place_id": "ChIJCzYy5IS16lQRQrfeQ5K5Oxw",
        "types": [
            "country",
            "political"
        ]
        }
    ],
    "status": "OK"
    }
    """
        #if 'data' in resp.keys():
    if not 'results' in resp.keys():
        raise Exception("ERROR: key 'results' not in resp.keys()")
    if not 'status' in resp.keys():
        raise Exception("ERROR: key 'status' not in resp.keys()")
    status = resp['status']
    if status != 'OK': return None
    #print("len(results) = " , len(resp['results']))     # 8
    results = resp['results'][0]
    if not 'formatted_address' in results.keys():
        raise Exception("ERROR: key 'formatted_address' not in resp.keys()")
    formatted_address = results['formatted_address']
    if not 'address_components' in results.keys():
        raise Exception("ERROR: key 'address_components' not in resp.keys()")
    address_components = results['address_components']
    if len(address_components) == 7:
        name = address_components[0]['long_name']
        addr = address_components[1]['long_name']
        state = address_components[2]['short_name']
        county = address_components[3]['long_name']
        country = address_components[4]['short_name']
        zip = address_components[5]['long_name']
        rtn_dic = {
            'formatted_address': formatted_address,
            'name': name,
            'addr': addr,
            'state': state,
            'zip': zip,
            'county': county,
            'country': country
        }
        return rtn_dic      #formatted_address, name, addr, state, zip, county, country
    else:
        return {'formatted_address': formatted_address}


def get_place_address(place:str="", verbose:bool=False):
    """
    Returns returns a dictionary using Google Maps AP for the 'place' with keys:
        full_address, street, city, state, zip, country, latitude, longitude

    Returns None if nothing found for place. 

    Google Maps API: os.getenv('GOOGLE_MAPS_API_KEY')

    https://developers.google.com/maps/documentation/places/web-service/search-find-place#maps_http_places_findplacefromtext_phonenumber-txt
    
    Usage:

    data = get_place_address("Ozark Mountains", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     # {'name': 'Ouachita Mountains', 'state': 'OK', 'country': 'US', 'zip': '74957', 'latitude': 34.50039179999999, 'longitude': -94.5004891}
    
    data = get_place_address("Adirondack Mountains", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     # {'name': 'Ouachita Mountains', 'state': 'OK', 'country': 'US', 'zip': '74957', 'latitude': 34.50039179999999, 'longitude': -94.5004891}

    data = get_place_address("Ouachita Mountains", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     # {'name': 'Ouachita Mountains', 'state': 'OK', 'country': 'US', 'zip': '74957', 'latitude': 34.50039179999999, 'longitude': -94.5004891}
    
    data = get_place_address("Big Bear Lake", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     # {'name': 'Ouachita Mountains', 'state': 'OK', 'country': 'US', 'zip': '74957', 'latitude': 34.50039179999999, 'longitude': -94.5004891}

    data = get_place_address("White Mountains", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     # {'name': 'Ouachita Mountains', 'state': 'OK', 'country': 'US', 'zip': '74957', 'latitude': 34.50039179999999, 'longitude': -94.5004891}

    data = get_place_address("idontexist", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     # {'name': 'Ouachita Mountains', 'state': 'OK', 'country': 'US', 'zip': '74957', 'latitude': 34.50039179999999, 'longitude': -94.5004891}

    """

    # usaddress is a Python library for parsing
    # https://pypi.org/project/usaddress/
    # Possibly a better solution using usaddress:  https://github.com/datamade/usaddress
    # pip install usaddress
    import usaddress


    if len(place) == 0:
        raise Exception('ERROR: argument place has a length of zero')
    
    #place = urllib.parse.quote(place)
    #print(place)

    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    #url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=mongolian&inputtype=textquery&locationbias=circle%3A2000%4047.6918452%2C-122.2226413&fields=formatted_address%2Cname%2Crating%2Copening_hours%2Cgeometry&key=os.getenv('GOOGLE_MAPS_API_KEY')"
    #url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + urllib.parse.quote(place) + "&inputtype=textquery&fields=formatted_address%2Cgeometry&key=os.getenv('GOOGLE_MAPS_API_KEY')"
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + urllib.parse.quote(place) + "&inputtype=textquery&fields=formatted_address%2Cgeometry&" + "key" + "=" + os.getenv('GOOGLE_MAPS_API_KEY') + ""
    if verbose: print(url)

    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9"})   # Optionally add an API key, etc.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #sleep(randint(0,3))     # random pause between 0 and 3 seconds
    try:
        req = requests.get(url, data=None, json=None, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), ' fn()', url)
        return None
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        return None

    resp = req.json()
    if len(resp) == 0:
        if verbose: print("\tNo results from query ", url)
        return None
    if verbose: print(json.dumps(resp, sort_keys=False, indent=2))
    #if 'data' in resp.keys():

    """
    {
    "candidates" : [
        {
            "formatted_address" : "White Mountains, Lincoln, NH 03251, USA",
            "geometry" : {
                "location" : {
                "lat" : 44.16438040000001,
                "lng" : -71.4325573
                },
                "viewport" : {
                "northeast" : {
                    "lat" : 44.172384,
                    "lng" : -71.41654989999999
                },
                "southwest" : {
                    "lat" : 44.1563757,
                    "lng" : -71.44856469999999
                }
                }
            }
        }
    ],
    "status" : "OK"
    }
    """

    if not 'status' in resp.keys():
        raise Exception("ERROR: key 'status' missing from response.   get_place_address()")
    status = resp['status']
    if status == "ZERO_RESULTS":
        print("NO RESULTS found for '" + place + "' by get_place_address()")
        return None
    elif not status == "OK":
        print(json.dumps(resp, sort_keys=False, indent=2))
        raise Exception("ERROR: status of '" + status + "' is not 'OK'.   get_place_address()")
    if not 'candidates' in resp.keys():
        raise Exception("ERROR: key 'candidates' missing from response.   get_place_address()")
    candidates = resp['candidates']
    if verbose: print(len(candidates), " candidates found.")
    candidate = candidates[0]
    
    if not 'formatted_address' in candidate.keys():
        raise Exception("ERROR: key 'formatted_address' missing from response.   get_place_address()")
    formatted_address = candidate['formatted_address']
    if verbose: print("formatted_address = ", formatted_address)

    if not 'geometry' in candidate.keys(): raise Exception("ERROR: key 'geometry' missing from response.   get_place_address()")
    geometry = candidate['geometry']
    if not 'location' in geometry.keys(): raise Exception("ERROR: key 'location' missing from response.   get_place_address()")
    location = geometry['location']
    if not 'lat' in location.keys() or not 'lng' in location.keys(): raise Exception("ERROR: key 'lat' and/or 'lng' missing from response.  get_place_address()")
    latitude = float(location['lat'])
    longitude = float(location['lng'])
    if verbose: print(latitude,longitude)

    usa_country_names = ["United States"]
    usa_country_name_abbreviations = ["US", "USA", "U.S.", "U.S.A."]
    state2abbrev = {
        'Alaska': 'AK',
        'Alabama': 'AL',
        'Arkansas': 'AR',
        'Arizona': 'AZ',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'District of Columbia': 'DC',
        'Delaware': 'DE',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Hawaii': 'HI',
        'Iowa': 'IA',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Massachusetts': 'MA',
        'Maryland': 'MD',
        'Maine': 'ME',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Missouri': 'MO',
        'Mississippi': 'MS',
        'Montana': 'MT',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Nebraska': 'NE',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'Nevada': 'NV',
        'New York': 'NY',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT', 
        'Virginia': 'VA',
        'Vermont': 'VT', 
        'Washington': 'WA',
        'Wisconsin': 'WI',
        'West Virginia': 'WV',
        'Wyoming': 'WY'
    }

    city = None
    state = None
    zip_code = None
    country = "US"
    if usaddress.tag(formatted_address)[1] == "Street Address" or usaddress.tag(formatted_address)[1] == "PO Box":
        #print("Street Address:")
        usaddress_dic = usaddress.tag(formatted_address)[0]
        if 'PlaceName' in usaddress_dic.keys(): city = usaddress_dic['PlaceName']
        if 'StateName' in usaddress_dic.keys(): state = usaddress_dic['StateName']
        if 'ZipCode' in usaddress_dic.keys(): zip_code = usaddress_dic['ZipCode']
        #if 'CountryName' in usaddress_dic.keys(): country = usaddress_dic['CountryName']
    elif usaddress.tag(formatted_address)[1] == "Ambiguous":
        #print("Ambiguous:")
        # (OrderedDict([('StreetName', 'Adirondack'), 
        #               ('StreetNamePostType', 'Mountains')
        #              ]), 
        #              'Ambiguous')
        usaddress_dic = usaddress.tag(formatted_address)[0]
        # Watch for:    'PlaceName', 'California'
        #               'StateName', 'USA')
        #               'StateName', 'CA, USA'
        #               (OrderedDict([('Recipient', 'Ozark Mountains, United States')]), 'Ambiguous')
        if 'StateName' in usaddress_dic.keys(): 
            #print("StateName: ", usaddress_dic['StateName'])
            if str(usaddress_dic['StateName']) == "Mexico":
                state = "NM"
            elif str(usaddress_dic['StateName']).count(',') == 1: 
                statename = str(usaddress_dic['StateName']).split(",")
                if not len(statename) == 2: raise Exception("ERROR: Unexpected length of " + str(len(statename)) + " for '" + statename + "' ")
                if statename[0].strip() in state2abbrev.keys(): state = state2abbrev[statename[0].strip()]
                if statename[0].strip() in state2abbrev.values(): state = statename[0].strip()
                #if statename[1].strip() in usa_country_name_abbreviations: country = statename[1].strip()
                #if statename[1].strip() in usa_country_names: country = statename[1].strip()
            elif str(usaddress_dic['StateName']).count(',') == 0:
                statename = str(usaddress_dic['StateName']).strip()
                if statename in state2abbrev.keys(): state = state2abbrev[statename]
                if statename in state2abbrev.values(): state = statename
            else:
                raise Exception("ERROR: Unexpected result in statename: '" + str(usaddress_dic['StateName']) + "'")
            if usaddress_dic['StateName'] in state2abbrev.keys(): print(state2abbrev[usaddress_dic['StateName']])
        if 'Recipient' in usaddress_dic.keys(): 
            recipient = str(usaddress_dic['Recipient']).strip()
            #print("recipient: ", recipient)
            if recipient.count(',') == 1: 
                statename = recipient.split(",")
                if not len(statename) == 2: raise Exception("ERROR: Unexpected length of " + str(len(statename)) + " for '" + statename + "' derived from recipient")
                if statename[0].strip() in state2abbrev.keys(): state = state2abbrev[statename[0].strip()]
                if statename[0].strip() in state2abbrev.values(): state = statename[0].strip()
            elif recipient.count(',') == 0:
                if recipient in state2abbrev.keys() and state is None: state = state2abbrev[recipient]
                if recipient in state2abbrev.values() and state is None: state = recipient
        if 'ZipCode' in usaddress_dic.keys(): zip_code = usaddress_dic['ZipCode']
        if 'PlaceName' in usaddress_dic.keys(): 
            placename = str(usaddress_dic['PlaceName']).strip()
            # placename could be a city name, state name, country name
            if placename == "New":
                placename = None
            elif placename.count(',') == 0:
                if not placename in state2abbrev.keys() and not placename in state2abbrev.values(): 
                    city = placename
                elif state is None and placename in state2abbrev.keys():
                    state = state2abbrev[placename]
                elif state is None and placename in state2abbrev.values():
                    state = placename
        #if 'CountryName' in usaddress_dic.keys(): print("CountryName: ", usaddress_dic['CountryName'])
        # (OrderedDict([('LandmarkName', 'Johnson Hill'), ('PlaceName', 'New'), ('StateName', 'Mexico'), ('ZipCode', '87823'), ('CountryName', 'United States')]), 'Ambiguous')
        if 'BuildingName' in usaddress_dic.keys():
            building_name = str(usaddress_dic['BuildingName']).strip()
            #print("building_name: ", building_name)     # Appalachian National Scenic Trail, Harpers Ferry, West Virginia 25425
            if building_name.count(",") > 0:
                building_names = building_name.split(",")
                for building_name in building_names:
                    building_name = building_name.strip()
                    # Need to handle the case of "West Virginia #####" and "New Mexico #####"
                    if building_name in state2abbrev.keys() and state is None: state = state2abbrev[building_name]
                    if building_name in state2abbrev.values() and state is None: state = building_name

    elif usaddress.tag(formatted_address)[1] == "Intersection":
        # (OrderedDict([('StreetName', 'Fish'), ('IntersectionSeparator', 'and'), ('SecondStreetName', 'Owl'), ('SecondStreetNamePostType', 'Rd'), ('PlaceName', 'Utah, United States')]), 'Intersection')
        usaddress_dic = usaddress.tag(formatted_address)[0]
        if 'PlaceName' in usaddress_dic.keys(): 
            placename = str(usaddress_dic['PlaceName']).strip()
            # placename could be a city name, state name, country name
            if placename.count(',') == 0:
                if not placename in state2abbrev.keys() and not placename in state2abbrev.values(): 
                    city = placename
                elif state is None and placename in state2abbrev.keys():
                    state = state2abbrev[placename]
                elif state is None and placename in state2abbrev.values():
                    state = placename
            elif placename.count(',') == 1: 
                placename = placename.split(",")
                if not len(placename) == 2: raise Exception("ERROR: Unexpected length of " + str(len(placename)) + " for '" + placename + "' ")
                if placename[0].strip() in state2abbrev.keys(): state = state2abbrev[placename[0].strip()]
                if placename[0].strip() in state2abbrev.values(): state = placename[0].strip()
                #if placename[1].strip() in usa_country_name_abbreviations: country = placename[1].strip()
                #if placename[1].strip() in usa_country_names: country = placename[1].strip()
    else:
        print("place: ", place)
        print("formatted_address = ", formatted_address)
        print("usaddress.tag: ", usaddress.tag(formatted_address))
        raise Exception("ERROR unexpected response '" + usaddress.tag(formatted_address)[1] + "' for input to usaddress.tag() of '" + formatted_address + "'")
    #print(str(city) + ", " + str(state), str(zip_code), str(country))

    return {
        'full_address': formatted_address,
        'city': city,
        'state': state,
        'zip': zip_code,
        'country': country,
        'latitude': latitude,
        'longitude': longitude
    }
    # {'full_address': 'White Mountains, Lincoln, NH 03251, USA', 'street': 'White Mountains', 'city': 'Lincoln', 'state': 'NH', 'zip': '03251', 'country': 'USA', 'latitude': 44.16438040000001, 'longitude': -71.4325573}
    # full_address, street, city, state, zip, country, latitude, longitude


def get_place_rating(place, verbose):
    """
    Returns returns a numerical rating (1.0 to 5.0) using Google Maps AP for the 'place'.

    Returns None if nothing found for place. 

    Google Maps API: os.getenv('GOOGLE_MAPS_API_KEY')

    https://developers.google.com/maps/documentation/places/web-service/search-find-place#maps_http_places_findplacefromtext_phonenumber-txt
    
    Usage:

    rating = get_place_rating("Carters Lake", False)
    if rating is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.  get_place_rating()")
    print("Place rating is ", rating)    

    """

    if len(place) == 0:
        raise Exception('ERROR: argument place has a length of zero')
    
    #place = urllib.parse.quote(place)
    #print(place)

    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + urllib.parse.quote(place) + "&inputtype=textquery&fields=rating&" + "key" + "=" + os.getenv('GOOGLE_MAPS_API_KEY') + ""
    if verbose: print(url)

    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9"})   # Optionally add an API key, etc.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #sleep(randint(0,3))     # random pause between 0 and 3 seconds
    try:
        req = requests.get(url, data=None, json=None, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), ' fn()', url)
        return None
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        return None

    resp = req.json()
    if len(resp) == 0:
        print("\tNo results from query ", url)
        return None
    if verbose: print(json.dumps(resp, sort_keys=False, indent=2))
    #if 'data' in resp.keys():

    """
    {
    "candidates": [
        {
        "rating": 4.8
        }
    ],
    "status": "OK"
    }
    """

    if not 'status' in resp.keys():
        raise Exception("ERROR: key 'status' missing from response.   get_place_rating()")
    status = resp['status']
    if status == "ZERO_RESULTS":
        print("NO RESULTS found for '" + place + "' by get_place_rating()")
        return None
    elif status == "OVER_QUERY_LIMIT " or status == 'REQUEST_DENIED':
        raise Exception("ERROR: you exceeded the Google API query limit!   get_place_rating()")
    elif not status == "OK":
        raise Exception("ERROR: status of '" + status + "' is not 'OK'.   get_place_rating()")
    if not 'candidates' in resp.keys():
        raise Exception("ERROR: key 'candidates' missing from response.   get_place_rating()")
    candidates = resp['candidates']
    if verbose: print(len(candidates), " candidates found using get_place_rating()")
    candidate = candidates[0]
    if not 'rating' in candidate.keys(): 
        # This happens if no rating exists for the place, or the place is not recognized.
        #print(json.dumps(resp, sort_keys=False, indent=2))
        #raise Exception("ERROR: key 'rating' missing from response.   get_place_rating()")
        return None
    rating = float(candidate['rating'])
    return rating


# ---------------------------------------------------------------------------------------------------------
# FIPS codes

def get_fips_codes_by_lat_lon_geocodio(lat1:float=None, lon1:float=None, verbose:bool=False):
    """
    Returns FIPS county, state, full codes for lat/lon coordinates and calculates 
    the distance error between the requested lat/lon and the found location using 
    the geocodio API.   
    The returned data is a dictionary with keys:
        'full_fips', 'county_fips', 'state_fips', 'dist_km'

    NOTE: This function acquires considerably more information than get_fips_code_by_lat_lon_fcc(),
    and the FIPS full code us much more accurate, but get_fips_code_by_lat_lon_fcc() is more robust 
    in terms of getting full_fips, county_fips, and state_fips codes. 

    FIPS codes are numbers which uniquely identify geographic areas.
    The longer the number, the more detailed the location identification.
    state level (PA=42), county level(Berks County=42011)
    https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt

    geocodio
    https://www.geocod.io/docs/#overview
    https://www.geocod.io/docs/?shell#census-block-tract-fips-codes-amp-msa-csa-codes
    Note that many other additional fields may be returned from the API. See: https://www.geocod.io/docs/#fields
    """

    import os

    if lat1 is None or lon1 is None: raise Exception("Required arguments lat1/lon1 not passed")

    # Verify the Windows environment variable API_GEOCODIO_KEY is set & demonstrate how to access it.
    if not os.getenv('API_GEOCODIO_KEY'): raise Exception("Windows environment variable 'API_GEOCODIO_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    if verbose: print('get_fips_codes_by_lat_lon_geocodio()..', lat1, lon1)
    rtn_dic = {}
    
    # curl "https://api.geocod.io/v1.8/reverse?q=38.9002898,-76.9990361&api_key=YOUR_API_KEY"
    url = "https://api.geocod.io/v1.7/reverse" + "?q=" + str(lat1) + "," + str(lon1) + "&fields=census&" + "api_key" + "=" + os.getenv('API_GEOCODIO_KEY') + "&limit=1"
    if verbose: print(url)

    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9"})   # Optionally add an API key, etc.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #sleep(randint(1,5))     # random pause between 1 and 5 seconds
    try:
        req = requests.get(url, data=None, json=None, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), 'get_fips_codes_by_lat_lon_geocodio()', "https://api.geocod.io/v1.7/reverse" + "?q=" + str(lat1) + "," + str(lon1) + "&fields=census")
        return rtn_dic
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        return rtn_dic

    resp = req.json()
    if len(resp) == 0:
        # This is the primary indicator when api.geocod.io fails to reverse geocode lat1,lon1
        # data: {"results": []}
        if verbose: print('\tapi.geocod.io failed to reverse geocode ', lat1, ',', lon1)
        return rtn_dic
    #print(json.dumps(resp, sort_keys=False, indent=2))

    #print(json.dumps(data, sort_keys=False, indent=2))
    """
    {
    "results": [
        {
        "accuracy": 1,
        "accuracy_type": "rooftop",
        "address_components": {
            "city": "Madison",
            "country": "US",
            "county": "Madison County",
            "formatted_street": "Big Meadows Access Rd",
            "number": "304",
            "state": "VA",
            "street": "Big Meadows Access",
            "suffix": "Rd",
            "zip": "22727"
        },
        "fields": {
            "census": {
            "2022": {
                "block_code": "1080",
                "block_group": "1",
                "census_year": 2022,
                "combined_statistical_area": {
                "area_code": "548",
                "name": "Washington-Baltimore-Arlington, DC-MD-VA-WV-PA"
                },
                "county_fips": "51113",
                "full_fips": "511139302021080",
                "metro_micro_statistical_area": {
                "area_code": "47900",
                "name": "Washington-Arlington-Alexandria, DC-VA-MD-WV",
                "type": "metropolitan"
                },
                "metropolitan_division": {
                "area_code": "47894",
                "name": "Washington-Arlington-Alexandria, DC-VA-MD-WV"
                },
                "place": null,
                "source": "US Census Bureau",
                "state_fips": "51",
                "tract_code": "930202"
            }
            }
        },
        "formatted_address": "304 Big Meadows Access Rd, Madison, VA 22727",
        "location": {
            "lat": 38.52864,
            "lng": -78.438732
        },
        "source": "Virginia Geographic Information Network (VGIN)"
        }
    ]
    }
    """
    if len(resp) > 0:
        if not 'results' in resp:
            if verbose: 
                print('\tresp JSON is missing "results"')
                print(url)
                print(json.dumps(resp, sort_keys=False, indent=2))
            return rtn_dic
        elif len(resp['results']) == 0:
            # This is the primary indicator when api.geocod.io fails to reverse geocode lat1,lon1
            if verbose: 
                print('\tlen(resp[\'results\'] == 0')
                print(url)
                print(json.dumps(resp, sort_keys=False, indent=2))
            return rtn_dic
        elif len(resp['results'][0]) < 7:
            if verbose: 
                print('\t***** WARNING: len(resp[\'results\'][0]) < 7 *****')
                print(url)
                print(json.dumps(resp, sort_keys=False, indent=2))
            return rtn_dic
    results = resp['results']
    #print('\tget_fips_codes_by_lat_lon_geocodio() len(results[0]): ', len(results[0]))
    if len(results[0]) < 7:
        print('***** WARNING: len(results[0]) < 7 *****')
        print(results, url)
    if len(results) == 0:
        print('\tLatitude/longitude ', lat1, lon1, 'is not in the database for geocodio.  Cannot reverse geocode and get FIPS.', url)
        return rtn_dic
    # The first item in the list 'results' is the location with the highest accuracy
    loc = results[0]
    address_components = loc['address_components']
    location = loc['location']
    fields = loc['fields']
    census = fields['census']
    census_data = next(iter(census.values()))
    lat2 = float(location['lat'])
    lon2 = float(location['lng'])
    if loc is None or len(loc) == 0 or location is None or len(location) == 0 or lat2 is None or lon2 is None:
        print('line 355 get_fips_codes_by_lat_lon_geocodio() loc is None or len(loc) == 0 or location is None or len(location) == 0 or lat2 is None or lon2 is None')
        print(json.dumps(resp, sort_keys=False, indent=2))

    if not 'full_fips' in census_data.keys() and not 'county_fips' in census_data.keys() and not 'state_fips' in census_data.keys():
        print('\tAll of the following required are missing: full_fips, county_fips, state_fips')
        return rtn_dic
    else:
        rtn_dic['full_fips'] = census_data['full_fips']
        rtn_dic['county_fips'] = census_data['county_fips']
        rtn_dic['state_fips'] = census_data['state_fips']
    
    if 'country' in address_components.keys(): rtn_dic['country'] = address_components['country']
    if 'state' in address_components.keys(): rtn_dic['state'] = address_components['state']
    if 'city' in address_components.keys(): rtn_dic['city'] = address_components['city']
    if 'county' in address_components.keys(): rtn_dic['county'] = address_components['county']
    if 'zip' in address_components.keys(): rtn_dic['country'] = address_components['zip']

    # Get the distance between the requested lat/lon and the reverse geocoded lat/lon.
    #dist_km = distance((lat1,lon1), (lat2,lon2))
    dist_m = haversine_distance(lat1, lon1, lat2, lon2)
    rtn_dic['dist_km'] = dist_m / 1000.0

    # Calculate the difference in latitude between the given latitude/longitude and
    # the latitude/longitude for the FIPS location.
    rtn_dic['delta_lat'] = abs(lat1 - lat2)

    # Calculate the difference in elevation between the given latitude/longitude and
    # the latitude/longitude for the FIPS location.
    elevation_m1 = elevation_by_lat_lon(lat1, lon1)
    elevation_m2 = elevation_by_lat_lon(lat2, lon2)
    delta_elevation_m = abs(elevation_m1 - elevation_m2)
    rtn_dic['delta_elevation_m'] = delta_elevation_m

    return rtn_dic


def get_fips_code_by_lat_lon_fcc(lat1, lon1, verbose):
    """
    Returns FIPS county, state, full codes for lat/lon coordinates and calculates 
    the distance error between the requested lat/lon and the found location using 
    the FCC API.   
    The returned data is a dictionary with keys:
        'full_fips', 'county_fips', 'state_fips', 'dist_km', 'delta_lat', 'delta_elevation_m'
    
    NOTE: delta_elevation_m is negative when the FIPS elevation is lower in elevation than the requested lat1/lon1. 
    
    This function gets more FiPS codes than get_fips_code_by_lat_lon_geocodio() provides, 
    but get_fips_code_by_lat_lon_geocodio() provides FIPS codes with better location
    accuracy, and additional location metadata is available with get_fips_code_by_lat_lon_geocodio(). 

    FIPS codes are numbers which uniquely identify geographic areas.
    The longer the number, the more detailed the location identification.
    state level (PA=42), county level(Berks County=42011)
    https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt

    https://geo.fcc.gov/api/census/

    "This product uses the FCC Data API but is not endorsed or certified by the FCC".

    fips = get_fips_code_by_lat_lon_fcc(59.05180188 , -156.112002, False)
    if len(fips) == 0:
        print(num, 'No FIPS code found for ', meta['lat1'],meta['lon1'])
    elif fips['full_fips'] is None or fips['county_fips'] is None or fips['state_fips'] is None:
        print(num, 'WARNING: limited FIPS code results for ', meta['lat1'],meta['lon1'])
        print(fips)
        #{'full_fips': None, 'county_fips': None, 'state_fips': None}  id=310
        #{'full_fips': None, 'county_fips': None, 'state_fips': None}  id=369
    else:
        print(num, fips)
        #{'full_fips': '021640001001185', 'county_fips': '02164', 'state_fips': '02'}

     
    """
    if verbose: print('get_fips_code_by_lat_lon_fcc()..', lat1, lon1)
    rtn_dic = {}

    url = 'https://geo.fcc.gov/api/census/block/find?latitude=' + str(lat1) + '%20&longitude=' + str(lon1) + '&censusYear=2010&format=json'
    if verbose: print(url)
    #sleep(randint(1,3))     # random pause between 1 and 3 seconds
    
    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9"})   # Optionally add an API key, etc.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #sleep(randint(1,5))     # random pause between 1 and 5 seconds

    try:
        req = requests.get(url, data=None, json=None, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), 'get_fips_code_by_lat_lon_fcc()', url)
        return rtn_dic
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        return rtn_dic

    resp = req.json()
    if len(resp) == 0:
        print("\tNo results from query ", url)
        return rtn_dic
    #print(json.dumps(resp, sort_keys=False, indent=2))
    
    """
    {
    "Block": {
        "FIPS": "021640001001185",
        "bbox": [
        -156.973634,
        58.465206,
        -154.30361,
        59.29674
        ]
    },
    "County": {
        "FIPS": "02164",
        "name": "Lake and Peninsula"
    },
    "State": {
        "FIPS": "02",
        "code": "AK",
        "name": "Alaska"
    },
    "status": "OK",
    "executionTime": "0"
    }  

    {
    "Block": {
        "FIPS": null,
        "bbox": null
    },
    "County": {
        "FIPS": null,
        "name": null
    },
    "State": {
        "FIPS": null,
        "code": null,
        "name": null
    },
    "status": "OK",
    "executionTime": "0"
    }
  
    """
    if not 'Block' in resp.keys() or not 'County' in resp.keys() or not 'State' in resp.keys():
        if verbose: print('ERROR: base key Bock, County, and/or state missing from response.  get_fips_code_by_lat_lon_fcc()')
        return rtn_dic

    if 'FIPS' in resp['Block'].keys() and not resp['Block']['FIPS'] is None: rtn_dic['full_fips'] = resp['Block']['FIPS']
    if 'FIPS' in resp['County'].keys() and not resp['County']['FIPS'] is None: rtn_dic['county_fips'] = resp['County']['FIPS']
    if 'FIPS' in resp['State'].keys() and not resp['State']['FIPS'] is None: rtn_dic['state_fips'] = resp['State']['FIPS']

    if 'bbox' in resp['Block'].keys() and not resp['Block']['bbox'] is None:
        bbox = resp['Block']['bbox']
        # and not bbox[0] is None and not bbox[1] is None and not bbox[2] is None and not bbox[3] is None
        # The bounding box has two coordinates, get the midpoint
        #print(float(bbox[1]),float(bbox[0]),float(bbox[3]),float(bbox[2]))
        midpoint = midpoint_euclidean(float(bbox[1]),float(bbox[0]),float(bbox[3]),float(bbox[2]))
        #print(midpoint[0],',',midpoint[1],'is the midpoint between', float(bbox[1]), float(bbox[0]), ' and ', float(bbox[3]), float(bbox[2]))
        lat2 = midpoint[0]
        lon2 = midpoint[1]
        # Get the distance between the requested lat/lon and the midpoint of the bounding box.
        #dist_km = distance((lat1,lon1), (lat2,lon2))
        dist_m = haversine_distance(lat1, lon1, lat2, lon2)
        rtn_dic['dist_km'] = dist_m / 1000.0
    
        # Calculate the difference in latitude between the given latitude/longitude and
        # the latitude/longitude for the FIPS location.
        rtn_dic['delta_lat'] = abs(lat1 - lat2)

        # Calculate the difference in elevation between the given latitude/longitude and
        # the latitude/longitude for the FIPS location.
        elevation_m1 = elevation_by_lat_lon(lat1, lon1)     # The requested latitude/longitude
        elevation_m2 = elevation_by_lat_lon(lat2, lon2)     # The lat/lon for the FIPS code
        delta_elevation_m = elevation_m2 - elevation_m1     # If negative, then lat2/lon2 is lower in elevation than lat1/lon1
        rtn_dic['delta_elevation_m'] = delta_elevation_m
    
    return rtn_dic


def get_fips_code_by_lat_lon(lat1:float=None, lon1:float=None, verbose:bool=False):
    """
    Returns FIPS county, state, full codes for lat/lon coordinates and calculates 
    the distance error between the requested lat/lon and the found location using 
    the FCC API.   
    The returned data is a dictionary with keys:
        'full_fips', 'county_fips', 'state_fips', 'dist_km', delta_lat, delta_elevation_m
    
    This function first attempts to acquire FIPS code from the FCC API, and then if it
    fails, it tries the geocodio API. The FCC API service is more robust than the 
    geeocodio API.  The geocodio API provides FIPS codes with better location accuracy
    than the FCC. 
    
    FIPS codes are numbers which uniquely identify geographic areas.
    The longer the number, the more detailed the location identification.
    state level (PA=42), county level(Berks County=42011)
    https://transition.fcc.gov/oet/info/maps/census/fips/fips.txt

    https://geo.fcc.gov/api/census/

    "This product uses the FCC Data API but is not endorsed or certified by the FCC".

    
    elevation_m = elevation_by_lat_lon(float(row[2]), float(row[3]))
    fips = get_fips_code_by_lat_lon(float(row[2]), float(row[3]), verbose)    # get_fips_code_by_lat_lon(lat1, lon1, verbose)
    # fips keys: 'full_fips', 'county_fips', 'state_fips', 'dist_km', delta_lat, delta_elevation_m
    if len(fips) == 0:
        print('No FIPS code found for ', row[2],row[3])
        fips = None
    elif fips['state_fips'] is None:
        fips = None
    elif fips['county_fips'] is None:
        fips = fips['state_fips']
    elif fips['full_fips'] is None:
        fips = fips['county_fips']
    else:
        fips = fips['full_fips']
    print("elevation_m: ", elevation_m, "\t", "fips: ", fips)


    fips = get_fips_code_by_lat_lon_fcc(59.05180188 , -156.112002, False)
    if len(fips) == 0:
        print('No FIPS code found for ', meta['lat1'],meta['lon1'])
    elif fips['full_fips'] is None or fips['county_fips'] is None or fips['state_fips'] is None:
        print('WARNING: limited FIPS code results for ', meta['lat1'],meta['lon1'])
        print(fips)
        #{'full_fips': None, 'county_fips': None, 'state_fips': None}  id=310
        #{'full_fips': None, 'county_fips': None, 'state_fips': None}  id=369
    else:
        print(fips)
        #{'full_fips': '021640001001185', 'county_fips': '02164', 'state_fips': '02'}

    
    """

    fips_geo = get_fips_codes_by_lat_lon_geocodio(lat1, lon1, verbose)
    if len(fips_geo) == 0:
        if verbose: print('No FIPS code returned from get_fips_codes_by_lat_lon_geocodio()')
        # Try using get_fips_code_by_lat_lon_fcc()
        fips_fcc = get_fips_code_by_lat_lon_fcc(lat1, lon1, verbose)
        if fips_fcc is None:
            if verbose: print('No FIPS code returned from get_fips_code_by_lat_lon_fcc()')
            return []
        elif len(fips_fcc) == 0:
            if verbose: print('No FIPS code returned from get_fips_code_by_lat_lon_fcc()')
            return []
        elif fips_fcc['full_fips'] is None and fips_fcc['county_fips'] is None and fips_fcc['state_fips'] is None:
            if verbose: print('No FIPS code returned from get_fips_code_by_lat_lon_fcc()')
            return []
        elif fips_fcc['full_fips'] is None or fips_fcc['county_fips'] is None or fips_fcc['state_fips'] is None:
            if verbose: print('WARNING: limited FIPS code results acquired by get_fips_code_by_lat_lon_fcc()')
            if verbose: print(fips_fcc)
            return fips_fcc
        else:
            if verbose: print('get_fips_code_by_lat_lon_fcc():')
            if verbose: print(fips_fcc)
            return fips_fcc
    elif fips_geo['full_fips'] is None or fips_geo['county_fips'] is None or fips_geo['state_fips'] is None:
        if verbose: print('WARNING: limited FIPS code results acquired by get_fips_codes_by_lat_lon_geocodio()')
        if verbose: print(fips_geo)
        fips_fcc = get_fips_code_by_lat_lon_fcc(lat1, lon1, verbose)
        if len(fips_fcc) == 0:
            if verbose: print('No FIPS code returned from get_fips_code_by_lat_lon_fcc()')
            return []
        elif fips_fcc['full_fips'] is None and fips_fcc['county_fips'] is None and fips_fcc['state_fips'] is None:
            if verbose: print('No FIPS code returned from get_fips_code_by_lat_lon_fcc()')
            return []
        elif fips_fcc['full_fips'] is None or fips_fcc['county_fips'] is None or fips_fcc['state_fips'] is None:
            if verbose: print('WARNING: limited FIPS code results acquired by get_fips_code_by_lat_lon_fcc()')
            if verbose: print(fips_fcc)
            # Determine what results are better, fips_geo or fips_fcc.

            return fips_fcc
        else:
            if verbose: print('get_fips_code_by_lat_lon_fcc():')
            if verbose: print(fips_fcc)
            return fips_fcc
    else:
        if verbose: print('get_fips_codes_by_lat_lon_geocodio():')
        if verbose: print(fips_geo)
        return fips_geo

    # CRITERIA:
    #   A 5 F change in temperature is significant:
    #       Latitude change of 3.8 degrees (265 mi)
    #       Elevation change of 282 m



# ---------------------------------------------------------------------------------------------------------
# Non GPS functions  (cartesian)

def dist_point_to_line(x, y, x1, y1, x2, y2):
    """
    Returns the perpendicular distance from the point x,y 
    and the line defined by x1,y1 and x2,y2. 

    This is a cartesian coordinate system solution, so don't apply it to GPS coordinates
    between two points very far away on the earth. 

    WARNING: if x is west of x1, or x is east of x2, then result is incorrect. 

    Usage:

    # point @ x,y
    x = -76.124517
    y = 40.443217
    # line defined by x1,y1 and x2,y1
    x1 = -76.126746
    y1 = 40.440363
    x2 = -76.121293
    y2 = 40.440406
    # All x/y values above are GPS coordinates, but they could be cartesian coordinates
    # dist_point_to_line(x, y, x1, y1, x2, y2)
    d = dist_point_to_line(x, y, x1, y1, x2, y2) 
    print("d: ", round(d* 111139,6), " meters")    # convert to meters using 1 decimal degree = 111,139 m
    # result:  # 315.2 m

    Source: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    """

    """
    # Alternative method:
    #import math
    m = (y2-y1)/(x2-x1)
    b = y1 - m * x1
    d = abs(b+m*x-y)/math.sqrt(1+pow(m,2))
    return d
    """

    # Source: https://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line
    d = (abs((x2-x1)*(y1-y) - (x1-x)*(y2-y1))) / (math.sqrt(pow((x2-x1),2) + pow((y2-y1),2)))
    return d




def get_place_by_address(address, verbose=False):
    """
    Returns the place name for the supplied address using Google Maps API

    Google Maps API: os.getenv('GOOGLE_MAPS_API_KEY')
    https://developers.google.com/maps/documentation/geocoding/start
    https://developers.google.com/maps/documentation/places/web-service/search-find-place
    Endpoint: 
    

    Usage:

    place = get_place_by_address("200 George C Delp Rd, New Holland, PA 17557")
    print(place)

    """

    if verbose: print("get_place_by_address()")

    import urllib.parse
    # NOTE:  Adding 'business in' insures a place name is returned.
    address = urllib.parse.quote_plus("business in " + address)
    #print("address:", address)

    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    # Endpoint: https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=name&input=200%20George%20C%20Delp%20Rd%2C%20New%20Holland%2C%20PA%2017557&inputtype=textquery&key=os.getenv('GOOGLE_MAPS_API_KEY')
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?fields=name&input=" + address + "&inputtype=textquery&key=" + os.getenv('GOOGLE_MAPS_API_KEY') + ""
    if verbose: print(url)

    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9"})   # Optionally add an API key, etc.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #sleep(randint(0,3))     # random pause between 0 and 3 seconds

    try:
        req = requests.get(url, headers=headers)
    except Exception as e:
        print('ERROR: ' + repr(e), 'get_nps_count_parks()', url)
        return None
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        return None

    resp = req.json()
    if len(resp) == 0:
        print("\tNo results from query ", url)
        return None
    
    if verbose: print(json.dumps(resp, sort_keys=False, indent=2))

    """
    {
    "candidates": [
        {
        "name": "200 George C Delp Rd"
        }
    ],
    "status": "OK"
    }
    """
        #if 'data' in resp.keys():
    if not 'candidates' in resp.keys():
        raise Exception("ERROR: key 'candidates' not in resp.keys()")
    if not 'status' in resp.keys():
        raise Exception("ERROR: key 'status' not in resp.keys()")
    status = resp['status']
    if status != 'OK': return None
    if verbose: print(len(resp['candidates']), "results (candidates) returned")
    results = resp['candidates'][0]
    if not 'name' in results.keys():
        raise Exception("ERROR: key 'name' not in resp.keys()")
    place = results['name']
    return place




def get_places_within_radius_and_lat_lon_old(latitude:float=40.440856, longitude:float=-76.122692, radius_m:float=8047.0, verbose=False):
    """
    Returns a list of places centered on latitude,longitude and within the radius radius_m.
    {"name": str, "latitude": float, "longitude": float, "types": []}

    latitude & longitude default to 16 Solly Ln, Bernville PA
    5 mi = 8046.7 m; 30 mi = 48280.3 m
    """
    # https://developers.google.com/maps/documentation/places/web-service/migrate-nearby
    # https://medium.com/@jrballesteros/the-shortest-guide-to-use-google-places-api-310b1b0ea29c

    import requests
    import json
    
    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    if not lat_lon_is_valid(latitude, longitude): raise Exception(f"latitude or longitude is invalid {latitude},{longitude}")

    if not isinstance(radius_m, float): raise Exception("Argument 'radius_m' must be a float between 0.0 and 50000.0 m")
    if radius_m < 0.0 or radius_m > 50000.0: raise Exception("Argument 'radius_m' must be a float between 0.0 and 50000.0 m")

    print("\nNOTE: This is the old Google Places API .. BUT the new API is buggy as of December 2024.\n")

    #gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    #print(gmaps.reverse_geocode((latitude, longitude)))

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    # Below works in place of using params. 
    #url += f"?key={os.getenv('GOOGLE_MAPS_API_KEY')}"
    #url += f"&location={latitude},{longitude}"
    #url += f"&radius={radius_m}"
    #url += f"&type=restaurant"
    if verbose: print(url)

    params = {
        "location": f"{latitude},{longitude}",
        "radius": f"{radius_m}",
        f"key": f"{os.getenv('GOOGLE_MAPS_API_KEY')}"
    }
    if verbose: print(params)

    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9"})   # Optionally add an API key, etc.
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    #sleep(randint(1,3))     # random pause between 0 and 3 seconds

    try:
        req = requests.post(url, headers=headers, params=params)
    except Exception as e:
        print('ERROR: ' + repr(e), 'get_nps_count_parks()', url)
        return None
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        return None

    resp = req.json()


    if len(resp) == 0:
        print("\tNo results from query ", url)
        return None
    
    #if verbose: print(json.dumps(resp, sort_keys=False, indent=2))

    places = []

    if not "results" in resp: raise Exception("key 'results' not found")
    results = resp['results']
    for result in results:
        #if not 'business_status' in result: raise Exception(f"key 'business_status' not found. \n{result}")    # Not always present
        if not 'geometry' in result: raise Exception(f"key 'geometry' not found \n{result}")
        if not 'location' in result['geometry']: raise Exception(f"key 'location' not found \n{result}")
        if not 'lat' in result['geometry']['location']: raise Exception(f"key 'lat' not found \n{result}")
        if not 'lng' in result['geometry']['location']: raise Exception(f"key 'lng' not found \n{result}")
        lat = result['geometry']['location']['lat']
        lng = result['geometry']['location']['lng']
        if not 'name' in result: raise Exception("key 'name' not found \n{result}")
        types = []
        if 'types' in result: types = result['types']
        name = result['name']
        #print(f"{name} @ {lat},{lng}  {types}")
        places.append({"name": name, "latitude": lat, "longitude": lng, "types": types})

    #print(results[0]['types'])
    #print(json.dumps(resp['results'][0], sort_keys=False, indent=2))
        
    return places



def get_places_within_radius_and_lat_lon_new(latitude:float=40.440856, longitude:float=-76.122692, radius_m=8047.0, verbose=False):
    """

    latitude & longitude default to 16 Solly Ln, Bernville PA
    5 mi = 8046.7 m; 30 mi = 48280.3 m
    """
    # https://developers.google.com/maps/documentation/places/web-service/migrate-nearby
    # https://medium.com/@jrballesteros/the-shortest-guide-to-use-google-places-api-310b1b0ea29c

    import requests
    import json
    
    #import googlemaps
    #from datetime import datetime

    raise Exception("Problems with the New API.  I get errors that I cannot explain.  Google documentation poor!")

    # Make sure Windows environment variable GOOGLE_MAPS_API_KEY is set & demonstrate how to access it.
    if not os.getenv('GOOGLE_MAPS_API_KEY'): raise Exception("Windows environment variable 'GOOGLE_MAPS_API_KEY' not configured!  Try to load it from a .env file with dotenv:\nfrom dotenv import load_dotenv\nload_dotenv()")

    if not lat_lon_is_valid(latitude, longitude): raise Exception(f"latitude or longitude is invalid {latitude},{longitude}")

    if not isinstance(radius_m, float): raise Exception("Argument 'radius_m' must be a float between 0.0 and 50000.0 m")
    if radius_m < 0.0 or radius_m > 50000.0: raise Exception("Argument 'radius_m' must be a float between 0.0 and 50000.0 m")

    #import googlemaps
    #gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    #places = gmaps.places_nearby(location=(latitude,longitude), radius=radius_m, type="restaurant")
    #print(places)
    #return None



    url = "https://places.googleapis.com/v1/places:searchNearby"
    if verbose: print(url)

    params = {
        #"includedTypes": ["restaurant"],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": 37.7937, 
                    "longitude": -122.3965},
            "radius": 500.0
            }
        }
    }
    if verbose: print(params)

    #headers = get_organic_req_header(url)
    #headers.update({"accept-language": "en-US,en;q=0.9", "Content-Type": "application/json", "X-Goog-Api-Key": f"{os.getenv('GOOGLE_MAPS_API_KEY')}", "X-Goog-FieldMask": "places.displayName"})
    #headers.update({"accept-language": "en-US,en;q=0.9"})
    #headers = {"Content-Type": "application/json", "X-Goog-Api-Key": os.getenv('GOOGLE_MAPS_API_KEY'), "X-Goog-FieldMask": "places.displayName"}
    headers = {"Content-Type": "application/json", "X-Goog-Api-Key": os.getenv('GOOGLE_MAPS_API_KEY'), "X-Goog-FieldMask": "places.formattedAddress"}
    print(headers)

    sleep(randint(1,3))     # random pause between 0 and 3 seconds
    try:
        req = requests.post(url, headers=headers, params=params)
    except Exception as e:
        print(e)
        return None
    
    if not req.status_code == 200: 
        print('ERROR: resp.status_code = ', req.status_code)
        print(req.text)
        return None

    resp = req.json()


    if len(resp) == 0:
        print("\tNo results from query ", url)
        return None
    
    #if verbose: print(json.dumps(resp, sort_keys=False, indent=2))

    if not "results" in resp: raise Exception("key 'results' not found")
    results = resp['results']
    for result in results:
        #if not 'business_status' in result: raise Exception(f"key 'business_status' not found. \n{result}")    # Not always present
        if not 'geometry' in result: raise Exception(f"key 'geometry' not found \n{result}")
        if not 'location' in result['geometry']: raise Exception(f"key 'location' not found \n{result}")
        if not 'lat' in result['geometry']['location']: raise Exception(f"key 'lat' not found \n{result}")
        if not 'lng' in result['geometry']['location']: raise Exception(f"key 'lng' not found \n{result}")
        lat = result['geometry']['location']['lat']
        lng = result['geometry']['location']['lng']
        if not 'name' in result: raise Exception("key 'name' not found \n{result}")
        types = []
        if 'types' in result: types = result['types']
        name = result['name']
        print(f"{name} @ {lat},{lng}  {types}")

    #print(results[0]['types'])
    #print(json.dumps(resp['results'][0], sort_keys=False, indent=2))


# GeoPy address cleaner and reverse geolocator.
def ex_geopy():
    # GeoPy
    # https://pypi.org/project/geopy/
    # pip install geopy

    # GeoPy requires API key from either GoogleV3 or Geocodio

    from geopy.geocoders import GoogleV3, Geocodio
    geolocator = GoogleV3(api_key = os.getenv('GOOGLE_MAPS_API_KEY'))
    #geolocator = Geocodio(api_key = os.getenv('API_GEOCODIO_KEY'))

    raw_address = "501 South Abbott Street, Marfa, TX, 79843"
    print(f"raw_address: {raw_address}")
    location = geolocator.geocode(raw_address)
    print("clean address: ", location.address)
    print("lat, lon ", location.latitude, location.longitude)
    # clean address:  501 S Abbot St, Marfa, TX 79843, USA
    # lat, lon  30.3058196 -104.0224489
    #
    # reverse(query, *, exactly_one=True, timeout=DEFAULT_SENTINEL, distance=None)¶
    location = geolocator.reverse("30.3058196, -104.0224489")
    print("reverse address of 30.3058196 -104.0224489: ", location.address)
    # reverse address of 30.3058196 -104.0224489:  501 S Abbot St, Marfa, TX 79843


def ex_distance_to_geofence():

    point = (40.440363, -76.126746)
    line_start = (40.440406, -76.121293)
    line_end = (40.443217, -76.124517)
    dist_m = distance_to_geofence(point, line_start, line_end)
    print(f"distance_to_geofence() for point {point}, line_start: {line_start}, line_end: {line_end} = {dist_m} m")
    # distance_to_geofence() for point (40.440363, -76.126746), line_start: (40.440406, -76.121293), line_end: (40.443217, -76.124517) = 369.1795312036444 m

    return None

    """
    point = (40.440363, -76.126746)
    line_start = (40.440406, -76.121293)
    line_end = (40.443217, -76.124517)
    dist_m = distance_to_geofence(point, line_start, line_end)
    print("dist_m: ", dist_m)   # result: 362.8 m.  Correct result is 365 m (graphical estimate using Google Maps)
    """

    """
    # point @ x,y
    lat = 40.443217
    lon = -76.124517
    # 40.440408, -76.127463  a point just N of the line, but west of the first line endpoint @ x1,y1
    lat = 40.440408
    lon = -76.127463
    """

    # line defined by x1,y1 and x2,y1
    lat1 = 40.440363
    lon1 = -76.126746

    lat2 = 40.440406
    lon2 = -76.121293

    # dist_point_to_line(x, y, x1, y1, x2, y2)
    #d = dist_point_to_line(x, y, x1, y1, x2, y2) 
    #print("d: ", round(d,1), " m")      # 315.2 m       1 deg = 111,139 m = 111,320 m

    #print(haversine_distance(lat1,lon1,lat2,lon2))

    d = distance_to_geofence((lat,lon), (lat1,lon1), (lat2,lon2))
    print("d: ", round(d,1), " m")      # 315.2 m


def ex_get_place_by_address():

    locations = [
        {"place_name": "CNH Technical Center", "address": "200 George C Delp Rd, New Holland, PA 17557", "latitude": None, "longitude": None}
    ]

    location = locations[0]
    place = get_place_by_address(location['address'], False)
    print(f"get_place_by_address() returned '{place}', expected '{location['place_name']}', for address: '{location['address']}'")

    return None


def ex_get_place_address():
    locations = [
        {"place_name": "Ozark Mountains", "address": None},
        {"place_name": "Adirondack Mountains", "address": None, "latitude": 44.1247154, "longitude": -73.8693043}
    ]

    location = locations[1]
    data = get_place_address(location['place_name'])
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(f"get_place_address() for '{location['place_name']}':  {data}") 
    # get_place_address() for 'Ozark Mountains':  {'full_address': 'Ozark Mountains, United States', 'city': None, 'state': None, 'zip': None, 'country': 'US', 'latitude': 36.5692952, 'longitude': -93.097702}
    # get_place_address() for 'Adirondack Mountains':  {'full_address': 'Adirondack Mountains', 'city': None, 'state': None, 'zip': None, 'country': 'US', 'latitude': 44.1247154, 'longitude': -73.8693043}


    return None

    """    
    data = get_place_address("Ouachita Mountains", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     # {'name': 'Ouachita Mountains', 'state': 'OK', 'country': 'US', 'zip': '74957', 'latitude': 34.50039179999999, 'longitude': -94.5004891}
    
    data = get_place_address("Big Bear Lake", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)    

    data = get_place_address("White Mountains", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)     

    #(639, 'Sequoia National Forest', Decimal('36.01567'), Decimal('-118.39294'), Decimal('2910.7'), None, '061070027012068')
    data = get_place_address("Sequoia National Forest", True)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)    

    #(791, 'Topaz Mountain Rockhound Recreation Area', Decimal('39.6665'), Decimal('-113.11455'), Decimal('1609.0'), None, '490230102001673')
    data = get_place_address("Topaz Mountain Rockhound Recreation Area", True)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)    

    # (947, 'Sand to Snow National Monument', Decimal('34.06778'), Decimal('-116.62791'), Decimal('1387.9'), None, '060710104171004')
    data = get_place_address("Sand to Snow National Monument", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)    

    addr = get_place_address("Samuel H. Boardman State Scenic Corridor", False)
    print("full_address: ", addr['full_address'])
    print(data)

    data = get_place_address("idontexist", False)
    if data is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.")
    print(data)    
    
    """
    # Ozark Mountains -> (OrderedDict([('Recipient', 'Ozark Mountains, United States')]), 'Ambiguous')
    # Adirondack Mountains -> (OrderedDict([('StreetName', 'Adirondack'), ('StreetNamePostType', 'Mountains')]), 'Ambiguous')
    # Ouachita Mountains -> (OrderedDict([('LandmarkName', 'Ouachita Mountains'), ('PlaceName', 'Oklahoma'), ('ZipCode', '74957'), ('CountryName', 'USA')]), 'Ambiguous')
    # Big Bear Lake -> (OrderedDict([('PlaceName', 'Big Bear Lake'), ('StateName', 'CA, USA')]), 'Ambiguous')
    # White Mountains -> (OrderedDict([('LandmarkName', 'White Mountains'), ('PlaceName', 'Lincoln'), ('StateName', 'NH'), ('ZipCode', '03251'), ('CountryName', 'USA')]), 'Ambiguous')
    # Sequoia National Forest -> Porterville, CA, United States -> (OrderedDict([('PlaceName', 'Porterville'), ('StateName', 'CA'), ('CountryName', 'United States')]), 'Ambiguous')
    # Topaz Mountain Rockhound Recreation Area -> (OrderedDict([('LandmarkName', 'Topaz Mountain'), ('Recipient', 'Utah, United States')]), 'Ambiguous')
    # Sand to Snow National Monument, Millard Canyon Rd, California, USA -> (OrderedDict([('Recipient', 'Sand to Snow National Monument, Millard'), ('StreetName', 'Canyon'), ('StreetNamePostType', 'Rd'), ('PlaceName', 'California'), ('StateName', 'USA')]), 'Ambiguous')
    # Fish And Owl Canyons -> ? -> (OrderedDict([('StreetName', 'Fish'), ('IntersectionSeparator', 'and'), ('SecondStreetName', 'Owl'), ('SecondStreetNamePostType', 'Rd'), ('PlaceName', 'Utah, United States')]), 'Intersection')
    # Marando Industries Inc. -> 2201 Reading Ave, Reading, PA 19609, United States -> (OrderedDict([('AddressNumber', '2201'), ('StreetName', 'Reading'), ('StreetNamePostType', 'Ave'), ('PlaceName', 'Reading'), ('StateName', 'PA'), ('ZipCode', '19609'), ('CountryName', 'United States')]), 'Street Address')
    # Wright Brothers National Memorial -> 1000 N Croatan Hwy, Kill Devil Hills, NC 27948, United States -> (OrderedDict([('AddressNumber', '1000'), ('StreetNamePreDirectional', 'N'), ('StreetName', 'Croatan'), ('StreetNamePostType', 'Hwy'), ('PlaceName', 'Kill Devil Hills'), ('StateName', 'NC'), ('ZipCode', '27948'), ('CountryName', 'United States')]), 'Street Address')
    # NOT RESOLVED: North Country National Scenic Trail -> Appalachian National Scenic Trail, Harpers Ferry, West Virginia 25425, United States -> (OrderedDict([('BuildingName', 'Appalachian National Scenic Trail, Harpers Ferry, West Virginia 25425'), ('CountryName', 'United States')]), 'Ambiguous')
    # NOT RESOLVED: Appalachian National Scenic Trail -> Appalachian National Scenic Trail, Harpers Ferry, West Virginia 25425, United States -> (OrderedDict([('BuildingName', 'Appalachian National Scenic Trail, Harpers Ferry, West Virginia 25425'), ('CountryName', 'United States')]), 'Ambiguous')
    # Johnson (Gordy's) Hill -> Johnson Hill, New Mexico 87823, United States -> (OrderedDict([('LandmarkName', 'Johnson Hill'), ('PlaceName', 'New'), ('StateName', 'Mexico'), ('ZipCode', '87823'), ('CountryName', 'United States')]), 'Ambiguous')

    """
    addr = get_place_address("Samuel H. Boardman State Scenic Corridor", False)
    print("full_address: ", addr['full_address'])
    print(addr['city'], addr['state'], addr['zip'], addr['country'])
    print("usaddress.tag: ", usaddress.tag(addr['full_address']))
    """

    """
    # get_place_address()
    test_places = ['Ozark Mountains', 'Adirondack Mountains', 'Ouachita Mountains', 'Big Bear Lake', 'White Mountains', 'Sequoia National Forest', 'Topaz Mountain Rockhound Recreation Area', 'Sand to Snow National Monument', 'Marando Industries Inc.', 'Wright Brothers National Memorial', 'Samuel H. Boardman State Scenic Corridor']
    for test_place in test_places:
        addr = get_place_address(test_place, False)
        print("full_address: ", addr['full_address'])
        print(addr['city'], addr['state'], addr['zip'], addr['country'], "\n")
    """


def ex_get_fips_code_by_lat_lon():

    locations = [
        {"place_name": None, "address": None, "latitude": 29.52743158, "longitude": -102.5979169},
        {"place_name": "Adirondack Mountains", "address": None, "latitude": 44.1247154, "longitude": -73.8693043}
    ]

    location = locations[1]
    fips = get_fips_code_by_lat_lon(location['latitude'], location['longitude'], verbose=False)
    print(f"get_fips_code_by_lat_lon({location['latitude']},{location['longitude']}): {fips} ")
    # get_fips_code_by_lat_lon(29.52743158,-102.5979169): []
    # get_fips_code_by_lat_lon(44.1247154,-73.8693043): {'full_fips': '360319609021081', 'county_fips': '36031', 'state_fips': '36', 'country': '12879', 'state': 'NY', 'city': 'Newcomb', 'county': 'Essex County', 'dist_km': 0.0505141646392236, 'delta_lat': 3.999999975690116e-07, 'delta_elevation_m': 0.031982421875909495}

    return None


def ex_get_fips_codes_by_lat_lon_geocodio():
    locations = [
        {"place_name": "CNH Technical Center", "address": "200 George C Delp Rd, New Holland, PA 17557", "latitude": None, "longitude": None},
        {"place_name": "Ozark Mountains", "address": None, "latitude": None, "longitude": None},
        {"place_name": "Adirondack Mountains", "address": None, "latitude": 44.1247154, "longitude": -73.8693043},
        {"place_name": "Alcatraz Main Cell House", "address": "Pier 39, San Francisco, CA 94133, USA", "latitude": 37.82676234, "longitude": -122.4230206}
    ]

    location = locations[3]
    print(f"location: {location}")
    fips = get_fips_codes_by_lat_lon_geocodio(location['latitude'], location['longitude'], verbose=False)
    if len(fips) == 0: print(f"ERROR get_fips_codes_by_lat_lon_geocodio({location['latitude']},{location['longitude']}): {fips} ")
    print(f"get_fips_codes_by_lat_lon_geocodio({location['latitude']},{location['longitude']}): {fips} ")
    # get_fips_code_by_lat_lon(29.52743158,-102.5979169): []
    # get_fips_code_by_lat_lon(44.1247154,-73.8693043): {'full_fips': '360319609021081', 'county_fips': '36031', 'state_fips': '36', 'country': '12879', 'state': 'NY', 'city': 'Newcomb', 'county': 'Essex County', 'dist_km': 0.0505141646392236, 'delta_lat': 3.999999975690116e-07, 'delta_elevation_m': 0.031982421875909495}



if __name__ == '__main__':

    """
    locations = [
        {"place_name": "CNH Technical Center", "address": "200 George C Delp Rd, New Holland, PA 17557", "latitude": None, "longitude": None},
        {"place_name": "Ozark Mountains", "address": None, "latitude": None, "longitude": None},
        {"place_name": "Adirondack Mountains", "address": None, "latitude": 44.1247154, "longitude": -73.8693043},
        {"place_name": "Alcatraz Main Cell House", "address": "Pier 39, San Francisco, CA 94133, USA", "latitude": 37.82676234, "longitude": -122.4230206}
    ]
    """


    #test_savvy_get_extreme_lat_long_in_set()

    #places = get_places_within_radius_and_lat_lon_old(verbose=True)
    #places = get_places_within_radius_and_lat_lon_new(verbose=True)


    # ---------------------------------------------------------------------------------------------------------
    # get_place_by_address()

    #ex_get_place_by_address()

    # ---------------------------------------------------------------------------------------------------------
    # get_place_address()

    #ex_get_place_address()


    # ---------------------------------------------------------------------------------------------------------
    # get_address_by_lat_lon()

    """
    addr = get_address_by_lat_lon(37.82676234, -122.4230206, False)
    #formatted_address, name, addr, state, zip, county, country
    print(addr['formatted_address'])
    """

    # ---------------------------------------------------------------------------------------------------------
    # get_fips_code_by_lat_lon()

    #ex_get_fips_code_by_lat_lon()

    #ex_get_fips_codes_by_lat_lon_geocodio()

        
    # ---------------------------------------------------------------------------------------------------------
    # get_address_by_lat_lon()

    """
    addr = get_address_by_lat_lon(37.82676234, -122.4230206, False)
    #formatted_address, name, addr, state, zip, county, country
    print(addr['formatted_address'])
    # Alcatraz Main Cell House, Pier 39, San Francisco, CA 94133, USA
    """

    """
    # This location doesn't return the correct 'name'
    addr = get_address_by_lat_lon(40.0906505, -76.1040396)
    print("formatted_address:", addr['formatted_address'])
    print("name:", addr['name'])
    """

    # ---------------------------------------------------------------------------------------------------------
    # get_gps_bounding_box()

    #test_get_gps_bounding_box()


    # ---------------------------------------------------------------------------------------------------------

    """
    rating = get_place_rating("Carters Lake", False)
    if rating is None: raise Exception("ERROR: No place found by Google Maps API for the place submitted.  get_place_rating()")
    print("Place rating is ", rating)    
    """


    # ---------------------------------------------------------------------------------------------------------

    #lat_lon = midpoint_euclidean(40.440363, -76.126746, 40.440406, -76.121293)
    #print('midpoint: ', lat_lon[0],',',lat_lon[1])
    # midpoint:  40.4403845 , -76.1240195

    # distance from midpoint 40.4403845 , -76.1240195 to 40.443217, -76.124517
    #dist_km = distance((40.4403845, -76.1240195), (40.443217, -76.124517))
    #print(f"distance: {round(dist_km,3)} km -> {round(dist_km*1000,3)} m")
    # distance: 0.318 km -> 317.761 m

    # ---------------------------------------------------------------------------------------------------------

    #dist_m = haversine_distance(40.4403845, -76.1240195, 40.443217, -76.124517)
    #print(f"haversine_distance: {round(dist_m/1000,3)} km \t {round(dist_m,3)} m")
    # haversine_distance: 0.318 km     317.761 m

    #dist_m = haversine_distance(40.440363, -76.126746, 40.440406, -76.121293)
    #print("dist_m: ", dist_m)
    # Result is 461.5 m.  The correct result is 461.5 m. 

    # ---------------------------------------------------------------------------------------------------------
    # distance_to_geofence()

    #ex_distance_to_geofence()


    # ---------------------------------------------------------------------------------------------------------
    # GeoPy
    # https://pypi.org/project/geopy/
    # pip install geopy
    
    #ex_geopy()

    # ---------------------------------------------------------------------------------------------------------
