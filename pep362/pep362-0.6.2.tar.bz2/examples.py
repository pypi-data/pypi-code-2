from pep362 import Signature

def quack_check(fxn):
    """Decorator to verify arguments and return value quack as they should.

    Positional arguments.
    >>> @quack_check
    ... def one_arg(x:int): pass
    ... 
    >>> one_arg(42)
    >>> one_arg('a')
    Traceback (most recent call last):
        ...
    TypeError: 'a' does not quack like a <class 'int'>


    *args
    >>> @quack_check
    ... def var_args(*args:int): pass
    ... 
    >>> var_args(*[1,2,3])
    >>> var_args(*[1,'b',3])
    Traceback (most recent call last):
        ...
    TypeError: *args contains a a value that does not quack like a <class 'int'>

    **kwargs
    >>> @quack_check
    ... def var_kw_args(**kwargs:int): pass
    ... 
    >>> var_kw_args(**{'a': 1})
    >>> var_kw_args(**{'a': 'A'})
    Traceback (most recent call last):
        ...
    TypeError: **kwargs contains a value that does not quack like a <class 'int'>

    Return annotations.
    >>> @quack_check
    ... def returned(x) -> int: return x
    ... 
    >>> returned(42)
    42
    >>> returned('a')
    Traceback (most recent call last):
        ...
    TypeError: the return value 'a' does not quack like a <class 'int'>

    """
    # Get the signature; only needs to be calculated once.
    sig = Signature(fxn)
    def check(*args, **kwargs):
        # Find out the variable -> value bindings.
        bindings = sig.bind(*args, **kwargs)
        # Check *args for the proper quack.
        try:
            duck = sig.var_annotations[sig.var_args]
        except KeyError:
            pass
        else:
            # Check every value in *args.
            for value in bindings[sig.var_args]:
                if not isinstance(value, duck):
                    raise TypeError("*%s contains a a value that does not "
                                    "quack like a %r" %
                                    (sig.var_args, duck))
            # Remove it from the bindings so as to not check it again.
            del bindings[sig.var_args]
        # **kwargs.
        try:
            duck = sig.var_annotations[sig.var_kw_args]
        except (KeyError, AttributeError):
            pass
        else:
            # Check every value in **kwargs.
            for value in bindings[sig.var_kw_args].values():
                if not isinstance(value, duck):
                    raise TypeError("**%s contains a value that does not "
                                    "quack like a %r" %
                                    (sig.var_kw_args, duck))
            # Remove from bindings so as to not check again.
            del bindings[sig.var_kw_args]
        # For each remaining variable ...
        for var, value in bindings.items():
            # See if an annotation was set.
            try:
                duck = sig[var].annotation
            except AttributeError:
                continue
            # Check that the value quacks like it should.
            if not isinstance(value, duck):
                raise TypeError('%r does not quack like a %s' % (value, duck))
        else:
            # All the ducks quack fine; let the call proceed.
            returned = fxn(*args, **kwargs)
            # Check the return value.
            try:
                if not isinstance(returned, sig.return_annotation):
                    raise TypeError('the return value %r does not quack like '
                                    'a %r' % (returned,
                                        sig.return_annotation))
            except AttributeError:
                pass
            return returned
    # Full-featured version would set function metadata.
    return check


if __name__ == '__main__':
    import doctest
    doctest.testmod()
