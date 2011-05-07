import settings

def tag(bucket, doc):
    def wrapped(inner, **options):
        options[bucket] = 1
        if 'name' in options:
            inner.__name__ = inner.name = options.pop('name')
        if 'doc' in options:
            inner.__doc__ = inner.doc = options.pop('doc')
        for i in options.items():
            setattr(inner, *i)
        inner.__doc__ = inner.doc = '%s\n%s' % (inner.__doc__, ''.join([
            'This is a :ref:`%s tag<%s-tags>`. ' % (tag, tag)
            for tag in settings.TAG_TYPES
            if hasattr(inner, tag) and
              str(inner.__doc__).find('This is a :ref:`%s' % tag)==-1]))
        return inner
    wrapped.__doc__ = doc
    return wrapped

block = tag('block', """
Block tag function decorator

Syntax::

    def my_tag_function(context, nodelist, [*vars], [**tag_options]):
        return nodelist.render(context)
    my_tag_function.block = True
""")
comparison = tag('comparison',"""
Comparison tag function decorator

Syntax::

    def my_comparison([*vars], [**tag_options]):
        return True
    my_comparison.comparison = True
""")
comparison.__doc__
filter = tag('filter',"""
Filter tag function decorator

Syntax::

    def my_filter(value, arg):
        return value
    my_filter.filter = True
""")
function = tag('function',"""
Function tag function decorator

Syntax::

    def foo[*args], [**kwargs]):
        return args, kwargs
    foo.function = True
""")
