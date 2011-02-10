
try:
    import json
except ImportError:
    import simplejson as json
import datetime
import os
import time
from urllib import quote_plus
from hashlib import md5

def encode_value(value):
    if isinstance(value, basestring):
        if isinstance(value, unicode):
            value = value.encode('utf-8')
    elif isinstance(value, bool):
        value = str(int(value))
    elif isinstance(value, (int, long)):
        value = str(value)
    elif isinstance(value, float):
        value = "%.5f" % value
    elif isinstance(value, datetime.timedelta):
        value = str(int(value.days*24*60*60 + value.seconds))
    elif isinstance(value, datetime.datetime):
        value = str(int(time.mktime(value.timetuple())))
    elif isinstance(value, (list, tuple)):
        value = ",".join(value)
    else:
        raise TypeError("Unsupported attribute value of type %s" % type(value))
    
    return value

class JSONFormatter(object):
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = "%s %s" % (DATE_FORMAT, TIME_FORMAT)

    def __call__(self, timestamp, attributes):
        attributes['ts'] = timestamp
        return json.dumps(attributes, separators=(',', ':'), default=self._default)
    
    def _default(self, obj):
        if isinstance(obj, datetime.timedelta):
            return str(int(obj.days*24*60*60 + obj.seconds))
        elif isinstance(obj, datetime.date) and not isinstance(obj, datetime.datetime):
            return obj.strftime(self.DATE_FORMAT)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime(self.DATETIME_FORMAT)
        elif isinstance(o, datetime.time):
            return obj.strftime(self.TIME_FORMAT)
        raise TypeError("[JSONFormatter] Unsupported attribute value of type %s" % type(value))

class HiveFormatter(object):
    def __call__(self, timestamp, attributes):
        return "%s\x01%s" % (int(timestamp), "\x02".join(
            "%s\x03%s" % (
                n, encode_value(v).replace('\n', '\\n').replace('\x03', '?').replace('\x02', '?').replace('\x01', '?')
            ) for n, v in attributes.iteritems()))

class StreamLogger(object):
    def __init__(self, stream, formatter):
        self.stream = stream
        self.formatter = formatter

    def open(self):
        pass

    def close(self):
        pass

    def flush(self):
        if hasattr(self.stream, "flush"):
            self.stream.flush()

    def write(self, event, timestamp, attributes):
        self.stream.write("%d\t%s\t%s\n" % (int(timestamp), event, self.formatter(timestamp, attributes)))

class FileLogger(StreamLogger):
    def __init__(self, path, formatter):
        self.path = path
        super(FileLogger, self).__init__(None, formatter)

    def open(self):
        if not self.stream:
            self.stream = open(self.path, "a")

    def close(self):
        if self.stream:
            self.stream.close()
            self.stream = None

    def write(self, event, timestamp, attributes):
        if not self.stream:
            self.open()

        super(FileLogger, self).write(event, timestamp, attributes)

class RotatingFileLogger(FileLogger):
    def __init__(self, path, formatter, rotate_period=30*60, rotate_size=50*1024*1024):
        super(RotatingFileLogger, self).__init__(None, formatter)
        self.base_path = path
        self.rotate_period = rotate_period
        self.rotate_size = rotate_size
        self.last_rotate_check = 0
        self.start_time = 0
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError, exc:
                if exc.errno != 17: # If the error isn't "file exists" then reraise
                    raise
    
    def open(self):
        if not self.stream:
            self.start_time = time.time()
            filename = "%d_%d.log" % (self.start_time, os.getpid())
            self.path = os.path.join(self.base_path, filename)
            super(RotatingFileLogger, self).open()
            stat = os.stat(self.path)
            self.dev, self.ino = stat.st_dev, stat.st_ino
            self.open_ts = time.time()
    
    def close(self):
        if self.stream:
            super(RotatingFileLogger, self).close()
            self.dev = self.ino = -1
            self.path = None
            self.open_ts = None
            self.start_time = 0
    
    def write(self, event, timestamp, attributes):
        # See if the file changed out from under us
        if self.stream:
            if os.path.exists(self.path):
                stat = os.stat(self.path)
                if (stat.st_dev != self.dev) or (stat.st_ino != self.ino):
                    self.close()
            else:
                self.close()
        
        super(RotatingFileLogger, self).write(event, timestamp, attributes)
        
        if self.should_rotate():
            self.close()
    
    def should_rotate(self):
        if time.time() - self.last_rotate_check < 60*5:
            return False
        
        self.flush()
        
        try:
            size = os.path.getsize(self.path)
        except OSError:
            return True

        if size > 1024*1024 and (size > self.rotate_size or time.time() - self.start_time >= self.rotate_period):
            return True
