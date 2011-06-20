from kforge.handlers.base import *
from kforge.handlers.apachecodes import *

class ModWsgiHandler(BaseHandler):

    def authoriseRequest(self):
        raise Exception, "Method not implemented on %s" % self.__class__

    def getDefaultResponseCode(self):
        return HTTP_INTERNAL_SERVER_ERROR
       
    def getRequestMethod(self):
        return self.getRequestEnvironVar('REQUEST_METHOD')

    def getRefererUri(self):
        return self.getRequestEnvironVar('HTTP_REFERER')

    def getRequestUri(self):
        return self.getRequestEnvironVar('REQUEST_URI')

    def getRequestUserAgent(self):
        return self.getRequestEnvironVar('HTTP_USER_AGENT')

    def getRequestEnvironVar(self, name):
        return self.environ.get(name, '')


class WsgiCheckPasswordHandler(ModWsgiHandler):

    def __call__(self, environ, user, password):
        self.environ = environ
        self.requestuser = user
        self.requestpassword = password
        return self.authorise()

    def authoriseRequest(self):
        if not self.validateRequestUri():
            return False
        self.initAuthuserFromBasicPrompt()
        if self.isAccessAuthorised():
            self.environ['REMOTE_USER'] = self.authuser
            return True
        else:
            return False

    def getRequestCredentials(self):
        return (self.requestuser, self.requestpassword)

    def hasCookies(self):
        return False

class WsgiAccessControlHandler(ModWsgiHandler):

    redirectUri = None
    statusMessages = {
        200: "200 OK",
        302: "302 Found",
        401: "401 Unauthorized",
        500: "500 Internal Server Error",
    }

    def __init__(self, application=None):
        self.wsgiApplication = application
        self.session = None

    def __call__(self, environ, start_response):
        self.environ = environ
        status = self.authorise()
        headers = [
            ("Content-type", "text/html; charset=iso-8859-1"),
        ]
        body = ""
        if status == HTTP_OK:
            if self.wsgiApplication:
                return self.wsgiApplication(environ, start_response)
            else:
                body = "Access was authorised, but there is no protected application."
        elif self.isCookieClient():
            if self.redirectUri:
                headers.append(("Location", self.redirectUri))
        elif status == HTTP_UNAUTHORIZED:
            realm = self.application.dictionary[HTTP_AUTH_REALM]
            realm = realm.encode('utf8')
            headers.append(('WWW-Authenticate', 'Basic realm="%s Restricted Area"' % realm))
        start_response(self.createWsgiStatus(status), headers)
        return [body]

    def createWsgiStatus(self, code):
        return self.statusMessages[code]

    def authoriseRequest(self):
        if self.isCookieClient():
            if not self.validateRequestUri():
                # Apache configuration should mean we never get here.
                self.setRedirect()
                return HTTP_MOVED_TEMPORARILY
            elif self.isLoginUri():
                self.setRedirect('login')
                return HTTP_MOVED_TEMPORARILY
            elif self.isLogoutUri():
                self.setRedirect('logout')
                return HTTP_MOVED_TEMPORARILY
            self.initAuthuserFromCookie()
            if self.isAccessAuthorised():
                if self.session:
                    self.setRequestUser(self.authuser.name)
                return HTTP_OK
            else:
                self.setRedirect()
                return HTTP_MOVED_TEMPORARILY
        else:
            if not self.validateRequestUri():
                return HTTP_NOT_FOUND
            self.initAuthuserFromDictionary()
            if self.isAccessAuthorised():
                return HTTP_OK
            else:
                if 'HTTP_AUTHORIZATION' in self.environ:
                    self.initAuthuserFromBasicPrompt()
                    if self.isAccessAuthorised():
                        self.setRequestUser(self.authuser.name)
                        return HTTP_OK
                    else:
                        return HTTP_UNAUTHORIZED
                else:
                    return HTTP_UNAUTHORIZED

    def getRequestCredentials(self):
        if 'HTTP_AUTHORIZATION' in self.environ:
            authorization = self.environ['HTTP_AUTHORIZATION']
            (authmeth, auth) = authorization.split(' ', 1)
            if authmeth.lower() != 'basic':
                msg = "Needs basic auth (not '%s')." % authmeth
                raise Exception, msg
            auth = auth.strip().decode('base64')
            username, password = auth.split(':', 1)
            return username, password
        elif self.session:
            return self.session.person.name, None

    def setRequestRedirect(self, uri):
        self.redirectUri = uri

    def setRequestUser(self, userName):
        if type(userName) == unicode:
            userName = userName.encode('utf-8')
        if type(userName) != str:
            userName = str(userName)
        self.environ['REMOTE_USER'] = userName
        
    def hasCookies(self):
        return self.environ.has_key('HTTP_COOKIE')

    def getCookies(self):
        return self.environ['HTTP_COOKIE']


class GitWsgiAccessControlHandler(WsgiAccessControlHandler):

    def getActionName(self):
        uri = self.normalizeUriPath(self.getRequestUri())
        if 'receive-pack' not in uri and 'upload-pack' in uri:
            # Client is doing clone or pull.
            return 'Read'
        elif 'receive-pack' in uri and 'upload-pack' not in uri:
            # Client is doing push.
            return 'Update'
        else:
            import kforge.url
            service = self.getServiceFromUri(uri)
            urlBuilder = kforge.url.UrlScheme()
            uriService = urlBuilder.getServicePath(service).strip('/')
            if uriService == uri.strip('/'):
                return super(GitWsgiAccessControlHandler, self).getActionName()
            raise Exception, "Can't identify action name from request URI: %s" % uri


