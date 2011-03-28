from datetime import datetime

DEFAULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

def parse_date(d, f=DEFAULT_DATE_FORMAT):
    return datetime.strptime(d, f)

def serialize_date(d, f=DEFAULT_DATE_FORMAT):
    return datetime.strftime(d, f)

def now():
    return datetime.utcnow()

def now_serialized():
    return serialize_date(now())

