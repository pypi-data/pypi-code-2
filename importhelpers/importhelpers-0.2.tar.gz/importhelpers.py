def dotted(name):
    """Import python object from dotted path string.

    eg: dotted('package.module.function')

    """
    mod, attr = name.split('.'), []
    obj = None
    while mod:
        try:
            obj = __import__('.'.join(mod), {}, {}, [''])
        except ImportError, e:
            attr.insert(0, mod.pop())
        else:
            for a in attr:
                try:
                    obj = getattr(obj, a)
                except AttributeError, e:
                    raise ImportError('could not get attribute %s from %s'
                        ' -> %s (%r)' % (a, '.'.join(mod), '.'.join(attr),
                        obj))
            return obj
    raise ImportError('could not import %s' % name)


def preferential(name, *morenames):
    """return first import that can be imported successfully.

    eg: preferential('lxml.etree', 'cElementTree',
        'elementtree.ElementTree', 'xml.etree.ElementTree')

    """
    if not isinstance(name, (list, tuple)):
        name = [name]
    names = list(name) + list(morenames)
    while names:
        name = names.pop(0)
        try:
            return dotted(name)
        except ImportError, e:
            pass
    raise ImportError('could not satisfy any imports.')
