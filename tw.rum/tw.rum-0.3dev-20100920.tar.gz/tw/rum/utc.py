import datetime

__all__ = ["UTC"]

ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)

# A UTC class.

class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO
