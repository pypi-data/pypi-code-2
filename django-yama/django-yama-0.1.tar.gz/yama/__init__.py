''' Yet another menuing application for Django '''
VERSION = (0, 1)

def get_version(join=' ', short=False):
    """
    Return the version of this package as a string.

    The version number is built from a ``VERSION`` tuple, which should consist
    of integers, or trailing version information (such as 'alpha', 'beta' or
    'final'). For example:

    >>> VERSION = (2, 0, 6)
    >>> get_version()
    '2.0.6'

    >>> VERSION = (1, 0, 'beta', 2)
    >>> get_version()
    '1.0 beta 2'

    Use the ``join`` argument to join the version elements by an alternate
    character to the default ``' '``. This is useful when building a distutils
    setup module::

        from this_package import get_version

        setup(
            version=get_version(join='-'),
            # ...
        )

    Use the ``short`` argument to get the version number without trailing
    version information.

    """
    version = []
    number = []
    remainder = []
    for i, bit in enumerate(VERSION):
        if isinstance(bit, int):
            number.append(str(bit))
        else:
            remainder = [str(bit) for bit in VERSION[i:]] 
            break
    if number:
        version.append('.'.join(number))
    if not short:
        if remainder == ['alpha', 0]:
            version.append('pre-alpha')
        elif 'final' not in remainder:
            version.extend(remainder)
    return join.join(version)

def autodiscover():
    """
    A ripoff of django.contrib.admin.autodiscover
    """
    import imp
    from django.conf import settings

    for app in settings.INSTALLED_APPS:
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue

        try:
            imp.find_module('menu', app_path)
        except ImportError:
            continue

        __import__("%s.menu" % app)
