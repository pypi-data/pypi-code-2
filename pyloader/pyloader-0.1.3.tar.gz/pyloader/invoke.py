import inspect
import sys
from cast import cast
from cast import str2args

def strcall(obj, *args, **kwargs):
    """call a thing with string arguments"""

    # TODO:
    # could have modes for casting, at least for intrinsic types
    # - optimistic: try to cast everything '1' -> 1
    # - argument-based: only cast what's in the arguments
    # - you should also be able to provide your own casts
    # This will have to be made an object in order to actually do this
    # so that these parameters may be provided to __init__
    
    inspected = obj
    if inspect.isclass(obj):
        inspected = obj.__init__ # inspect the ctor
    try:
        argspec = inspect.getargspec(inspected)
    except TypeError:
        argspec = None
    if argspec is None:
        args = [cast(i) for i in args]
        kwargs = dict([(key, cast(value)) for key, value in kwargs.items()])
    else:
        # TODO: get values from argspec
        args = [cast(i) for i in args]
        kwargs = dict([(key, cast(value)) for key, value in kwargs.items()])
    return obj(*args, **kwargs)

def call(obj, **kwargs):
    """
    call an object with the subset of kwargs appropriate to the object.
    this assumes that the obj does not take **kwargs
    """
    inspected = obj
    if inspect.isclass(obj):
        inspected = obj.__init__ # inspect the ctor
        args = inspect.getargspec(inspected).args[1:]
    else:
        args = inspect.getargspec(obj).args[:]
    kw = {} # kwargs to invoke obj with
    for arg in args:
        if arg in kwargs:
            kw[arg] = kwargs[arg]
    return obj(**kw)

def main(args=sys.argv[1:]):
    """CLI entry point"""
    from loader import load
    from optparse import OptionParser
    usage = '%prog Object arg1=value1 arg2=value2 [...]'
    description = 'invoke an Object given string arguments'
    parser = OptionParser(usage=usage, description=description)
    if not args:
        parser.print_usage()
        parser.exit()
    obj = load(args[0])
    obj_args, obj_kwargs = str2args(' '.join(args[1:]))
    print strcall(obj, *obj_args, **obj_kwargs)

if __name__ == '__main__':
    main()
