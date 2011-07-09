"""
    $Id: pyfb.py

    This is an Easy to Use Python Interface to the Facebook Graph API

    It gives you methods to access your data on facebook and
    provides objects instead of json dictionaries!
"""

import urllib
import webbrowser

from utils import Json2ObjectsFactory


class Pyfb(object):
    """
        This class is Facade for FacebookClient
    """    
    
    def __init__(self, app_id, access_token=None):
            
        self._client = FacebookClient(app_id, access_token)        
    
    def authenticate(self):
        """
            Open your prefered web browser to make the authentication request
        """
        self._show_in_browser(self.get_auth_url())        
        
    def get_auth_url(self, redirect_uri='http://www.facebook.com/connect/login_success.html'):
        """
            Returns the authentication url
        """
        return self._client.get_auth_url(redirect_uri)
        
    def show_dialog(self, redirect_uri='http://www.example.com/response/'):
        """
            Open your prefered web browser to make the authentication request
        """
        self._show_in_browser(self.get_dialog_url(redirect_uri=redirect_uri))
        
    def get_dialog_url(self, redirect_uri=''):
        """
            Returns a url inside facebook that shows a dialog allowing 
            users to publish contents.
        """
        return self._client.get_dialog_url(redirect_uri)        
        
    def _show_in_browser(self, url):
        """
            Opens your prefered web browser to make the authentication request
        """
        webbrowser.open(url)
    
    def set_access_token(self, token):
        """
            Sets the access token. Necessary to make the requests that requires autenthication.
        """
        self._client.access_token = token
    
    def get_myself(self):
        """
            Gets myself data
        """
        return self._client.get_one("me", "FBUser")

    def get_user_by_id(self, id=None):
        """
            Gets an user by the id
        """
        if id is None:
            id = "me"
        return self._client.get_one(id, "FBUser")

    def get_friends(self, id=None):
        """
            Gets a list with your friends
        """
        return self._client.get_list(id, "Friends")

    def get_statuses(self, id=None):
        """
            Gets a list of status objects
        """
        return self._client.get_list(id, "Statuses")

    def get_photos(self, id=None):
        """
            Gets a list of photos objects
        """
        return self._client.get_list(id, "Photos")
        
    def get_comments(self, id=None):
        """
            Gets a list of photos objects
        """
        return self._client.get_list(id, "Comments")

    def publish(self, message, id=None):
        """
            Publishes a message on the wall
        """
        self._client.push(id, "feed", message=message)
        
    def comment(self, message, id=None):
        """
            Publishes a message on the wall
        """
        self._client.push(id, "comments", message=message)
        
    def get_likes(self, id=None):
        """
            Get a list of liked objects
        """
        return self._client.get_list(id, "likes")
        
    def like(self, id):
        """
            LIKE: It Doesn't work. Seems to be a bug on the Graph API 
            http://bugs.developers.facebook.net/show_bug.cgi?id=10714
        """
        print self.like.__doc__
        return self._client.push(id, "likes")
        
    def delete(self, id):
        """ 
            Deletes a object
        """
        self._client.delete(id)
        
    def fql_query(self, query):
        """
            Executes a FBQL query
        """
        return self._client.execute_fql_query(query)


class FacebookClient(object):
    """
        This class implements the interface to the Facebook Graph API
    """
    
    FACEBOOK_URL = "https://www.facebook.com/"
    GRAPH_URL = "https://graph.facebook.com/"
    API_URL = "https://api.facebook.com/"
    
    BASE_AUTH_URL = "%soauth/authorize?" % GRAPH_URL
    DIALOG_BASE_URL = "%sdialog/feed?" % FACEBOOK_URL
    FBQL_BASE_URL = "%smethod/fql.query?" % API_URL

    #A factory to make objects from a json
    factory = Json2ObjectsFactory()

    def __init__(self, app_id, access_token=None):

        self.app_id = app_id
        self.access_token = access_token    
        
    def _make_request(self, url, **data):
        """
            Makes a simple request. If not data is a GET else is a POST.
        """
        if not data:
            data = None
        return urllib.urlopen(url, data).read()
    
    def _make_auth_request(self, path, **data):
        """
            Makes a request to the facebook Graph API.
            This method requires authentication!
            Don't forgot to get the access token before use it.
        """
        if self.access_token is None:
            raise PyfbException("Must Be authenticated. Do you forgot to get the access token?")

        token_url = "?access_token=%s" % self.access_token
        url = "%s%s%s" % (self.GRAPH_URL, path, token_url)
        if data:
            post_data = urllib.urlencode(data)
        else:
            post_data = None
        return urllib.urlopen(url, post_data).read()

    def _make_object(self, name, data):
        """
            Uses the factory to make an object from a json
        """
        return self.factory.make_object(name, data)
    
    def _get_url_path(self, dic):
    
        return urllib.urlencode(dic)
    
    def get_auth_url(self, redirect_uri):
        """
            Returns the authentication url
        """
        url_path = self._get_url_path({
            "client_id": self.app_id,
            "display": "popup",
            "type": "user_agent",
            "scope": "publish_stream,read_stream,status_update,offline_access,user_photos,friends_photos,friends_status",
            "redirect_uri": redirect_uri,
        })
        url = "%s%s" % (self.BASE_AUTH_URL, url_path)
        return url
        
    def get_dialog_url(self, redirect_uri):
        url_path = self._get_url_path({
            "app_id" : self.app_id,
            "redirect_uri": redirect_uri,
        })
        url = "%s%s" % (self.DIALOG_BASE_URL, url_path)
        return url

    def get_one(self, path, object_name):
        """
            Gets one object
        """
        data = self._make_auth_request(path)
        return self._make_object(object_name, data)

    def get_list(self, id, path, object_name=None):
        """
            Gets A list of objects
        """
        if id is None:
            id = "me"
        if object_name is None:
            object_name = path
        path = "%s/%s" % (id, path.lower())
        return self.get_one(path, object_name).__dict__[object_name]
        
    def push(self, id, path, **data):
        """
            Pushes data to facebook
        """
        if id is None:
            id = "me"
        path = "%s/%s" % (id, path)
        self._make_auth_request(path, **data)
        
    def delete(self, id):
        """
            Deletes a object by id
        """
        data = {"method": "delete"}
        self._make_auth_request(id, **data)
        
    def _get_table_name(self, query):
        """
            Try to get the table name from a fql query
        """
        KEY = "FROM"
        try:
            index = query.index(KEY) + len(KEY) + 1
            table = query[index:].strip().split(" ")[0]
            return table
        except Exception, e:
            raise PyfbException("Invalid FQL Sintax")
    
    def execute_fql_query(self, query):
        """
            Executes a FBQL query and return a list of objects
        """
        table = self._get_table_name(query)
        url_path = self._get_url_path({'query' : query, 'format' : 'json'})
        url = "%s%s" % (self.FBQL_BASE_URL, url_path)
        data = self._make_request(url)
        return self.factory.make_objects_list(table, data)
    

class PyfbException(Exception):
    """
        A PyFB Exception class
    """

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

