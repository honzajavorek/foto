from datetime import time


def format_datetime(val):
    if isinstance(val, time):
        s = val.strftime('%H:%M:%S')
    else:
        s = val.strftime('%Y:%m:%d %H:%M:%S')
    if val.microsecond:
        ms = val.strftime('%f').lstrip('0')
        s += '.' + ms
    if val.tzinfo:
        tz = val.strftime('%z')
        s += tz[:-2] + ':' + tz[-2:]
    return s
