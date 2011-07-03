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
        This class is an interface to the Facebook Graph API
    """
            
    GRAPH_URL = "https://graph.facebook.com/"
    BASE_AUTH_URL = "%soauth/authorize?" % GRAPH_URL
    
    #A factory to make objects from a json
    factory = Json2ObjectsFactory()
    
    def __init__(self, app_id, access_token=None):
        
        self.app_id = app_id
        self.access_token = access_token
        
    def authenticate(self):
        """
            Open your prefered web browser to make the authentication request
        """
        webbrowser.open(self.get_auth_url())
        
    def get_auth_url(self, redirect_uri='http://www.facebook.com/connect/login_success.html'):            
        """
            Returns the authentication url
        """
        url_path = urllib.urlencode({
            "client_id": self.app_id,
            "display": "popup",
            "type": "user_agent",
            "scope": "publish_stream,read_stream,status_update,offline_access,user_photos,friends_photos,friends_status",
            "redirect_uri": redirect_uri,
        })
        url = "%s%s" % (self.BASE_AUTH_URL, url_path)
        return url
        
    def set_access_token(self, token):
        """
            Sets the access token. Necessary to make the requests that requires autenthication.
        """
        self.access_token = token
    
    def _make_auth_request(self, path):
        """
            Makes a request to the facebook Graph API.
            This method requires authentication!
            Don't forgot to get the access token before use it.
        """
        if self.access_token is None:
            raise PyfbException("Must Be authenticated. Do you forgot to get the access token?")
            
        token_url = "?access_token=%s" % self.access_token
        url = "%s%s%s" % (self.GRAPH_URL, path, token_url)
        data = urllib.urlopen(url).read()
        return data
        
    def _make_object(self, name, data):
        """
            Uses the factory to make an object from a json
        """
        return self.factory.make_object(name, data)
        
    def _get_one(self, path, object_name):
        """
            Gets one object
        """        
        data = self._make_auth_request(path)        
        return self._make_object(object_name, data)
    
    def _get_list(self, id, path, object_name=None):
        """
            Gets A list of objects
        """
        if id is None:
            id = "me"
        if object_name is None:
            object_name = path
        path = "%s/%s" % (id, path.lower())
        return self._get_one(path, object_name).__dict__[object_name]
        
    def get_myself(self):
        """
            Gets myself data
        """
        return self._get_one("me", "FBUser")
        
    def get_user_by_id(self, id=None):
        """
            Gets an user by the id
        """
        if id is None:
            id = "me"
        return self._get_one(id, "FBUser")
        
    def get_friends(self, id=None):
        """
            Gets a list with your friends
        """        
        return self._get_list(id, "Friends")
        
    def get_statuses(self, id=None): 
        """
            Gets a list of status objects
        """
        return self._get_list(id, "Statuses")
        
    def get_photos(self, id=None): 
        """
            Gets a list of photos objects
        """
        return self._get_list(id, "Photos")
        
        
class PyfbException(Exception):
    """
        A PyFB Exception class
    """
    
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)

