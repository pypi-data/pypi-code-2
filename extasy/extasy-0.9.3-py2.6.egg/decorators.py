import extasy
import pycukes
import pyhistorian
import sys

_extasy_hooks = {
    'StartTest' : [],
    'EndTest' : [],
}

def extasy_decorator__init__(self, message, *args):
    self._message = extasy.lang.get( message )
    self._args = args
    self._context = sys._getframe(1)
    self._set_step_attrs(self._context.f_locals)
    step = self.__class__.name
    self._steps = self._context.f_locals['_%ss' % step]
    self._steps.append((None, self._message, self._args))


Given = type( 'Given', (pycukes.Given,), { '__init__' : extasy_decorator__init__ } )
When = type( 'When', (pycukes.When,), { '__init__' : extasy_decorator__init__ } )
Then = type( 'Then', (pycukes.Then,), { '__init__' : extasy_decorator__init__ } )

def StartTest( f ):
    global _extasy_hooks
    _extasy_hooks[ 'StartTest' ].append( f )
    return f
    
def EndTest( f ):
    global _extasy_hooks
    _extasy_hooks[ 'EndTest' ].append( f )
    return f
    
def execute_hooks( name ):
    global _extasy_hooks
    extasy.scope.reset()
    for f in _extasy_hooks[ name ]:
        f( extasy )
        

class BeforeScenario( pyhistorian.Step ):
    name = 'before_each'
    
    def __init__(self, title, *args):
        self._title_to_run = title
        self._args = args
        self._context = sys._getframe(1)
        self._set_step_attrs(self._context.f_locals)
        step = self.__class__.name
        self._steps = self._context.f_locals['_%ss' % step]
        
    def __call__( self, f ):
        def wrapped( context, *args, **kwargs ):
            if context.title == self._title_to_run:
                return f( context, *args, **kwargs )
            
        self._message = wrapped
        self._steps.append((None, self._message, self._args))
        return wrapped
        
class AfterScenario( BeforeScenario ):
    name = 'after_each'