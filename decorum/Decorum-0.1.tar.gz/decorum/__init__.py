class decorator(object):
    def __init__(self, *args, **kwargs):
        """
        Unifies decorator interface, so that it can be used
        both with and without arguments the same way.
          
        """
        if args and callable(args[0]):
            # used as decorator without being called
            self.init()
            self._call_wrapper(args[0])
        else:
            # used as decorator and called
            self.init(*args, **kwargs)
            self.__call__ = self._call_wrapper # replace call

    def _call_wrapper(self, f, keep_attrs=True):
        """Replaces __call__ and allows returns wrapped function"""
        wrapped = self.wraps(f)
        if keep_attrs:
            wrapped.__doc__ = f.__doc__
            wrapped.__name__ = f.__name__
        return wrapped

    def wraps(self, f):
        """Wraps the function and returns it"""
        return f

    def init(self, *args, **kwargs):
        """Passed any possible arguments to decorator"""
        pass
