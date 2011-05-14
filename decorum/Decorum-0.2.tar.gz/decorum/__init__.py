class Decorator(object):
    """
    A decorator class that tries to unify writing decorators
    for use with and without arguments.
    """

    keep_attrs = True
    
    def __init__(self, *args, **kwargs):
        """
        Unifies decorator interface, so that it can be used
        both with and without arguments the same way.
          
        """
        if args and callable(args[0]):
            # used as decorator without being called
            self.init()
            self._wrapped = self.__call__(args[0])
        else:
            # used as decorator and called
            self.init(*args, **kwargs)

    def __call__(self, f=None, *args, **kwargs):
        """Uses `wrap` to handle decoration, restores `__doc__` and `__name__`"""
        if not callable(f):
            return self._wrapped(f, *args, **kwargs)
        else:
            wrapped = self.wraps(f)
            if self.keep_attrs:
                wrapped.__doc__ = f.__doc__
                wrapped.__name__ = f.__name__
            return wrapped

    def wraps(self, f):
        """Wraps the function and returns it"""
        return f

    def init(self, *args, **kwargs):
        """Passed any possible arguments to decorator"""
        pass
