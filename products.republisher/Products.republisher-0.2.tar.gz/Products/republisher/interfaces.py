from z3c.form import interfaces
from zope.interface import Interface
from zope import schema

class IRepublisherSettings(Interface):    
    """ The view for Republisher prefs form. """

    api_key = schema.TextLine(title=u"API key from Flickr",
                                  description=u"The app key given to you when you create your FLICKR app",
                                  required=False,
                                  default=u'88c9ed38ced3a04fa8c683f3eac9cd6f',)
    
    api_secret = schema.TextLine(title=u"Flickr app secret",
                                  description=u"The secret that matches your api key",
                                  required=False,
                                  default=u'39615d0571871bdf',)

    republisher_toggle = schema.Bool(title=u'Republisher on',
                                  description=u'Turn republisher on?',
                                  required=True,
                                  default=True,)
    
    
class IRepublisherTokenKeeper(Interface):
    """A Record to keep the Authentication Tokens from the OAuth systems from the social networks"""
    
    flickr_token = schema.TextLine(title=u"Flickr Auth Token", default=u'None',)
    flickr_frob = schema.TextLine(title=u"Flickr Auth Frob", default=u'None',)