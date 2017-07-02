import re
from decimal import Decimal

import geocoder

from .metadata import Metadata


cache = {}


def location(filename, **options):
    meta = Metadata(filename)
    coords = parse_coords(meta)
    if coords:
        cache_key = _create_cache_key(*coords)
        if cache_key not in cache:
            cache[cache_key] = locate(*coords, **options)
        return cache[cache_key]
    return None


def _create_cache_key(lat, lng):
    key_parts = []
    for float_num in lat, lng:
        decimal_num = Decimal(float_num)
        decimal_num = decimal_num.quantize(Decimal('1.0'))
        key_parts.append(str(decimal_num))
    return ';'.join(key_parts)


def locate(lat, lng, **kwargs):
    return geocoder.google([lat, lng], method='reverse', **kwargs)


def parse_coords(metadata):
    lat = None
    lng = None

    gps = metadata['GPSCoordinates'] or metadata['GPSPosition']
    if not gps:
        gps_lat = metadata['GPSLatitude']
        gps_lng = metadata['GPSLongitude']
        if gps_lat and gps_lng:
            gps = ', '.join([gps_lat, gps_lng])
    if not gps:
        return None

    # 45 deg 27' 56.16" N, 9 deg 11' 28.68" E
    gps_re = (
        r'(\d+) deg (\d+)\' ([\d\.]+)" ([NS]), '
        r'(\d+) deg (\d+)\' ([\d\.]+)" ([WE])'
    )
    match = re.search(gps_re, gps)
    if not match:
        return None

    lat_deg, lat_min, lat_sec = match.group(1), match.group(2), match.group(3)
    lat_pos = match.group(4)
    lat = _dms2dd(lat_deg, lat_min, lat_sec, lat_pos)

    lng_deg, lng_min, lng_sec = match.group(5), match.group(6), match.group(7)
    lng_pos = match.group(8)
    lng = _dms2dd(lng_deg, lng_min, lng_sec, lng_pos)

    return lat, lng


def _dms2dd(degrees, minutes, seconds, direction):
    dd = float(degrees) + float(minutes) / 60 + float(seconds) / (60 * 60)
    if direction == 'S' or direction == 'W':
        dd *= -1
    return dd
