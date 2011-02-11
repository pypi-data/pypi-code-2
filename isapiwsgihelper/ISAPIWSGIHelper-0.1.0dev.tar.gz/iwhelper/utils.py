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

class FixEnv(object):
    """

    """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):

        # SCRIPT_NAME & PATH_INFO don't seem to be calculated correctly, lets just
        # use PATH_INFO.
        environ['PATH_INFO_ORIG'] = environ['PATH_INFO']
        environ['SCRIPT_NAME_ORIG'] = environ['SCRIPT_NAME']
        if environ['PATH_INFO'] == '':
            environ['PATH_INFO'] = environ['SCRIPT_NAME']
        else:
            environ['PATH_INFO'] = environ['SCRIPT_NAME'].rstrip('/') + '/' + environ['PATH_INFO'].lstrip('/')
        environ['SCRIPT_NAME'] = ''

        # fix wsgi.url_scheme
        if environ['SERVER_PORT'] == '443':
            environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)

class FixWsgiInput(object):
    """
       PyISAPIe doesn't provide a readline() on wsgi.input and
       isapi-wsgi can't handle readline(value), we fix that here
    """
    def __init__(self, app, strsize=102400, maxsize=20971520):
        self.app = app
        self.strsize = strsize
        self.maxsize = maxsize

    def __call__(self, environ, start_response):

        environ['wsgi.input'] = self.replaceinput(environ)
        return self.app(environ, start_response)

    def replaceinput(self, environ):
        logging.debug('replace input')
        try:
            length = int(environ.get('CONTENT_LENGTH', 0) or 0)
        except ValueError:
            length = 0

        # if no content or content is too big, return
        if length == 0 or length > self.maxsize:
            if length > self.maxsize:
                logging.info('file too big, max size %d bytes but size %d' % (self.maxsize, length))
                environ['fixwsgiinput.error'] = 'file too big, max size %d bytes' % self.maxsize
                environ['CONTENT_LENGTH'] = 0
            return StringIO('')
        logging.debug('starting temp file')
        if length > self.strsize or length < 0:
            logging.debug('using file for temp storage')
            f = tempfile.TemporaryFile()
            if length < 0:
                f.write(environ['wsgi.input'].read())
            else:
                copy_len = length
                while copy_len > 0:
                    chunk = environ['wsgi.input'].read(min(copy_len, 4096))
                    if not chunk:
                        environ['fixwsgiinput.error'] = 'request body truncated'
                        environ['CONTENT_LENGTH'] = 0
                        return StringIO('')
                    f.write(chunk)
                    copy_len -= len(chunk)
            f.seek(0)
            return f
        logging.debug('using StringIO for temp storage')
        return StringIO(environ['wsgi.input'].read(length))

## Other
def prependsitedir(projdir, *args):
    """
        like sys.addsitedir() but gives the added directory preference
        over system directories.  The paths will be normalized for dots and
        slash direction before being added to the path.

        projdir: the path you want to add to sys.path.  If its a
            a file, the parent directory will be added

        *args: additional directories relative to the projdir to add
            to sys.path.
    """
    libpath = None

    # let the user be lazy and send a file, we will convert to parent directory
    # of file
    if path.isfile(projdir):
        projdir = path.dirname(projdir)

    projdir = path.abspath(projdir)

    # any args are considered paths that need to be joined to the
    # projdir to get to the correct directory.
    libpaths = []
    for lpath in args:
        libpaths.append(path.join(projdir, path.normpath(lpath)))

    # add the path to sys.path with preference over everything that currently
    # exists in sys.path
    syspath_orig = set(sys.path)
    site.addsitedir(projdir)
    for lpath in libpaths:
        site.addsitedir(lpath)
    syspath_after = set(sys.path)
    new_paths = list(syspath_after.difference(syspath_orig))
    sys.path = new_paths + sys.path
