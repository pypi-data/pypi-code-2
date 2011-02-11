import datetime
import sys
import logging
import tempfile
from pprint import PrettyPrinter
from StringIO import StringIO
from traceback import format_exc
from os import path
import site

def hwapp(environ, start_response):
    start_response('200 OK', [('content-type', 'text/html')])
    return ['Hello world from ISAPIWSGIHelper!']

def excapp(environ, start_response):
    raise ValueError('testing exception handling')

### Middleware
class ExceptionCatcher(object):
    def __init__(self, basedir, app):
        self.app = app
        self.logfile = path.join(basedir, 'isapi-wsgi-helper.log')

    def htmlmsg(self, log_ok):
        html = """
                <h1>OOPS...ISAPIWSGIHelper caught an exception</h1>
                <p>The exception occured during a request to the WSGI application.</p>
            """
        if log_ok:
            html += """
            <p>Check isapi-wsgi\isapi-wsgi-helper.log for exception details.</p>
            """
        else:
            html += """
            <p>Please make isapi-wsgi\isapi-wsgi-helper.log writeable
            by the web server user and exception details will be written to the log.</p>
            """
        return html

    def writetolog(self, trace, environ):
        envstr = PrettyPrinter().pformat(environ)
        syspath = PrettyPrinter().pformat(sys.path)
        logmsg = '%s %s\n\n== TRACE ==\n\n%s\n\n== ENVIRON ==\n\n%s\n\n== SYS.PATH ==\n\n%s\n\n'\
             % (datetime.datetime.now(), '#'*100, trace, envstr, syspath)

        try:
            with open(self.logfile, 'ab') as fh:
                fh.write(logmsg)
            return True
        except:
            return False

    def __call__(self, environ, start_response):
        try:
            return self.app(environ, start_response)
        except Exception, e:
            log_ok = self.writetolog(format_exc(), environ)
            # leave as 200 OK otherwise IIS shows the default 500 page, not our
            # HTML
            start_response('200 OK', [('content-type', 'text/html')])
            return [self.htmlmsg(log_ok)]

## Other
def prepend_site_dir(basepath, *joinparts):
    """
        like sys.addsitedir() but gives the added directory preference
        over system directories.

        basepath: the path you want to add to sys.path.  If its a
            a file, the parent directory will be used.

        *joinparts: (optional) additional path parts that will be joined
            to basepath to get the real path added to SYS.PATH.  The final paths
            will be normalized for dots and slash direction before being added.
    """

    # let the user be lazy and send a file, we will convert to parent directory
    # of file
    if path.isfile(basepath):
        basepath = path.dirname(basepath)

    path_to_prepend = path.abspath(path.join(basepath, *joinparts))
    sys.path.insert(0, path_to_prepend)
