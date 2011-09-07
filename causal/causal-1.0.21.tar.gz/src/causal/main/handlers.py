"""Base service handler classes
"""
from causal.main.utils.services import get_config
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.shortcuts import redirect
import httplib2
import oauth2 as oauth

class BaseServiceHandler(object):
    display_name = 'BASE SERVICE HANDLER'
    custom_form = False
    oauth_form = False
    # Don't require enable() to be called by default, this is normally only
    # needed by services that have auth steps, such as enabled OAuth services
    requires_enabling = False

    def __init__(self, model_instance):
        self.service = model_instance

    def get_auth_url_alias(self):
        """Returns the alias to lookup the reversable auth URL, not used by
        most services.
        """
        raise NotImplementedError()

    def get_auth_url(self):
        """Returns the URL to auth the service, not used by most services.
        """
        raise NotImplementedError()

    def get_auth_url_alias(self):
        """Returns the alias to lookup the reversable auth URL.
        """
        return "%s-auth" % (self.service.app.module_name.replace('.', '-'),)

    def get_auth_url(self):
        """Returns the URL to auth the service.
        """
        return reverse(self.get_auth_url_alias())

    def enable(self):
        """Action to enable this service, not needed by most services.
        """
        raise NotImplementedError()

    def get_items(self, since):
        raise NotImplementedError("ServiceHandler classes need a custom get_items method")

class OAuthServiceHandler(BaseServiceHandler):
    oauth_form = True
    requires_enabling = True
    
    def __init__(self, model_instance, oauth_version=2, disable_ssl=False):
        super(OAuthServiceHandler, self).__init__(model_instance)
        #self.service - model_instance
        self.oauth_version = oauth_version
        self.disable_ssl = disable_ssl

    def enable(self):
        """Setup and authorise the service.
        """
        return redirect(self.get_auth_url_alias())
    

    def get_data(self, url):
        """Fetch oauth protected urls, use oauth v2 by default."""
    
        try:
            # if the user doesn't have an access token something bad has happened
            access_token = self.service.auth.access_token
        except:
            return
        
        if self.oauth_version == 1:
            json = self._get_oauth_v1(url)
        else:
            # yay we can use the lovely oauth2 spec
            json = self._get_oauth_v2(url)
        
        return json
        
    def _get_oauth_v1(self, url, method='GET'):
        """Fetch url data using v1 of oauth spec.
        This involves using the OAuth libs."""
    
        auth_settings = get_config(self.service.app.module_name, 'auth')
        if self.service.auth.access_token:
            consumer = oauth.Consumer(
                self.service.app.auth_settings['consumer_key'],
                self.service.app.auth_settings['consumer_secret']
            )
            token = oauth.Token(self.service.auth.access_token.oauth_token, self.service.auth.access_token.oauth_token_secret)
    
            client = oauth.Client(consumer, token)
            resp, content = client.request(url, method)

            if resp['status'] == '200':
                return simplejson.loads(content)    

        return False
        

    def _get_oauth_v2(self, url):
        """Lets got and use the nice oauth2 process of just fetching urls."""
        
        if self.disable_ssl:
            try:
                h = httplib2.Http(disable_ssl_certificate_validation=True)
            except:
                h = httplib2.Http()
        else:
            h = httplib2.Http()
            
        if not url.endswith('?'):
            url += "?"
            
        if self.display_name == 'Foursquare':
            url += 'oauth_token=%s'
        else:
            url += 'access_token=%s'
        resp, content = h.request(url % (self.service.auth.access_token.oauth_token), "GET")
        
        # we at least know the request was successful
        # the data might be an error but we did our bit
        if resp['status'] == '200':
            return simplejson.loads(content)

