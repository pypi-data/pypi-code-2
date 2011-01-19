import logging
from threading import local

from formencode import Invalid

from .utils import Bunch

log = logging.getLogger(__name__)

widget_context = None

def _setup_globals():
    global widget_context
    widget_context = WidgetContext()

class WidgetContext(object):
    '''Proxy for the 'ew.widget_context' value in the
    WSGI environ for the current request
    '''

    def __init__(self):
        self._local=  local()

    def set_up(self, environ):
        self._local.environ = environ
        self._local.environ['ew.widget_context'] = Bunch(
            widget=None,
            validation_error=None,
            render_context=None,
            resource_manager=None)

    def tear_down(self):
        del self._local.environ['ew.widget_context']
        del self._local.environ

    def _current(self):
        if not hasattr(self._local, 'environ'):
            self.set_up({})
        return self._local.environ['ew.widget_context']

    def __getattr__(self, name):
        return getattr(self._current(), name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            super(WidgetContext, self).__setattr__(name, value)
        else:
            setattr(self._current(), name, value)

def validator(func):
    def inner(*a, **kw):
        try:
            return func(*a, **kw)
        except Invalid, inv:
            widget_context.validation_error=inv
            raise
    inner.__name__ = 'validator(%s)' % func.__name__
    return inner

_setup_globals()
