from os import path
from urlparse import urlsplit
from urlreduce import utils
from urlreduce.models import Link
from django.utils.encoding import smart_unicode


def replace_insensitive(string, target, replacement):
    """
    Similar to string.replace() but is case insensitive
    Code borrowed from: http://forums.devshed.com/python-programming-11/case-insensitive-string-replace-490921.html
    """
    no_case = string.lower()
    index = no_case.rfind(target.lower())
    if index >= 0:
        return string[:index] + replacement + string[index + len(target):]
    else: # no results so return the original string
        return string

class UrlShortnerMiddleware:
    """
    The URL shortner middleware handles creating, and injecting short urls into
    your webpages. This is done by generating the url, creating the Link response
    header for your HTML document and inject the html meta option into your HTML
    page.
    """

    # -- Holds the Link Object
    link        = None
    shortlink   = None

    def process_request( self, request ):
        
        # -- Ignore Everything in Media
        if request.get_full_path().split( "/" )[1] != "media":
            
            # -- Define host, make sure there is no www to make it shorter
            host = request.get_host().replace( "www.", "" )
            
            # -- Get Link Record from the Database
            try:
                self.link = Link.objects.get( url = request.build_absolute_uri().rstrip('/') )
            except Link.DoesNotExist:
                Link( url = request.build_absolute_uri().rstrip('/') ).save()
                self.link = Link.objects.get( url = request.build_absolute_uri().rstrip('/') )
            
            # -- Construct Shortlink
            if request.is_secure():
                self.shortlink = "https://%s/x/%s" % ( host, self.link.short_url )
            else:
                self.shortlink = "http://%s/x/%s" % ( host, self.link.short_url )
            
            # -- Attach to Request
            request.META['shortlink'] = self.shortlink
            
    def process_response( self, request, response ):
        """
        Injection Pattern Based on django-debug-toolbar:
        https://github.com/robhudson/django-debug-toolbar
        """
        
        FIND        = "</head>"
        REPLACE     = '\t<link rel="shortlink" href="%s" />\n</head>'
        HTML_TYPES  = ('text/html', 'application/xhtml+xml')
        
        # -- Check if 200 and HTML Request Type
        if response.status_code == 200:
            if response['Content-Type'].split(';')[0] in HTML_TYPES:
                
                # -- Add Link to Request Headers
                response['Link'] = '<%s>; rel="shortlink"' % self.shortlink
             
                # -- Inject into HTML Head
                response.content = replace_insensitive( smart_unicode(response.content), FIND, REPLACE % self.shortlink )
                
                # -- Refresh Content Length
                if response.get('Content-Length', None):
                    response['Content-Length'] = len( response.content )

        return response