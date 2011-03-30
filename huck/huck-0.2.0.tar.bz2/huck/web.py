# Copyright 2011 Silas Sewell
# Copyright 2010 Alexandre Fiori
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from twisted.internet import defer
from twisted.internet import protocol
from twisted.python import failure
from twisted.python import log
from huck import __version__
from huck import http
from huck import template
from huck import utils

import base64
import binascii
import calendar
import Cookie
import cStringIO
import datetime
import email.utils
import functools
import gzip
import hashlib
import httplib
import hmac
import locale
import mimetypes
import os.path
import re
import stat
import sys
import time
import types
import urllib
import urlparse
import uuid
import struct

class RequestHandler(object):
    """Subclass this class and define get() or post() to make a handler.

    If you want to support more methods than the standard GET/HEAD/POST, you
    should override the class variable SUPPORTED_METHODS in your
    RequestHandler class.
    """
    SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PUT")

    no_keep_alive = False
    def __init__(self, application, request, transforms=None):
        self.application = application
        self.request = request
        self._headers_written = False
        self._finished = False
        self._auto_finish = True
        self._transforms = transforms or []
        self.ui = utils.objectify((n, self._ui_method(m)) for n, m in
                     application.ui_methods.iteritems())
        self.ui["modules"] = utils.objectify((n, self._ui_module(n, m)) for n, m in
                                application.ui_modules.iteritems())
        self.clear()
        self.request.connection.no_keep_alive = self.no_keep_alive

    @property
    def settings(self):
        return self.application.settings

    def head(self, *args, **kwargs):
        raise HTTPError(405)

    def get(self, *args, **kwargs):
        raise HTTPError(405)

    def post(self, *args, **kwargs):
        raise HTTPError(405)

    def delete(self, *args, **kwargs):
        raise HTTPError(405)

    def put(self, *args, **kwargs):
        raise HTTPError(405)

    def prepare(self):
        """Called before the actual handler method.

        Useful to override in a handler if you want a common bottleneck for
        all of your requests.
        """
        pass

    def on_connection_close(self, *args, **kwargs):
        """Called when the connection is closed.

        You may override this to clean up resources associated with
        long-lived connections.
        """
        pass

    def clear(self):
        """Resets all headers and content for this response."""
        self._headers = {
            "Server": "Huck/" + __version__,
            "Content-Type": "text/html; charset=UTF-8",
        }
        if not self.request.supports_http_1_1():
            if self.request.headers.get("Connection") == "Keep-Alive":
                self.set_header("Connection", "Keep-Alive")
        self._write_buffer = []
        self._status_code = 200

    def set_status(self, status_code):
        """Sets the status code for our response."""
        if status_code not in httplib.responses:
            raise Exception('Invalid status code: %s' % status_code)
        self._status_code = status_code

    def set_header(self, name, value):
        """Sets the given response header name and value.

        If a datetime is given, we automatically format it according to the
        HTTP specification. If the value is not a string, we convert it to
        a string. All header values are then encoded as UTF-8.
        """
        if isinstance(value, datetime.datetime):
            t = calendar.timegm(value.utctimetuple())
            value = email.utils.formatdate(t, localtime=False, usegmt=True)
        elif isinstance(value, (float, int, long)):
            value = str(value)
        elif isinstance(value, basestring):
            value = utils.utf8.encode(value)
            # If \n is allowed into the header, it is possible to inject
            # additional headers or split the request. Also cap length to
            # prevent obviously erroneous values.
            safe_value = re.sub(r"[\x00-\x1f]", " ", value)[:4000]
            if safe_value != value:
                raise ValueError("Unsafe header value %r", value)
        else:
            raise TypeError("Unknown header type %r", value)
        self._headers[name] = value

    @property
    def cookies(self):
        """A dictionary of Cookie.Morsel objects."""
        if not hasattr(self, "_cookies"):
            self._cookies = Cookie.BaseCookie()
            if "Cookie" in self.request.headers:
                try:
                    self._cookies.load(self.request.headers["Cookie"])
                except:
                    self.clear_all_cookies()
        return self._cookies

    def get_cookie(self, name, default=None):
        """Gets the value of the cookie with the given name, else default."""
        if name in self.cookies:
            return self.cookies[name].value
        return default

    def set_cookie(self, name, value, domain=None, expires=None, path="/",
                   expires_days=None, **kwargs):
        """Sets the given cookie name/value with the given options.

        Additional keyword arguments are set on the Cookie.Morsel
        directly.
        See http://docs.python.org/library/cookie.html#morsel-objects
        for available attributes.
        """
        name = utils.utf8.encode(name)
        value = utils.utf8.encode(value)
        if re.search(r"[\x00-\x20]", name + value):
            # Don't let us accidentally inject bad stuff
            raise ValueError("Invalid cookie %r: %r" % (name, value))
        if not hasattr(self, "_new_cookies"):
            self._new_cookies = []
        new_cookie = Cookie.BaseCookie()
        self._new_cookies.append(new_cookie)
        new_cookie[name] = value
        if domain:
            new_cookie[name]["domain"] = domain
        if expires_days is not None and not expires:
            expires = datetime.datetime.utcnow() + datetime.timedelta(
                days=expires_days)
        if expires:
            timestamp = calendar.timegm(expires.utctimetuple())
            new_cookie[name]["expires"] = email.utils.formatdate(
                timestamp, localtime=False, usegmt=True)
        if path:
            new_cookie[name]["path"] = path
        for k, v in kwargs.iteritems():
            new_cookie[name][k] = v
        return value

    def clear_cookie(self, name, path="/", domain=None):
        """Deletes the cookie with the given name."""
        expires = datetime.datetime.utcnow() - datetime.timedelta(days=365)
        self.set_cookie(name, value="", path=path, expires=expires,
                        domain=domain)

    def clear_all_cookies(self):
        """Deletes all the cookies the user sent with this request."""
        for name in self.cookies.iterkeys():
            self.clear_cookie(name)

    def set_secure_cookie(self, name, value, expires_days=30, **kwargs):
        """Signs and timestamps a cookie so it cannot be forged.

        You must specify the 'cookie_secret' setting in your Application
        to use this method. It should be a long, random sequence of bytes
        to be used as the HMAC secret for the signature.

        To read a cookie set with this method, use get_secure_cookie().
        """
        self.set_cookie(name, self.create_signed_value(name, value),
                        expires_days=expires_days, **kwargs)

    def create_signed_value(self, name, value):
        """Signs and timestamps a string so it cannot be forged.

        Normally used via set_secure_cookie, but provided as a separate
        method for non-cookie uses.  To decode a value not stored
        as a cookie use the optional value argument to get_secure_cookie.
        """
        timestamp = str(int(time.time()))
        value = base64.b64encode(value)
        signature = self._cookie_signature(name, value, timestamp)
        value = "|".join([value, timestamp, signature])
        return value

    def get_secure_cookie(self, name, value=None):
        """Returns the given signed cookie if it validates, or None.
        """
        if value is None:
            value = self.get_cookie(name)
        if not value:
            return
        parts = value.split("|")
        if len(parts) != 3:
            return
        signature = self._cookie_signature(name, parts[0], parts[1])
        if not _time_independent_equals(parts[2], signature):
            log.err("Invalid cookie signature %r" % value)
            return
        timestamp = int(parts[1])
        if timestamp < time.time() - 31 * 86400:
            log.err("Expired cookie %r" % value)
            return
        if timestamp > time.time() + 31 * 86400:
            # _cookie_signature does not hash a delimiter between the
            # parts of the cookie, so an attacker could transfer trailing
            # digits from the payload to the timestamp without altering the
            # signature.  For backwards compatibility, sanity-check timestamp
            # here instead of modifying _cookie_signature.
            logging.warning("Cookie timestamp in future; possible tampering %r", value)
            return
        if parts[1].startswith("0"):
            logging.warning("Tampered cookie %r", value)
        try:
            return base64.b64decode(parts[0])
        except:
            return

    def _cookie_signature(self, *parts):
        self.require_setting("cookie_secret", "secure cookies")
        hash = hmac.new(self.application.settings["cookie_secret"],
                        digestmod=hashlib.sha1)
        for part in parts:
            hash.update(part)
        return hash.hexdigest()

    def redirect(self, url, permanent=False):
        """Sends a redirect to the given (optionally relative) URL."""
        if self._headers_written:
            raise Exception("Cannot redirect after headers have been written")
        self.set_status(301 if permanent else 302)
        # Remove whitespace
        url = re.sub(r"[\x00-\x20]+", "", utils.utf8.encode(url))
        self.set_header("Location", urlparse.urljoin(self.request.uri, url))
        self.finish()

    def write(self, chunk):
        """Writes the given chunk to the output buffer.

        To write the output to the network, use the flush() method below.

        If the given chunk is a dictionary, we write it as JSON and set
        the Content-Type of the response to be text/javascript.
        """
        assert not self._finished
        if isinstance(chunk, dict):
            chunk = utils.json.encode(chunk)
            self.set_header("Content-Type", "text/javascript; charset=UTF-8")
        chunk = utils.utf8.encode(chunk)
        self._write_buffer.append(chunk)

    def render(self, template_name, **kwargs):
        """Renders the template with the given arguments as the response."""
        html = self.render_string(template_name, **kwargs)

        # Insert the additional JS and CSS added by the modules on the page
        js_embed = []
        js_files = []
        css_embed = []
        css_files = []
        html_heads = []
        for module in getattr(self, "_active_modules", {}).itervalues():
            embed_part = module.embedded_javascript()
            if embed_part:
                js_embed.append(utils.utf8.encode(embed_part))
            file_part = module.javascript_files()
            if file_part:
                if isinstance(file_part, basestring):
                    js_files.append(file_part)
                else:
                    js_files.extend(file_part)
            embed_part = module.embedded_css()
            if embed_part:
                css_embed.append(utils.utf8.encode(embed_part))
            file_part = module.css_files()
            if file_part:
                if isinstance(file_part, basestring):
                    css_files.append(file_part)
                else:
                    css_files.extend(file_part)
            head_part = module.html_head()
            if head_part:
                html_heads.append(utils.utf8.encode(head_part))
        if js_files:
            # Maintain order of JavaScript files given by modules
            paths = []
            unique_paths = set()
            for path in js_files:
                if not path.startswith("/") and not path.startswith("http:"):
                    path = self.static_url(path)
                if path not in unique_paths:
                    paths.append(path)
                    unique_paths.add(path)
            js = ''.join('<script src="' + utils.xhtml.escape(p) +
                         '" type="text/javascript"></script>'
                         for p in paths)
            sloc = html.rindex('</body>')
            html = html[:sloc] + js + '\n' + html[sloc:]
        if js_embed:
            js = '<script type="text/javascript">\n//<![CDATA[\n' + \
                '\n'.join(js_embed) + '\n//]]>\n</script>'
            sloc = html.rindex('</body>')
            html = html[:sloc] + js + '\n' + html[sloc:]
        if css_files:
            paths = set()
            for path in css_files:
                if not path.startswith("/") and not path.startswith("http:"):
                    paths.add(self.static_url(path))
                else:
                    paths.add(path)
            css = ''.join('<link href="' + utils.xhtml.escape(p) + '" '
                          'type="text/css" rel="stylesheet"/>'
                          for p in paths)
            hloc = html.index('</head>')
            html = html[:hloc] + css + '\n' + html[hloc:]
        if css_embed:
            css = '<style type="text/css">\n' + '\n'.join(css_embed) + \
                '\n</style>'
            hloc = html.index('</head>')
            html = html[:hloc] + css + '\n' + html[hloc:]
        if html_heads:
            hloc = html.index('</head>')
            html = html[:hloc] + ''.join(html_heads) + '\n' + html[hloc:]

        self.finish(html)

    def render_string(self, template_name, **kwargs):
        """Generate the given template with the given arguments.

        We return the generated string. To generate and write a template
        as a response, use render() above.
        """
        # If no template_path is specified, use the path of the calling file
        template_path = self.application.settings.get("template_path")
        if not template_path:
            frame = sys._getframe(0)
            web_file = frame.f_code.co_filename
            while frame.f_code.co_filename == web_file:
                frame = frame.f_back
            template_path = os.path.dirname(frame.f_code.co_filename)
        if not getattr(RequestHandler, "_templates", None):
            RequestHandler._templates = {}
        if template_path not in RequestHandler._templates:
            RequestHandler._templates[template_path] = template.Loader(
                template_path)
        t = RequestHandler._templates[template_path].load(template_name)
        args = dict(
            handler=self,
            request=self.request,
            current_user=self.current_user,
            locale=self.locale,
            _=self.locale.translate,
            static_url=self.static_url,
            xsrf_form_html=self.xsrf_form_html,
            reverse_url=self.application.reverse_url
        )
        args.update(self.ui)
        args.update(kwargs)
        return t.generate(**args)

    def flush(self, include_footers=False):
        """Flushes the current output buffer to the nextwork."""
        chunk = "".join(self._write_buffer)
        self._write_buffer = []
        if not self._headers_written:
            self._headers_written = True
            for transform in self._transforms:
                self._headers, chunk = transform.transform_first_chunk(
                    self._headers, chunk, include_footers)
            headers = self._generate_headers()
        else:
            for transform in self._transforms:
                chunk = transform.transform_chunk(chunk, include_footers)
            headers = ""

        # Ignore the chunk and only write the headers for HEAD requests
        if self.request.method == "HEAD":
            if headers:
                self.request.write(headers)
            return

        if headers or chunk:
            self.request.write(headers + chunk)

    def notifyFinish(self):
        return self.request.notifyFinish()

    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        assert not self._finished
        if chunk is not None:
            self.write(chunk)

        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if not self._headers_written:
            if self._status_code == 200 and self.request.method == "GET":
                hasher = hashlib.sha1()
                for part in self._write_buffer:
                    hasher.update(part)
                etag = '"%s"' % hasher.hexdigest()
                inm = self.request.headers.get("If-None-Match")
                if inm and inm.find(etag) != -1:
                    self._write_buffer = []
                    self.set_status(304)
                else:
                    self.set_header("Etag", etag)
            if "Content-Length" not in self._headers:
                content_length = sum(len(part) for part in self._write_buffer)
                self.set_header("Content-Length", content_length)

        self.flush(include_footers=True)
        self.request.finish()
        self._log()
        self._finished = True

    def send_error(self, status_code=500, **kwargs):
        """Sends the given HTTP error code to the browser.

        We also send the error HTML for the given error code as returned by
        get_error_html. Override that method if you want custom error pages
        for your application.
        """
        if self._headers_written:
            log.err("Cannot send error response after headers written")
            if not self._finished:
                self.finish()
            return
        self.clear()
        self.set_status(status_code)

        e = kwargs.get("exception")
        if isinstance(e, HTTPAuthenticationRequired):
            args = ",".join(['%s="%s"' % (k, v) for k, v in e.kwargs.items()])
            self.set_header("WWW-Authenticate", "%s %s" % (e.auth_type, args))

        message = self.get_error_html(status_code, **kwargs)
        self.finish(message)

    def get_error_html(self, status_code, **kwargs):
        """Override to implement custom error pages.

        If this error was caused by an uncaught exception, the
        exception object can be found in kwargs e.g. kwargs['exception']
        """
        return "<html><title>%(code)d: %(message)s</title>" \
               "<body>%(code)d: %(message)s</body></html>" % {
            "code": status_code,
            "message": httplib.responses[status_code],
        }

    @property
    def locale(self):
        """The local for the current session.

        Determined by either get_user_locale, which you can override to
        set the locale based on, e.g., a user preference stored in a
        database, or get_browser_locale, which uses the Accept-Language
        header.
        """
        if not hasattr(self, "_locale"):
            self._locale = self.get_user_locale()
            if not self._locale:
                self._locale = self.get_browser_locale()
                assert self._locale
        return self._locale

    def get_user_locale(self):
        """Override to determine the locale from the authenticated user.

        If None is returned, we use the Accept-Language header.
        """
        return

    def get_browser_locale(self, default="en_US"):
        """Determines the user's locale from Accept-Language header.

        See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.4
        """
        if "Accept-Language" in self.request.headers:
            languages = self.request.headers["Accept-Language"].split(",")
            locales = []
            for language in languages:
                parts = language.strip().split(";")
                if len(parts) > 1 and parts[1].startswith("q="):
                    try:
                        score = float(parts[1][2:])
                    except (ValueError, TypeError):
                        score = 0.0
                else:
                    score = 1.0
                locales.append((parts[0], score))
            if locales:
                locales.sort(key=lambda (l, s): s, reverse=True)
                codes = [l[0] for l in locales]
                return locale.get(*codes)
        return locale.get(default)

    @property
    def current_user(self):
        """The authenticated user for this request.

        Determined by either get_current_user, which you can override to
        set the user based on, e.g., a cookie. If that method is not
        overridden, this method always returns None.

        We lazy-load the current user the first time this method is called
        and cache the result after that.
        """
        if not hasattr(self, "_current_user"):
            self._current_user = self.get_current_user()
        return self._current_user

    def get_current_user(self):
        """Override to determine the current user from, e.g., a cookie."""
        return

    def get_login_url(self):
        """Override to customize the login URL based on the request.

        By default, we use the 'login_url' application setting.
        """
        self.require_setting("login_url", "@huck.web.authenticated")
        return self.application.settings["login_url"]

    @property
    def xsrf_token(self):
        """The XSRF-prevention token for the current user/session.

        To prevent cross-site request forgery, we set an '_xsrf' cookie
        and include the same '_xsrf' value as an argument with all POST
        requests. If the two do not match, we reject the form submission
        as a potential forgery.

        See http://en.wikipedia.org/wiki/Cross-site_request_forgery
        """
        if not hasattr(self, "_xsrf_token"):
            token = self.get_cookie("_xsrf")
            if not token:
                token = binascii.b2a_hex(uuid.uuid4().bytes)
                expires_days = 30 if self.current_user else None
                self.set_cookie("_xsrf", token, expires_days=expires_days)
            self._xsrf_token = token
        return self._xsrf_token

    def check_xsrf_cookie(self):
        """Verifies that the '_xsrf' cookie matches the '_xsrf' argument.

        To prevent cross-site request forgery, we set an '_xsrf'
        cookie and include the same value as a non-cookie
        field with all POST requests. If the two do not match, we
        reject the form submission as a potential forgery.

        The _xsrf value may be set as either a form field named _xsrf
        or in a custom HTTP header named X-XSRFToken or X-CSRFToken
        (the latter is accepted for compatibility with Django).

        See http://en.wikipedia.org/wiki/Cross-site_request_forgery
        """
        token = (self.request.post("_xsrf") or
                 self.request.headers.get("X-Xsrftoken") or
                 self.request.headers.get("X-Csrftoken"))
        if not token:
            raise HTTPError(403, "'_xsrf' argument missing from POST")
        if self.xsrf_token != token:
            raise HTTPError(403, "XSRF cookie does not match POST argument")

    def xsrf_form_html(self):
        """An HTML <input/> element to be included with all POST forms.

        It defines the _xsrf input value, which we check on all POST
        requests to prevent cross-site request forgery. If you have set
        the 'xsrf_cookies' application setting, you must include this
        HTML within all of your HTML forms.

        See check_xsrf_cookie() above for more information.
        """
        return '<input type="hidden" name="_xsrf" value="' + \
            utils.xhtml.escape(self.xsrf_token) + '"/>'

    def static_url(self, path):
        """Returns a static URL for the given relative static file path.

        This method requires you set the 'static_path' setting in your
        application (which specifies the root directory of your static
        files).

        We append ?v=<signature> to the returned URL, which makes our
        static file handler set an infinite expiration header on the
        returned content. The signature is based on the content of the
        file.

        If this handler has a "include_host" attribute, we include the
        full host for every static URL, including the "http://". Set
        this attribute for handlers whose output needs non-relative static
        path names.
        """
        self.require_setting("static_path", "static_url")
        if not hasattr(RequestHandler, "_static_hashes"):
            RequestHandler._static_hashes = {}
        hashes = RequestHandler._static_hashes
        if path not in hashes:
            try:
                f = open(os.path.join(
                    self.application.settings["static_path"], path))
                hashes[path] = hashlib.md5(f.read()).hexdigest()
                f.close()
            except:
                log.err("Could not open static file %r" % path)
                hashes[path] = None
        base = self.request.protocol + "://" + self.request.host \
            if getattr(self, "include_host", False) else ""
        static_url_prefix = self.settings.get('static_url_prefix', '/static/')
        if hashes.get(path):
            return base + static_url_prefix + path + "?v=" + hashes[path][:5]
        else:
            return base + static_url_prefix + path

    def async_callback(self, callback, *args, **kwargs):
        """Wrap callbacks with this if they are used on asynchronous requests.

        Catches exceptions and properly finishes the request.
        """
        if callback is None:
            return
        if args or kwargs:
            callback = functools.partial(callback, *args, **kwargs)
        def wrapper(*args, **kwargs):
            try:
                return callback(*args, **kwargs)
            except Exception, e:
                if self._headers_written:
                    log.err("Exception after headers written: %s" % str(e))
                else:
                    self._handle_request_exception(e)
        return wrapper

    def require_setting(self, name, feature="this feature"):
        """Raises an exception if the given app setting is not defined."""
        if not self.application.settings.get(name):
            raise Exception("You must define the '%s' setting in your "
                            "application to use %s" % (name, feature))

    def reverse_url(self, name, *args):
        return self.application.reverse_url(name, *args)

    def _execute(self, transforms, *args, **kwargs):
        """Executes this request with the given output transforms."""
        self._transforms = transforms
        try:
            if self.request.method not in self.SUPPORTED_METHODS:
                raise HTTPError(405)
            # If XSRF cookies are turned on, reject form submissions without
            # the proper cookie
            if self.request.method not in ("GET", "HEAD", "OPTIONS") and \
               self.application.settings.get("xsrf_cookies"):
                self.check_xsrf_cookie()
            self.prepare()
            if not self._finished:
                function = getattr(self, self.request.method.lower())
                d = defer.maybeDeferred(function, *args, **kwargs)
                d.addCallback(self._execute_success)
                d.addErrback(self._execute_failure)
                self.notifyFinish().addCallback(self.on_connection_close)
        except Exception, e:
            self._handle_request_exception(e)

    def _execute_success(self, ign):
        if self._auto_finish and not self._finished:
            self.finish()

    def _execute_failure(self, err):
        self._handle_request_exception(err)

    def _generate_headers(self):
        lines = [self.request.version + " " + str(self._status_code) + " " +
                 httplib.responses[self._status_code]]
        lines.extend(["%s: %s" % (n, v) for n, v in self._headers.iteritems()])
        for cookie_dict in getattr(self, "_new_cookies", []):
            for cookie in cookie_dict.values():
                lines.append("Set-Cookie: " + cookie.OutputString(None))
        return "\r\n".join(lines) + "\r\n\r\n"

    def _log(self):
        request_time = 1000.0 * self.request.request_time()
        log.msg("%d %s %.2fms" % (self._status_code, self._request_summary(), request_time))

    def _request_summary(self):
        return '%s %s (%s)' % (
            self.request.method,
            self.request.uri,
            self.request.remote_ip,
        )

    def _handle_request_exception(self, e):
        try:
            if isinstance(e.value, (HTTPError, HTTPAuthenticationRequired)):
                e = e.value
        except:
            pass

        if isinstance(e, (HTTPError, HTTPAuthenticationRequired)):
            if e.status_code not in httplib.responses:
                log.err("Bad HTTP status code: %d" % e.status_code)
                self.send_error(500, exception=e)
            else:
                self.send_error(e.status_code, exception=e)
        else:
            log.err(e)
            log.err("Uncaught exception %s :: %r" % (self._request_summary(), self.request))
            self.send_error(500, exception=e)

    def _ui_module(self, name, module):
        def render(*args, **kwargs):
            if not hasattr(self, "_active_modules"):
                self._active_modules = {}
            if name not in self._active_modules:
                self._active_modules[name] = module(self)
            rendered = self._active_modules[name].render(*args, **kwargs)
            return rendered
        return render

    def _ui_method(self, method):
        return lambda *args, **kwargs: method(self, *args, **kwargs)


def asynchronous(method):
    """Wrap request handler methods with this if they are asynchronous.

    If this decorator is given, the response is not finished when the
    method returns. It is up to the request handler to call self.finish()
    to finish the HTTP request. Without this decorator, the request is
    automatically finished when the get() or post() method returns.

       class MyRequestHandler(web.RequestHandler):
           @web.asynchronous
           def get(self):
              http = httpclient.AsyncHTTPClient()
              http.fetch("http://friendfeed.com/", self._on_download)

           def _on_download(self, response):
              self.write("Downloaded!")
              self.finish()

    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        self._auto_finish = False
        return method(self, *args, **kwargs)
    return wrapper


def removeslash(method):
    """Use this decorator to remove trailing slashes from the request path.

    For example, a request to '/foo/' would redirect to '/foo' with this
    decorator. Your request handler mapping should use a regular expression
    like r'/foo/*' in conjunction with using the decorator.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.path.endswith("/"):
            if self.request.method in ("GET", "HEAD"):
                uri = self.request.path.rstrip("/")
                # don't try to redirect '/' to ''
                if uri:
                    if self.request.query:
                        uri += "?" + self.request.query
                    self.redirect(uri)
                    return
            else:
                raise HTTPError(404)
        return method(self, *args, **kwargs)
    return wrapper


def addslash(method):
    """Use this decorator to add a missing trailing slash to the request path.

    For example, a request to '/foo' would redirect to '/foo/' with this
    decorator. Your request handler mapping should use a regular expression
    like r'/foo/?' in conjunction with using the decorator.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.request.path.endswith("/"):
            if self.request.method == "GET":
                uri = self.request.path + "/"
                if self.request.query:
                    uri += "?" + self.request.query
                self.redirect(uri)
                return
            raise HTTPError(404)
        return method(self, *args, **kwargs)
    return wrapper


class Application(protocol.ServerFactory):
    """A collection of request handlers that make up a web application.

    Instances of this class are callable and can be passed directly to
    Server to serve the application:

        application = web.Application([
            (r"/", MainPageHandler),
        ])
        reactor.listenTCP(8080, application)
        reactor.run()

    The constructor for this class takes in a list of (regexp, request_class)
    tuples. When we receive requests, we iterate over the list in order and
    instantiate an instance of the first request class whose regexp matches
    the request path.

    Each tuple can contain an optional third element, which should be a
    dictionary if it is present. That dictionary is passed as keyword
    arguments to the contructor of the handler. This pattern is used
    for the StaticFileHandler below:

        application = web.Application([
            (r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
        ])

    We support virtual hosts with the add_handlers method, which takes in
    a host regular expression as the first argument:

        application.add_handlers(r"www\.myhost\.com", [
            (r"/article/([0-9]+)", ArticleHandler),
        ])

    You can serve static files by sending the static_path setting as a
    keyword argument. We will serve those files from the /static/ URI,
    and we will serve /favicon.ico and /robots.txt from the same directory.
    """
    protocol = http.Server

    def __init__(self, handlers=None, default_host="", transforms=None, **settings):
        if transforms is None:
            self.transforms = []
            if settings.get("gzip"):
                self.transforms.append(GZipContentEncoding)
            self.transforms.append(ChunkedTransferEncoding)
        else:
            self.transforms = transforms
        self.handlers = []
        self.named_handlers = {}
        self.default_host = default_host
        self.settings = utils.objectify(settings)
        self.ui_modules = {}
        self.ui_methods = {}
        self._load_ui_modules(settings.get("ui_modules", {}))
        self._load_ui_methods(settings.get("ui_methods", {}))
        if self.settings.get("static_path"):
            path = self.settings["static_path"]
            handlers = list(handlers or [])
            static_url_prefix = settings.get("static_url_prefix",
                                             "/static/")
            handlers = [
                (re.escape(static_url_prefix) + r"(.*)", StaticFileHandler,
                 dict(path=path)),
                (r"/(favicon\.ico)", StaticFileHandler, dict(path=path)),
                (r"/(robots\.txt)", StaticFileHandler, dict(path=path)),
            ] + handlers
        if handlers:
            self.add_handlers(".*$", handlers)

    def add_handlers(self, host_pattern, host_handlers):
        """Appends the given handlers to our handler list."""
        if not host_pattern.endswith("$"):
            host_pattern += "$"
        handlers = []
        self.handlers.append((re.compile(host_pattern), handlers))

        for spec in host_handlers:
            if type(spec) is type(()):
                assert len(spec) in (2, 3)
                pattern = spec[0]
                handler = spec[1]
                if len(spec) == 3:
                    kwargs = spec[2]
                else:
                    kwargs = {}
                spec = URLSpec(pattern, handler, kwargs)
            handlers.append(spec)
            if spec.name:
                self.named_handlers[spec.name] = spec

    def add_transform(self, transform_class):
        """Adds the given OutputTransform to our transform list."""
        self.transforms.append(transform_class)

    def _get_host_handlers(self, request):
        host = request.host.lower().split(':')[0]
        for pattern, handlers in self.handlers:
            if pattern.match(host):
                return handlers
        # Look for default host if not behind load balancer (for debugging)
        if "X-Real-Ip" not in request.headers:
            for pattern, handlers in self.handlers:
                if pattern.match(self.default_host):
                    return handlers
        return

    def _load_ui_methods(self, methods):
        if type(methods) is types.ModuleType:
            self._load_ui_methods(dict((n, getattr(methods, n))
                                       for n in dir(methods)))
        elif isinstance(methods, list):
            for m in methods:
                self._load_ui_methods(m)
        else:
            for name, fn in methods.iteritems():
                if not name.startswith("_") and hasattr(fn, "__call__") \
                   and name[0].lower() == name[0]:
                    self.ui_methods[name] = fn

    def _load_ui_modules(self, modules):
        if type(modules) is types.ModuleType:
            self._load_ui_modules(dict((n, getattr(modules, n))
                                       for n in dir(modules)))
        elif isinstance(modules, list):
            for m in modules:
                self._load_ui_modules(m)
        else:
            assert isinstance(modules, dict)
            for name, cls in modules.iteritems():
                try:
                    if issubclass(cls, UIModule):
                        self.ui_modules[name] = cls
                except TypeError:
                    pass

    def __call__(self, request):
        """Called by Server to execute the request."""
        transforms = [t(request) for t in self.transforms]
        handler = None
        args = []
        handlers = self._get_host_handlers(request)
        if not handlers:
            handler = RedirectHandler(
                request, "http://" + self.default_host + "/")
        else:
            for spec in handlers:
                match = spec.regex.match(request.path)
                if match:
                    handler = spec.handler_class(self, request, **spec.kwargs)
                    args = match.groups()
                    break
            if not handler:
                handler = ErrorHandler(self, request, 404)

        # In debug mode, re-compile templates and reload static files on every
        # request so you don't need to restart to see changes
        if self.settings.get("debug"):
            RequestHandler._templates = None
            RequestHandler._static_hashes = {}

        handler._execute(transforms, *args)
        return handler

    def reverse_url(self, name, *args):
        """Returns a URL path for handler named `name`

        The handler must be added to the application as a named URLSpec
        """
        if name in self.named_handlers:
            return self.named_handlers[name].reverse(*args)
        raise KeyError("%s not found in named urls" % name)


class HTTPError(Exception):
    """An exception that will turn into an HTTP error response."""
    def __init__(self, status_code, log_message=None, *args):
        self.status_code = status_code
        self.log_message = log_message
        self.args = args

    def __str__(self):
        message = "HTTP %d: %s" % (
            self.status_code, httplib.responses[self.status_code])
        if self.log_message:
            return message + " (" + (self.log_message % self.args) + ")"
        else:
            return message

class HTTPAuthenticationRequired(HTTPError):
    """An exception that will turn into an HTTP Authentication Required response"""
    def __init__(self, auth_type="Basic", realm="Restricted Access", **kwargs):
        self.status_code = 401
        self.log_message = None
        self.auth_type = auth_type
        self.kwargs = kwargs
        self.kwargs["realm"] = realm

class ErrorHandler(RequestHandler):
    """Generates an error response with status_code for all requests."""
    def __init__(self, application, request, status_code):
        RequestHandler.__init__(self, application, request)
        self.set_status(status_code)

    def prepare(self):
        raise HTTPError(self._status_code)


class RedirectHandler(RequestHandler):
    """Redirects the client to the given URL for all GET requests.

    You should provide the keyword argument "url" to the handler, e.g.:

        application = web.Application([
            (r"/oldpath", web.RedirectHandler, {"url": "/newpath"}),
        ])
    """
    def __init__(self, application, request, url, permanent=True):
        RequestHandler.__init__(self, application, request)
        self._url = url
        self._permanent = permanent

    def get(self):
        self.redirect(self._url, permanent=self._permanent)


class StaticFileHandler(RequestHandler):
    """A simple handler that can serve static content from a directory.

    To map a path to this handler for a static data directory /var/www,
    you would add a line to your application like:

        application = web.Application([
            (r"/static/(.*)", web.StaticFileHandler, {"path": "/var/www"}),
        ])

    The local root directory of the content should be passed as the "path"
    argument to the handler.

    To support aggressive browser caching, if the argument "v" is given
    with the path, we set an infinite HTTP expiration header. So, if you
    want browsers to cache a file indefinitely, send them to, e.g.,
    /static/images/myimage.png?v=xxx.
    """
    def __init__(self, application, request, path):
        RequestHandler.__init__(self, application, request)
        self.root = os.path.abspath(path) + os.path.sep

    def head(self, path):
        self.get(path, include_body=False)

    def get(self, path, include_body=True):
        abspath = os.path.abspath(os.path.join(self.root, path))
        if not abspath.startswith(self.root):
            raise HTTPError(403, "%s is not in root static directory", path)
        if not os.path.exists(abspath):
            raise HTTPError(404)
        if not os.path.isfile(abspath):
            raise HTTPError(403, "%s is not a file", path)

        stat_result = os.stat(abspath)
        modified = datetime.datetime.fromtimestamp(stat_result[stat.ST_MTIME])

        self.set_header("Last-Modified", modified)
        if "v" in self.request.get:
            self.set_header("Expires", datetime.datetime.utcnow() + \
                                       datetime.timedelta(days=365*10))
            self.set_header("Cache-Control", "max-age=" + str(86400*365*10))
        else:
            self.set_header("Cache-Control", "public")
        mime_type, encoding = mimetypes.guess_type(abspath)
        if mime_type:
            self.set_header("Content-Type", mime_type)

        # Check the If-Modified-Since, and don't send the result if the
        # content has not been modified
        ims_value = self.request.headers.get("If-Modified-Since")
        if ims_value is not None:
            date_tuple = email.utils.parsedate(ims_value)
            if_since = datetime.datetime.fromtimestamp(time.mktime(date_tuple))
            if if_since >= modified:
                self.set_status(304)
                return

        if not include_body:
            return
        self.set_header("Content-Length", stat_result[stat.ST_SIZE])
        with open(abspath, "r") as f:
            self.write(f.read())


class OutputTransform(object):
    """A transform modifies the result of an HTTP request (e.g., GZip encoding)

    A new transform instance is created for every request. See the
    ChunkedTransferEncoding example below if you want to implement a
    new Transform.
    """
    def __init__(self, request):
        pass

    def transform_first_chunk(self, headers, chunk, finishing):
        return headers, chunk

    def transform_chunk(self, chunk, finishing):
        return chunk


class GZipContentEncoding(OutputTransform):
    """Applies the gzip content encoding to the response.

    See http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.11
    """
    CONTENT_TYPES = set([
        "text/plain", "text/html", "text/css", "text/xml",
        "application/x-javascript", "application/xml", "application/atom+xml",
        "text/javascript", "application/json", "application/xhtml+xml"])
    MIN_LENGTH = 5

    def __init__(self, request):
        self._gzipping = request.supports_http_1_1() and \
            "gzip" in request.headers.get("Accept-Encoding", "")

    def transform_first_chunk(self, headers, chunk, finishing):
        if self._gzipping:
            ctype = headers.get("Content-Type", "").split(";")[0]
            self._gzipping = (ctype in self.CONTENT_TYPES) and \
                (not finishing or len(chunk) >= self.MIN_LENGTH) and \
                (finishing or "Content-Length" not in headers) and \
                ("Content-Encoding" not in headers)
        if self._gzipping:
            headers["Content-Encoding"] = "gzip"
            self._gzip_value = cStringIO.StringIO()
            self._gzip_file = gzip.GzipFile(mode="w", fileobj=self._gzip_value)
            self._gzip_pos = 0
            chunk = self.transform_chunk(chunk, finishing)
            if "Content-Length" in headers:
                headers["Content-Length"] = str(len(chunk))
        return headers, chunk

    def transform_chunk(self, chunk, finishing):
        if self._gzipping:
            self._gzip_file.write(chunk)
            if finishing:
                self._gzip_file.close()
            else:
                self._gzip_file.flush()
            chunk = self._gzip_value.getvalue()
            if self._gzip_pos > 0:
                chunk = chunk[self._gzip_pos:]
            self._gzip_pos += len(chunk)
        return chunk


class ChunkedTransferEncoding(OutputTransform):
    """Applies the chunked transfer encoding to the response.

    See http://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.6.1
    """
    def __init__(self, request):
        self._chunking = request.supports_http_1_1()

    def transform_first_chunk(self, headers, chunk, finishing):
        if self._chunking:
            # No need to chunk the output if a Content-Length is specified
            if "Content-Length" in headers or "Transfer-Encoding" in headers:
                self._chunking = False
            else:
                headers["Transfer-Encoding"] = "chunked"
                chunk = self.transform_chunk(chunk, finishing)
        return headers, chunk

    def transform_chunk(self, block, finishing):
        if self._chunking:
            # Don't write out empty chunks because that means END-OF-STREAM
            # with chunked encoding
            if block:
                block = ("%x" % len(block)) + "\r\n" + block + "\r\n"
            if finishing:
                block += "0\r\n\r\n"
        return block


def authenticated(method):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            if self.request.method == "GET":
                url = self.get_login_url()
                if "?" not in url:
                    url += "?" + urllib.urlencode(dict(next=self.request.uri))
                self.redirect(url)
                return
            raise HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


class UIModule(object):
    """A UI re-usable, modular unit on a page.

    UI modules often execute additional queries, and they can include
    additional CSS and JavaScript that will be included in the output
    page, which is automatically inserted on page render.
    """
    def __init__(self, handler):
        self.handler = handler
        self.request = handler.request
        self.ui = handler.ui
        self.current_user = handler.current_user
        self.locale = handler.locale

    def render(self, *args, **kwargs):
        raise NotImplementedError()

    def embedded_javascript(self):
        """Returns a JavaScript string that will be embedded in the page."""
        return

    def javascript_files(self):
        """Returns a list of JavaScript files required by this module."""
        return

    def embedded_css(self):
        """Returns a CSS string that will be embedded in the page."""
        return

    def css_files(self):
        """Returns a list of JavaScript files required by this module."""
        return

    def html_head(self):
        """Returns a CSS string that will be put in the <head/> element"""
        return

    def render_string(self, path, **kwargs):
        return self.handler.render_string(path, **kwargs)

class URLSpec(object):
    """Specifies mappings between URLs and handlers."""
    def __init__(self, pattern, handler_class, kwargs={}, name=None):
        """Creates a URLSpec.

        Parameters:
        pattern: Regular expression to be matched.  Any groups in the regex
            will be passed in to the handler's get/post/etc methods as
            arguments.
        handler_class: RequestHandler subclass to be invoked.
        kwargs (optional): A dictionary of additional arguments to be passed
            to the handler's constructor.
        name (optional): A name for this handler.  Used by
            Application.reverse_url.
        """
        if not pattern.endswith('$'):
            pattern += '$'
        self.regex = re.compile(pattern)
        self.handler_class = handler_class
        self.kwargs = kwargs
        self.name = name
        self._path, self._group_count = self._find_groups()

    def _find_groups(self):
        """Returns a tuple (reverse string, group count) for a url.

        For example: Given the url pattern /([0-9]{4})/([a-z-]+)/, this method
        would return ('/%s/%s/', 2).
        """
        pattern = self.regex.pattern
        if pattern.startswith('^'):
            pattern = pattern[1:]
        if pattern.endswith('$'):
            pattern = pattern[:-1]

        if self.regex.groups != pattern.count('('):
            # The pattern is too complicated for our simplistic matching,
            # so we can't support reversing it.
            return (None, None)

        pieces = []
        for fragment in pattern.split('('):
            if ')' in fragment:
                paren_loc = fragment.index(')')
                if paren_loc >= 0:
                    pieces.append('%s' + fragment[paren_loc + 1:])
            else:
                pieces.append(fragment)

        return (''.join(pieces), self.regex.groups)

    def reverse(self, *args):
        assert self._path is not None, \
            "Cannot reverse url regex " + self.regex.pattern
        assert len(args) == self._group_count, "required number of arguments "\
            "not found"
        if not len(args):
            return self._path
        return self._path % tuple([str(a) for a in args])

url = URLSpec

def _time_independent_equals(a, b):
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    return result == 0
