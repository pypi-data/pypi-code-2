import os
import sys
from pycukes import *

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