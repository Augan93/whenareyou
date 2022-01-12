import os
import requests


from functools import lru_cache
from urllib.parse import quote#, quote_plus
# from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

# -----------------------------------------------------------------------------
# old / broken: using google maps api to obtain address lat/lng
# -----------------------------------------------------------------------------
_LONG_LAT_URL = ('https://maps.googleapis.com/maps/api/geocode/json?address={0}'
                 '&sensor=false')
# -----------------------------------------------------------------------------
# alternative: use openstreetmap
# -----------------------------------------------------------------------------
_LONG_LAT_URL_Nominatim = "http://nominatim.openstreetmap.org/search?q="
# -----------------------------------------------------------------------------


# HELPERS ---------------------------------------------------------------------
@lru_cache(None)
def _cached_json_get(url):
    """
    a general helper -
    Makes a get to that URL and caches it. Simple right? Oh it also returns the
    JSON as a dict for you already!
    """
    return requests.get(url).json()

def _queryOSM(address):
    """
    a helper to query nominatim.openstreetmap for given address
    """
    url = _LONG_LAT_URL_Nominatim + quote(address) + '&format=json&polygon=0'
    response = _cached_json_get(url)
    if not response:
        raise ValueError(f"Address not found: '{address}'")
    return (float(response[0].get(key)) for key in ('lat', 'lon'))

def _get_tz(lat, lng, _tf=TimezoneFinder()):
    """
    a helper to call timezonefinder.
    returns IANA time zone name of given lat/long coordinates
    """
    tzname = _tf.timezone_at(lng=lng, lat=lat)
    if tzname:
        return tzname
    return None


# MAIN METHODS ----------------------------------------------------------------
def whenareyou(address):
    """
    Find the time zone of a given address

    Parameters
    ----------
    address : str
        address to search.

    Returns
    -------
    tzname : str
        IANA time zone name

    """
    # adding "geolocator" kwarg would allow to select geolocating service,
    # i.e. the "geolocator" keyword would select a function like _queryOSM
    return _get_tz(*_queryOSM(address))



with open(os.path.join(os.path.dirname(__file__), 'airports.csv'), encoding="utf-8") as csvfile:
    data = csvfile.read().splitlines()
    for i, l in enumerate(data):
        data[i] = l.split(",")
    _airports_dict = {item[0]: list(item[1:]) for item in zip(*data)}

del csvfile, data, i, l


def whenareyou_IATA(airport):
    """
    Find the time zone of a given airport IATA code

    Parameters
    ----------
    airport : str
        airport IATA code.

    Returns
    -------
    tzname : str
        IANA time zone name

    """
    airport = airport.upper().strip()
    l = _airports_dict["iata_code"]
    ix = l.index(airport) if airport in l else None

    if not ix:
        raise ValueError(f"IATA code not found: '{airport}'")

    tzname = _get_tz(float(_airports_dict['latitude_deg'][ix]),
                     float(_airports_dict['longitude_deg'][ix]))
    return tzname