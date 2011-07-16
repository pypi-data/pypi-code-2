import isapi_wsgi
from traceback import format_exc
from iwhelper.utils import ErrorApp, ExceptionCatcher, hwapp, FixEnv

try:
    from .appinit import __wsgiapp__ as wsgiapp
    wsgiapp = FixEnv(wsgiapp)
    wsgiapp = ExceptionCatcher(wsgiapp)
except Exception, e:
    wsgiapp = ErrorApp(format_exc())

# The entry points for the ISAPI extension.
def __ExtensionFactory__():
    return isapi_wsgi.ISAPIThreadPoolHandler(wsgiapp)
