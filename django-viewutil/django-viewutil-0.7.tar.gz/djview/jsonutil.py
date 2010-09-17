"""
This module wraps the simplejson dump/dumps/load/loads functions
with versions that provide custom encoding/decoding of these types:

   datetime.date
   datetime.datetime
   datetime.time

Also, any object that defines a method "to_jsondata()", which should return
a json-encodable value, will be encoded thus.  There is no corresponding
decode mechanism at this point.

An external simplejson library will be used if available; otherwise, the one
bundled with Django.

"""

import datetime
import time

try:
    import simplejson
except:
    # use bundled version
    from django.utils import simplejson


FORMATS = {datetime.datetime: "%Y-%m-%dT%H:%M:%S",
           datetime.date: '%Y-%m-%d',
           datetime.time: '%H:%M:%S'}


def datedecode(obj):
    if isinstance(obj, basestring):
        for cls, fmt in FORMATS.items():
            try:
                res = datetime.datetime.strptime(obj, fmt)
            except ValueError:
                continue
            else:
                if obj == datetime.date:
                    return res.date()
                elif obj == datetime.time:
                    return res.time()
                return res
        return obj
    elif isinstance(obj, dict):
        for k, v in obj.iteritems():
            obj[k] = datedecode(v)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            obj[i] = datedecode(v)
    return obj


class Encoder(simplejson.JSONEncoder):

    def default(self, obj):
        if hasattr(obj, 'to_jsondata'):
            return obj.to_jsondata()
        for k in FORMATS:
            if isinstance(obj, k):
                return obj.strftime(FORMATS[k])
        return super(Encoder, self).default(obj)


def dump(obj, fp, **kw):
    kw.setdefault('cls', Encoder)
    return simplejson.dump(obj, fp, **kw)


def dumps(obj, **kw):
    kw.setdefault('cls', Encoder)
    return simplejson.dumps(obj, **kw)


def loads(s, **kw):
    return datedecode(simplejson.loads(s, **kw))


def load(s, fp, **kw):
    return datedecode(simplejson.load(s, fp, **kw))


__all__ = ['load', 'loads', 'dump', 'dumps']
