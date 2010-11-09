import os
import sys
from pycukes import *
import pycukes

BASE_DIR = os.path.dirname(__file__)

EXTASY_STEP_PATHS = [
    'step_definitions'
]

def _extasy_find_all_steps_modules( dirs, suffix = '.py' ):
    all_modules = []
    for dirname in dirs:
        sys.path.insert(0, dirname)
        modules = [__import__(filename[:-3]) for filename in os.listdir(dirname)
                                           if filename.endswith(suffix)]
        all_modules += modules
        del sys.path[0]
    return all_modules
    
    
def extasy_find_steps_modules( dirname ):
    modules = _extasy_find_all_steps_modules( [ '%s/%s' % ( BASE_DIR, x ) for x in EXTASY_STEP_PATHS ] )
    if( os.path.exists( dirname ) ):
        modules += _extasy_find_all_steps_modules( [dirname], 'steps.py' )
    return modules
    
    
def extasy_find_hook_steps( filename ):
    dirname = os.path.dirname( filename ) + '/support'
    pyname = os.path.basename( filename )[:-6] + '_hooks'
    hook_meths = {}
    
    if not os.path.exists( dirname + '/' + pyname + '.py' ):
        return hook_meths
    
    sys.path.insert(0, dirname)
    module = __import__( pyname )
    del sys.path[0]
    
    for name in [ '_before_alls', '_after_alls', '_before_eachs', '_after_eachs' ]:
        hook_meths[ name ] = []
        steps = getattr(module, name, [])
        hook_meths[ name ].extend([step[1] for step in steps])
        
    return hook_meths
    
    
def pycukes_find_hook_steps(name, dirname):
    sys.path.insert(0, dirname)
    modules = [__import__(filename[:-3]) for filename in os.listdir(dirname)
                                           if filename == 'env.py' ]
    del sys.path[0]
    before_all_meths = []
    for module in modules:
        steps = getattr(module, name, [])
        before_all_meths.extend([step[1] for step in steps])
    return before_all_meths
    
pycukes.finder._find_hook_steps = pycukes_find_hook_steps