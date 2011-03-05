#!/usr/bin/env python
"""
Module DECOTOOLS -- Decorator Functions and Factories
Sub-Package STDLIB of Package PLIB
Copyright (C) 2008-2011 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from plib.stdlib.func import wraps


def test_required(test_func, fail_func):
    """General pattern for decorators with pretest and failure functions.
    
    Parameters:
    
        ``test_func`` is called with the same arguments as the decorated
            function; it must return a true value for the decorated function
            to be called.
        
        ``fail_func`` is called with the same arguments as the decorated
            function if ``test_func`` returns a false value.
    
    Example, similar to a simple web app user login use case::
    
        >>> users = ['alice', 'bob']
        >>> def test_user(username):
        ...     return username in users
        ... 
        >>> def failed_user(username):
        ...     return username + " is not a known user."
        ... 
        >>> login_required = test_required(test_user, failed_user)
        >>> @login_required
        ... def user_login(username):
        ...     return username + " is logged in."
        ... 
        >>> user_login('alice')
        'alice is logged in.'
        >>> user_login('bob')
        'bob is logged in.'
        >>> user_login('charlie')
        'charlie is not a known user.'
        >>> 
    """
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if test_func(*args, **kwargs):
                return f(*args, **kwargs)
            return fail_func(*args, **kwargs)
        return decorated_function
    return decorator


def merge_dict(target, source):
    """Merges source into target."""
    merges = dict((key, value) for key, value in source.iteritems()
        if key not in target)
    target.update(merges)


def decorator_prep_result(prep_func=None, result_func=None,
        *d_args, **d_kwargs):
    """General pattern for decorators with preparation and result functions.
    
    Parameters:
    
    - ``prep_func`` will be passed the ``d_args`` and ``d_kwargs`` passed to
      the decorator, and should return a tuple ``(args, kwargs)``, where
      ``args`` and ``kwargs`` are positional and keyword arguments to be
      passed to the result function; or, it can return ``None`` (the default
      if it is a procedure and doesn't explicitly return a value), in which
      case the ``d_args`` and ``d_kwargs`` will be passed on unchanged to
      the result function (this is expected to be the common case).
      
    - ``result_func`` will be passed the positional and keyword arguments that
      result from processing by ``prep_func`` above, and by the decorated
      function itself, which can return a ``dict`` of keyword arguments that
      will be used to update those coming from ``prep_func``.
    
    Examples, similar to a simple web app templating use case:
    
    - The simplest usage is a decorated function that does nothing, all of
      the work is in the decorator itself; this usage is for arguments that
      are known at import time::
    
        >>> def render_template(filename):
        ...     return "Template rendered: " + filename
        ... 
        >>> def templated(filename):
        ...     return decorator_prep_result(None, render_template, filename)
        ... 
        >>> @templated("test.html")
        ... def test():
        ...     pass
        ... 
        >>> test()
        'Template rendered: test.html'
    
    - Alternatively, we can pass arguments by having the decorated function
      return a dict, if the arguments are only known at run time::
    
        >>> def templated_alt():
        ...     return decorator_prep_result(None, render_template)
        ... 
        >>> @templated_alt()
        ... def test_alt(filename):
        ...     return dict(filename=filename)
        ... 
        >>> test_alt("test.html")
        'Template rendered: test.html'
    
    - Be careful not to pass the same argument both ways, however::
    
        >>> @templated("test1.html")
        ... def test_bad(filename):
        ...     return dict(filename=filename)
        ...
        >>> test_bad("test2.html")
        Traceback (most recent call last):
         ...
        TypeError: render_template() got multiple values for keyword argument 'filename'
    
    - We can also pass keyword arguments via the decorator at import time::
    
        >>> def templated_kwd(filename):
        ...     return decorator_prep_result(None, render_template, filename=filename)
        ... 
        >>> @templated_kwd(filename="test.html")
        ... def test_kwd():
        ...     pass
        ... 
        >>> test_kwd()
        'Template rendered: test.html'
    
    - But remember that keyword arguments passed via the decorator will be
      overridden by keyword arguments passed at runtime via the decorated
      function (note the difference from the case above where we passed the
      argument positionally in the decorator)::
    
        >>> @templated_kwd(filename="notseen.html")
        ... def test_kwd_update(filename):
        ...     return dict(filename=filename)
        ... 
        >>> test_kwd_update("test.html")
        'Template rendered: test.html'
    
    - Also, we can add a preparation function to massage arguments passed to
      the decorator; but note that this is less convenient because we have to
      return a tuple ``(args, kwargs)``::
    
        >>> import os
        >>> def massage_path(basename):
        ...     return (basename.replace("test", "massaged"),), {}
        ... 
        >>> def templated_prep(basename):
        ...     return decorator_prep_result(massage_path, render_template, basename)
        ... 
        >>> @templated_prep("test.html")
        ... def test_prep():
        ...     pass
        ... 
        >>> test_prep()
        'Template rendered: massaged.html'
    
    - And, of course, we can combine all of the above (note that we pass all
      arguments as keyword arguments to ensure no collisions, since the
      ordering is reversed--the template argument comes after the decorated
      function argument in the result function's signature)::
    
        >>> def render_template_in_dir(dirname, basename):
        ...     return "Template rendered: " + basename + " in directory " + dirname
        ... 
        >>> def massage_basename(basename):
        ...     return (), {'basename': basename.replace("test", "massaged")}
        ... 
        >>> def templated_combined(basename):
        ...     return decorator_prep_result(massage_basename, render_template_in_dir, basename=basename)
        ... 
        >>> @templated_combined("test.html")
        ... def test_combined(dirname):
        ...     return dict(dirname=dirname)
        ... 
        >>> test_combined("testdir")
        'Template rendered: massaged.html in directory testdir'
    
    - Finally, note that, even though ``result_func`` is given a default
      argument in the function signature above, we can't omit it (we shouldn't
      want to anyway, since if we could it would just be a roundabout way of
      forming a closure)::
    
        >>> @decorator_prep_result()
        ... def test_no_result_func():
        ...     pass
        ... 
        >>> test_no_result_func()
        Traceback (most recent call last):
         ...
        TypeError: 'NoneType' object is not callable
        >>> 
    """
    
    def decorator(f):
        p = None
        if prep_func:
            p = prep_func(*d_args, **d_kwargs)
            if p:
                r_args, f_kwargs = p
        if not p:
            r_args, f_kwargs = d_args, d_kwargs.copy()
        @wraps(f)
        def decorated_function(*args, **kwargs):
            r_kwargs = (f(*args, **kwargs) or {})
            merge_dict(r_kwargs, f_kwargs)
            return result_func(*r_args, **r_kwargs)
        return decorated_function
    return decorator


def decorator_with_f(f, decorator):
    """Allows decorator to be used either with or without parameters.
    
    For example, let's modify the above web app login use case::
    
    - We set up a login_required decorator we can use with no arguments,
      as above (note that we have to give defaults for all arguments, and
      in particular the first argument ``f`` must default to ``None``)::
    
        >>> users = ['alice', 'bob']
        >>> def test_user(username):
        ...     return username in users
        ... 
        >>> def failed_user(username):
        ...     return username + " is not a known user."
        ... 
        >>> def login_required(f=None, test=test_user, failed=failed_user):
        ...     return decorator_with_f(f, test_required(test, failed))
        ... 
        >>> @login_required
        ... def user_login(username):
        ...     return username + " is logged in."
        ... 
        >>> user_login('alice')
        'alice is logged in.'
        >>> user_login('bob')
        'bob is logged in.'
        >>> user_login('charlie')
        'charlie is not a known user.'
    
    - But now we can use the same decorator with different functions, by
      passing them as arguments (note that they have to be keyword arguments
      so that the first, function argument will be ``None``, as needed)::
    
        >>> admins = ['alice']
        >>> def test_admin(username):
        ...     return username in admins
        ... 
        >>> def failed_admin(username):
        ...     if test_user(username):
        ...         return username + " is not an admin."
        ...     return failed_user(username)
        ... 
        >>> @login_required(test=test_admin, failed=failed_admin)
        ... def admin_login(username):
        ...     return username + " is logged in as an admin."
        ... 
        >>> admin_login('alice')
        'alice is logged in as an admin.'
        >>> admin_login('bob')
        'bob is not an admin.'
        >>> admin_login('charlie')
        'charlie is not a known user.'
        >>> 
    """
    
    if f is None:
        return decorator
    return decorator(f)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
