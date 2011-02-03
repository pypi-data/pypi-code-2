import json
import datetime
try:
    import iso8601
except ImportError:
    iso8601 = None

class FancyJSONEncoder(json.JSONEncoder):
    _registry = {}

    def __call__(self, obj, **kwargs):
        '''
        Pass object trough all encoders.
        '''
        for cls in self._registry:
            checker, encoder = self._registry[cls]
            if checker(obj):
                return {'__proxy__': cls, 'value': encoder(obj)}

        return obj

    def register(self, cls, checker, encoder):
        self._registry[cls] = (checker, encoder)
        

class FancyJSONDecoder(object):
    _registry = {}

    def __call__(self, obj, **kwargs):
        '''
        Pass object trough all decoders.
        '''
        try:
            cls = obj['__proxy__']
        except:
            return obj
        else:
            try:
                decoder = self._registry[cls]
            except KeyError:
                raise ValueError("JSON decoder for %r not registered." % (cls,))
            else:
                return decoder(obj['value'])

    def register(self, cls, decoder):
        self._registry[cls] = decoder

    def unregister(self, cls):
        try:
            del self._registry[cls]
        except:
            pass


ENCODER = FancyJSONEncoder()
DECODER = FancyJSONDecoder()

# complex encoder
ENCODER.register('complex',
    lambda obj: isinstance(obj, complex),
    lambda obj: [obj.real, obj.imag])
DECODER.register('complex',
    lambda obj: complex(*obj))

# Ellipsis encoded
ENCODER.register('ellipsis',
    lambda obj: obj == Ellipsis,
    lambda obj: None)
DECODER.register('ellipsis',
    lambda obj: Ellipsis)

# set encoder
ENCODER.register('set',
    lambda obj: isinstance(obj, set),
    lambda obj: list(obj))
DECODER.register('set',
    lambda obj: set(obj))

if iso8601:
    # datetime.date encoder
    ENCODER.register('date',
        lambda obj: isinstance(obj, datetime.date),
        lambda obj: obj.isoformat())
    DECODER.register('date',
        lambda obj: iso8601.parse_date(obj))

    # datetime.datetime encoder
    ENCODER.register('datetime',
        lambda obj: isinstance(obj, datetime.datetime),
        lambda obj: obj.isoformat())
    DECODER.register('datetime',
        lambda obj: iso8601.parse_date(obj))


def dumps(obj, *args, **kwargs):
    return json.dumps(obj, default=ENCODER, *args, **kwargs)

def loads(obj, *args, **kwargs):
    return json.loads(obj, object_hook=DECODER, *args, **kwargs)


if __name__ == '__main__':
    import pprint
    ppr = pprint.PrettyPrinter()
    now = datetime.datetime.now()

    test1 = json_dump({
        'now': now, 
        'set': set((1,2,3,4,42,42,23,23)),
        'ell': Ellipsis,
        'complex': 23+42j,
    })
    ppr.pprint(test1)
    test2 = json_load(test1)
    ppr.pprint(test2)
    ppr.pprint(test1 == test2)

