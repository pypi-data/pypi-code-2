from dynts.utils import import_module
from dynts.conf import settings
from base import TimeSeries, Formatters

BACKENDS = {
    'zoo': 'zoo',
    'rmetrics': 'rmetrics',
    'numpy': 'tsnumpy',
}

istimeseries = lambda value : isinstance(value,TimeSeries)


def timeseries(name = '', backend = None, **kwargs):
    '''Create a new :class:`dynts.TimeSeries` object.'''
    from dynts import InavlidBackEnd
    backend = backend or settings.backend
    bname = BACKENDS.get(backend,None)
    if bname:
        bmodule = 'dynts.backends.%s' % bname
    else:
        bmodule = backend
    module = import_module(bmodule)
    name = name or bmodule
    try:
        factory = getattr(module, 'TimeSeries')
    except AttributeError:
        raise InavlidBackEnd('Could not find a TimeSeries class in module %s' % bmodule)
    return factory(name = name, **kwargs)
