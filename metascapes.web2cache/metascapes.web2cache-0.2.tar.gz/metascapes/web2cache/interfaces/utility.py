from zope.interface import Interface
from zope import schema
from zope.i18nmessageid import MessageFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

_ = MessageFactory('metascapes.web2cache')

class IWeb2Flickr(Interface):
    """This interface defines the layout properties.
    """
    
    flickr_enabled = schema.Bool(
                          title=_(u"Enabled"),
                          description=_(u"switch this thing on"),
                          required=False)

    flickr_api_key = schema.TextLine(
                                     title=_(u"FLICKR API KEY"),
                                     description=_(u"Enter the API key bla bla bla "),
                                     required=False) 

    flickr_user_id = schema.TextLine(
                                     title=_(u"FLICKR User ID"),
                                     description=_(u"Enter the FLICKR User ID "),
                                     required=False) 
    
class IWeb2Delicious(Interface):
    """
    This interface defines the layout properties.
    """

    delicious_enabled = schema.Bool(
                          title=_(u"Enabled"),
                          description=_(u"switch this thing on"),
                          required=False)

    delicious_rss_url = schema.TextLine(
                                     title=_(u"Delicious URL"),
                                     description=_(u"Enter the Delicious Url"),
                                     required=False)
    
class IWeb2Wordpress(Interface):
    """
    This interface defines the layout properties.
    """

    wordpress_enabled = schema.Bool(
                          title=_(u"Enabled"),
                          description=_(u"switch this thing on"),
                          required=False)

    wordpress_rss_url = schema.TextLine(
                                     title=_(u"Wordpress URL"),
                                     description=_(u"Enter the URL for Wordpress"),
                                     required=False) 
    
class IWeb2Twitter(Interface):
    """
    This interface defines the layout properties.
    """

    twitter_enabled = schema.Bool(
                          title=_(u"Enabled"),
                          description=_(u"switch this thing on"),
                          required=False)

    twitter_rss_url = schema.TextLine(
                                     title=_(u"Twitter URL"),
                                     description=_(u"Enter the URL for Twitter"),
                                     required=False) 
    
class IWeb2Facebook(Interface):
    """
    This interface defines the layout properties.
    """

    facebook_enabled = schema.Bool(
                          title=_(u"Enabled"),
                          description=_(u"switch this thing on"),
                          required=False)

    facebook_rss_url = schema.TextLine(
                                     title=_(u"Facebook URL"),
                                     description=_(u"Enter the URL for Facebook"),
                                     required=False) 
    
class IWeb2Slideshare(Interface):
    """
    This interface defines the layout properties.
    """

    slideshare_enabled = schema.Bool(
                          title=_(u"Enabled"),
                          description=_(u"switch this thing on"),
                          required=False)

    slideshare_rss_url = schema.TextLine(
                                     title=_(u"Slideshare URL"),
                                     description=_(u"Enter the URL for Slideshare"),
                                     required=False) 
    
class IWeb2Vimeo(Interface):
    """
    This interface defines the layout properties.
    """

    vimeo_enabled = schema.Bool(
                          title=_(u"Enabled"),
                          description=_(u"switch this thing on"),
                          required=False)

    vimeo_rss_url = schema.TextLine(
                                     title=_(u"Vimeo URL"),
                                     description=_(u"Enter the URL for Vimeo"),
                                     required=False) 
    
class IWeb2(
            IWeb2Flickr,
            IWeb2Delicious,
            IWeb2Wordpress,
            IWeb2Twitter,
            IWeb2Facebook,
            IWeb2Slideshare,
            IWeb2Vimeo
            ):
    """This interface defines the Utility."""

    pass
