#encoding:utf-8
import httplib, urllib, base64

#Exceptions
class ClientException(Exception):
    pass

class ServerException(Exception):
    pass

class SetCookieException(Exception):
    pass

class SessionIdException(Exception):
    pass

class NotAuthenticatedException(Exception):
    pass

class NotLoginPageException(Exception):
    pass

class ServiceUnreachable(Exception):
    pass

#Classes
class Headers(dict):
    """A convenient subclass of dict to 'objectify' the header of a request."""
    pass

class Parameters(dict):
    """A convenient subclass of dict to 'objectify' parameters sent to the server."""
    def encode(self):    
        return urllib.urlencode(self)

class RemoteConnection(object):
    """Access to services or resources exposed by a remote server.
    
    Developed to correct the logic of 'helmholtz.access_control.views.authenticate_from_facets'.
    Currently, the success of a connection is tested with try ... except construction decorating 
    the function 'urllib2.urlopen'. With this kind of construction the only fact the program could
    actually detect is that the specified resource is not accessible. This poor granularity in 
    exception handling is explained by the loss of the response sent by the remote server. Consequently,
    a better solution should test the response of the server to detect the real kind of exception 
    and make the appropriate action in the program. The use of 'urllib2' has been replaced by the 
    'httplib' one because it exposes to the user the response of the server.
    
    Public parameters:
    
    - protocol : defines if the server is a classic 'http' or a secured 'https' server
    - host : the web address of the django server
    - username : user login
    - password : user password
    - response : httpllib.HTTPResponse object corresponding to the server response
    - access_possible : a flag to materialize the fact that a RemoteServer object has correctly requested the remote resource
    - exceptions : a list of exceptions encountered during connection, for debugging purpose
    
    Internal parameters:
    
    - server : the HTTP(S)Connection object that interacts with the server depending on the selected protocol
               
      NB : The class is in fact a kind of decorator that exposes the 'HTTP(S)Connection.response' parameter
           to user by using the 'response' parameter.
                
    Public methods:
    
    - connect(self,type,url,parameters=Parameters(),headers=Headers(),fail_silently=True): sends a request to the remote server
    
    Internal methods:
    
    - set_connection_type(self): sets django_server parameter to an HTTP or HTTPS Connection object depending on the specified protocol parameter
    - _request(self,type,url,parameters,headers): sends the request and gets the server response
    - request(self,type,url,parameters,headers,fail_silently): decorates _request with an exception detection mechanism.
    
    """
    
    def __init__(self, protocol, host, username=None, password=None):
        assert protocol in ['http', 'https'], 'protocol must be http or https'
        self.protocol = protocol
        self.host = host
        self.server = None
        self.exceptions = {}
        self.response = None
        self.access_possible = False 
        self.request_counter = 0
    
    def report_exceptions(self):
        for request in self.exceptions :
            counter = 0
            print "Request %s :" % (request)
            for exception in self.exceptions[request] :
                print "\t- %s" % (exception) 
                counter += 1
            if counter < 1 :
                print '\t- no exceptions'
    
    def count_exceptions(self):
        return len(self.exceptions[self.request_counter])    
                       
    def set_connection_type(self):
        """Sets django_server parameter to an HTTP or HTTPS Connection object depending on the specified protocol parameter."""
        cls = getattr(httplib, '%sConnection' % (self.protocol.upper()))
        self.server = cls(self.host)
    
    def _request(self, type, url, parameters, headers):
        """Sends the request and gets the server response."""
        self.request_counter += 1
        self.exceptions[self.request_counter] = []
        #ensure that the request will be sent
        if self.response :
            self.response.read() 
        params = parameters.encode()
        self.server.request(type, url, params, headers)
        self.response = self.server.getresponse()
        
    def request(self, type, url, parameters, headers, fail_silently):
        """Decorates _request with an exception detection mechanism.
        
        NB: Currently it only detects a client or server error by generating ClientException or ServerException.   
        """
        self._request(type, url, parameters, headers)
        client_error = (self.response.status >= 400) and (self.response.status < 500)
        server_error = (self.response.status >= 500) and (self.response.status < 600)
        if client_error or server_error :
            if client_error :
                exception = ClientException('%s | Client error: %s (%s)\n\n' % (self.host, self.response.status, self.response.reason)) 
            elif server_error :
                exception = ServerException('%s | Server error: %s (%s)\n\n' % (self.host, self.response.status, self.response.reason))
            if not fail_silently :
                raise exception
            else:
                self.exceptions[self.request_counter].append(exception)
    
    def connect(self, type, url, parameters=Parameters(), headers=Headers(), fail_silently=True):
        """Sends a request to the remote server : 
        
        - type: specify the kind of request; i.e. 'GET', 'POST' or 'PUT' values
        - url: the part of the url that exposes the server resources or services
        - parameters: parameters to transmit encapsulated in a Parameters object
        - headers: headers parameters to transmit encapsulated in a Headers object
        - fail_silently: specifies if an exception is directly raised or stored in 
                         the 'exceptions' property to be analyzed later
                             
        """
        assert isinstance(parameters, Parameters) and isinstance(headers, Headers), 'Please use Parameters and Headers classes to specify parameters and headers transmitted to the server.'        
        if not self.server :
            self.set_connection_type()
        self.request(type, url, parameters, headers, fail_silently)
        if self.count_exceptions() < 1 :
            self.access_possible = True
        else :
            self.access_possible = False

class BasicAuthConnection(RemoteConnection):
    """A RemoteConnection that can manage Basic Authentication from a username and a password."""
    
    def __init__(self, protocol, host, username, password):
        super(BasicAuthConnection, self).__init__(protocol, host)
        self.username = username
        self.password = password
        self.auth_header = None
        self.is_authenticated = False
        raw = "%s:%s" % (self.username, self.password)
        auth = base64.b64encode(raw).strip()
        self.auth_header = Headers(Authorization='Basic %s' % (auth))
    
    def connect(self, type, url, parameters=Parameters(), headers=Headers(), fail_silently=True):
        """Sends a request to the remote server :
        
        - type: specify the kind of request; i.e. 'GET', 'POST' or 'PUT' values
        - url: the part of the url that exposes the server a resource or a service
        - parameters: parameters to transmit encapsulated in a Parameters object
        - headers: headers parameters to transmit encapsulated in a Headers object
        - fail_silently: specifies if an exception is directly raised or stored in 
                         the 'exceptions' property to be analyzed later
        
        """
        headers_copy = Headers(headers)
        if self.auth_header :
            headers_copy.update(self.auth_header)
        super(BasicAuthConnection, self).connect(type, url, parameters, headers_copy, fail_silently)

class DjangoAuthConnection(RemoteConnection):
    """Mimic a classic user login/navigation session to access services contained in a remote django server from python scripts :
    
    Principle : 
    
    The connection is done in two phases : 
    
    - The first one is to go to the login page : This action corresponds to a GET request that tells to django to start 
    a new session and put the new session id in the 'set-cookie' field of the response.  
    
    - The second one is to launch the authentication : This action represents a POST request that sends to django a username,
    a password and other parameters necessary to launch the login process. The request headers contains a 'Cookie' field that
    stores the extracted session id. If the user is authenticated, django deletes the current session, makes a new session 
    for the authenticated user and transmits it in the 'set-cookie' field of the response. The old session id is replaced by
    the new one.
    
    Finally, each time it is necessary to access a service or resource of the django server, the request header must contain 
    a 'Cookie' field containing the authenticated user session id.
    
    Public parameter:
    
    - login_page : url of the login page 
    - is_authenticated : a flag to avoid multiple login
    
    Internal parameter:
    
    - session_parameters : django session identifier
    
    Public methods :
    
    - connect(self,type,url,parameters=Parameters(),headers=Headers(),fail_silently=True): sends a request to the remote server, must be launched after the 'login' function
    
    Internal methods :
    
    - _get_session_parameters(self,response,fail_silently): gets the session id from the response 'set-cookie' header field
    - get_session_parameters(self,response,fail_silently): decorates _get_session_parameters with an exception detection mechanism
    - login(self,url,username,password,parameters=Parameters(),headers=Headers(),fail_silently=True): logs the specified user on the remote server
    """
    
    def __init__(self, protocol, host, login_page, username, password, **login_parameters):
        super(DjangoAuthConnection, self).__init__(protocol, host)
        self.username = username
        self.password = password
        self.login_page = login_page
        self.login_parameters = login_parameters
        self.session_parameters = None
        self.is_authenticated = False
    
    def _get_session_parameters(self, response, fail_silently):
        """Gets the session id from the response 'set-cookie' header field ."""
        session_parameters = None
        cookie_field = self.response.getheader('set-cookie')
        if cookie_field : 
            set_cookie_field = cookie_field.split(';')
            counter = 0
            for parameter in set_cookie_field :
                if 'sessionid' in parameter :
                    session_parameters = set_cookie_field[counter]
                counter += 1
        else:
            exception = SetCookieException("the response doesn't contain the 'set-cookie' field") 
            if not fail_silently :
                raise exception
            else:
                self.exceptions[self.request_counter].append(exception)
        return session_parameters
        
    def get_session_parameters(self, response, fail_silently):
        """Decorates _get_session_parameters with an exception detection mechanism."""    
        session_parameters = self._get_session_parameters(response, fail_silently)
        if not session_parameters :
            exception = SessionIdException("the 'set-cookie' field doesn't contain the session id")
            if not fail_silently :
                raise exception
            else:
                self.exceptions[self.request_counter].append(exception)
        return session_parameters     
    
    def login(self, url, parameters=Parameters(), headers=Headers(), fail_silently=True):
        """Logs the specified user on the remote server :
        
        - url: part of the url corresponding to the login page
        - parameters : complementary parameters to transmit in order to make the authentication process 
        - headers : complementary headers parameters to transmit in order to make the authentication process
        - fail_silently : specifies if an exception is directly raised or stored in the 'exceptions' property to be analyzed later
        
        """
        parameters_copy = Parameters(parameters)
        parameters_copy.update(self.login_parameters)
        parameters_copy.update({'next':url})
        super(DjangoAuthConnection, self).connect('GET', self.login_page, fail_silently=fail_silently)
        session_parameters_1 = self.get_session_parameters(self.response, fail_silently=True)
        if session_parameters_1 : 
            parameters_copy.update({'username':self.username, 'password':self.password})   
            cookie_parameters = {'Cookie': session_parameters_1}
            self.request('POST', self.login_page, parameters_copy, cookie_parameters, fail_silently)
            session_parameters_2 = self.get_session_parameters(self.response, fail_silently)
            if session_parameters_2 and (session_parameters_1 != session_parameters_2) :
                self.session_parameters = session_parameters_2
                self.is_authenticated = True
            else :
                self.is_authenticated = False
                exception = NotAuthenticatedException('authentication on login page %s%s failed' % (self.host, url))
                if not fail_silently :
                    raise exception    
                else :
                    self.exceptions[self.request_counter].append(exception)
        else :
            exception = NotLoginPageException("the url %s%s doesn't redirect to the login page" % (self.host, url))
            if not fail_silently :
                raise exception
            else :
                self.exceptions[self.request_counter].append(exception)
                    
    def connect(self, type, url, parameters=Parameters(), headers=Headers(), fail_silently=True):
        """Sends a request to the remote server :
        
        - type: specify the kind of request; i.e. 'GET', 'POST' or 'PUT' values
        - url: the part of the url that exposes the server a resource or a service
        - parameters: parameters to transmit encapsulated in a Parameters object
        - headers: headers parameters to transmit encapsulated in a Headers object
        - fail_silently: specifies if an exception is directly raised or stored in 
                         the 'exceptions' property to be analyzed later
        """
        headers_copy = Headers(headers)
        if not self.is_authenticated :
            self.login(url, parameters, headers_copy, fail_silently)
        if self.session_parameters :
            headers_copy.update({'Cookie':self.session_parameters})
        self.request(type, url, parameters, headers_copy, fail_silently)
        if self.count_exceptions() < 1 :
            self.access_possible = True
        else :
            self.access_possible = False
    
class ForeignAuthority(object):
    """Represent a delegated authentication, i.e. the Django server 
    contact a remote server to determine if the user can connect."""
    
    def __init__(self, type, group, protocol, host, url, login_page=None):
        assert type in ['django', 'basic'], 'type must be in [django,basic]'
        self.type = type
        self.group = group
        self.protocol = protocol
        self.host = host
        self.url = url
        self.login_page = login_page
    
    def authentify(self, username, password):
        """Launches the authentication."""
        if self.type == 'basic' :
            server = BasicAuthConnection(self.protocol, self.host, username, password)
        elif self.type == 'django' :
            assert self.login_page, "login page must be specified for a remote django server"
            server = DjangoAuthConnection(self.protocol, self.host, username, password, self.login_page)
        server.connect('GET', self.url)
        member = {'django':server.is_authenticated, 'basic':server.access_possible}
        return member[self.type]

def select_authority(authorities, username, password):
    """Determine from which authentication server a user depends."""
    access_possible = False
    selected_authority = None
    for authority in authorities :
        authority_obj = ForeignAuthority(*authorities[authority])
        if authority_obj.authentify(username, password) :
            access_possible = True
            selected_authority = authority_obj
            break
    return selected_authority, access_possible
                

