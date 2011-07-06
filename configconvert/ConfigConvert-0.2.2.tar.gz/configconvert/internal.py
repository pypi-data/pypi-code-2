# These three functions are from Paste and are released under an MIT license
# but the docs don't list any specific terms. They are copied here to avoid
# a large dependency.

def eval_import(s):
    """
    Import a module, or import an object from a module.

    A module name like ``foo.bar:baz()`` can be used, where
    ``foo.bar`` is the module, and ``baz()`` is an expression
    evaluated in the context of that module.  Note this is not safe on
    arbitrary strings because of the eval.
    """
    if ':' not in s:
        return simple_import(s)
    module_name, expr = s.split(':', 1)
    module = import_module(module_name)
    obj = eval(expr, module.__dict__)
    return obj

def simple_import(s):
    """
    Import a module, or import an object from a module.

    A name like ``foo.bar.baz`` can be a module ``foo.bar.baz`` or a
    module ``foo.bar`` with an object ``baz`` in it, or a module
    ``foo`` with an object ``bar`` with an attribute ``baz``.
    """
    parts = s.split('.')
    module = import_module(parts[0])
    name = parts[0]
    parts = parts[1:]
    last_import_error = None
    while parts:
        name += '.' + parts[0]
        try:
            module = import_module(name)
            parts = parts[1:]
        except ImportError, e:
            last_import_error = e
            break
    obj = module
    while parts:
        try:
            obj = getattr(module, parts[0])
        except AttributeError:
            raise ImportError(
                "Cannot find %s in module %r (stopped importing modules with error %s)" % (parts[0], module, last_import_error))
        parts = parts[1:]
    return obj

def import_module(s):
    """
    Import a module.
    """
    try:
        mod = __import__(s)
    except ImportError, e:
        raise ImportError(str(e)+', failed when trying to import %r'%s)
    parts = s.split('.')
    for part in parts[1:]:
        mod = getattr(mod, part)
    return mod


