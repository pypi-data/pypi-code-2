import os, re

_installed_apps = None
def installed_apps():
    '''
    Return list of installed applications.
    '''
    global _installed_apps
    if not _installed_apps:
        _installed_apps = [app for app in os.listdir('.') if os.path.isdir(app) and not app.startswith("_") and app != 'gae']
    return _installed_apps

def monkey_patch(name, bases, namespace):
    assert len(bases) == 1, 'Exactly one base class is required'
    base = bases[0]
    for name, value in namespace.iteritems():
        if name not in ('__metaclass__', '__module__'):
            setattr(base, name, value)
    return base

def prepare_url_vars(url_address, var_pattern="(?P<\\1>[^/]+)"):
    '''
    Return url address with replaced variables to regex pattern.
    
    Examples:
        blog/(blog_slug)/new -> blog/%(blog_slug)s/new
        blog/category-(category_id:number) -> blog/category:(?P<category_slug>[0-9]+)
    '''
    return re.sub("(\([a-z][a-z0-9_]*(:[a-z]+)\))", lambda x: re.sub("(.*)", var_pattern, x.group()), url_address).replace(" ", "")
