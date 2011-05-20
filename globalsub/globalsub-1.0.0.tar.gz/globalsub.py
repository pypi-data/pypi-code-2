"""Global substitution for Python unit tests

Provides substitution in all dictionaries throughout the interpreter,
this includes references held by objects and modules.  Restores those 
references which were replaced (only), i.e. you can re-use the objects
you used as substitutions after restoring.

Sample usage:

    >>> import globalsub
    >>> def x():
    ...     print 'x'
    ... 
    >>> def y():
    ...     print 'y'
    ... 
    >>> globalsub.subs( x, y )
    <function y at 0xb7470a04>
    >>> x()
    y
    >>> y()
    y
    >>> globalsub.restore( x )
    <function x at 0xb74709cc>
    >>> x()
    x
    >>> y()
    y

Sample usage for a test case:

    import globalsub as gs
    class Test(TestCase):
        def setUp( self ):
            gs.subs( somefunction, replacement )
        def tearDown( self ):
            gs.restore( somefunction )

Notes:

    * if you need to refer to the original function, store a
      reference in a list or tuple
    * you cannot currently subs built-in or other fixed-attribute 
      objects, this could be fixed, but isn't yet a priority.
"""
__version__ = '1.0.0'
import gc,logging 
log = logging.getLogger(__name__)

__all__ = ['subs','restore']

def subs( function, replacement=None ):
    """Replaces function in all namespaces with replacement 
    
    function -- function to replace
    replacement -- if provided, is used as the replacement object,
        otherwise a function returning None is constructed 
    
    Used to stub out functionality globally, this function uses 
    global_replace to find all references to function and replace 
    them with replacement.  Use restore( replacement ) to restore 
    function references.
    
    Note: 
    
        Only references in namespaces will be replaced, references 
        in anything other than dictionaries will not be replaced.
    
    returns replacement
    """
    if replacement is None:
        def replacement( *args, **named ):
            return None 
        replacement.__name__ = function.__name__
    if function is not replacement:
        replacement.__is_subs__ = True
        replacement.original = [function,replace_filter(replacement)]
        global_replace( function, replacement )
        return replacement 
    return function

def restore( function ):
    """Restore previously subs'd function in all namespaces
    
    function -- the replacement function which was substituted 

    returns resolved function
    """
    new,filters = resolve( function )
    if new is not function:
        global_replace( function, new, filters )
    return new

def resolve( function ):
    """Find original function from the function or subs of the function"""
    seen = {}
    all_filters = {}
    while hasattr( function, 'original' ):
        seen[id(function)] = True 
        function,filters = function.original
        all_filters.update( filters )
        if id(function) in seen:
            log.warn( 'Seem to have created a substituation loop on %s', function)
            break
    return function,all_filters

def global_replace(remove, install, filter=None):
    """Replace object 'remove' with object 'install' on all dictionaries.
    """
    for referrer in gc.get_referrers(remove):
        if (
            type(referrer) is dict and
            referrer.get("_mocker_replace_", True)
        ):
            for key, value in list(referrer.iteritems()):
                if value is remove:
                    if filter and id(referrer) in filter:
                        if key in filter[id(referrer)]:
                            continue # next key 
                    referrer[key] = install
def replace_filter( install ):
    """Calculate which instances should *not* be replaced"""
    blocks = {} # id(referrer): keys_to_skip
    for referrer in gc.get_referrers(install):
        if (
            type(referrer) is dict and
            referrer.get("_mocker_replace_", True)
        ):
            for key, value in list(referrer.iteritems()):
                if value is install:
                    blocks.setdefault(id(referrer),[]).append( key )
    return blocks 
