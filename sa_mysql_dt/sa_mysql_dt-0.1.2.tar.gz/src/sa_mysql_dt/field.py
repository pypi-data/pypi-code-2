import time
from datetime import datetime
#from sqlalchemy.types import Numeric
from sqlalchemy.databases.mysql import MSNumeric
from decimal import Decimal

class DateTime(MSNumeric):
    """A DateTime type that stores itself as a float.
    
    This is to support higher-precision DateTime fields in MySQL,
    as its datetime field only supports second granularity.
    """

    def __init__(self):
        super(DateTime, self).__init__(precision=20, scale=6, asdecimal=False)

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return value
            # this will fail on a 32 bit platform by 2038, but
            # should work on a 64 bit platform
            t = time.mktime(value.timetuple())
            ms = value.microsecond / 1000000.
            result = Decimal(repr(t + ms))
            return result
        
        return process

    def result_processor(self, dialect):
        def process(value):
            if value is None:
                return value
            return datetime.fromtimestamp(float(value))
        return process
