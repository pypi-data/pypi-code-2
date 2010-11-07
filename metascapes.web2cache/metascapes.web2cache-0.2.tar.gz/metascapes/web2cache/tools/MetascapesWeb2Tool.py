# -*- coding: utf-8 -*-
#
# File: MetascapesWeb2Tool.py
#
# Copyright (c) 2010 by Bernhard Snizek <unknown>
# Generator: ArchGenXML Version 2.5
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Bernhard Snizek <bs@metascapes.org>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import UniqueObject
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from ZPublisher import BeforeTraverse
from ZPublisher.HTTPRequest import HTTPRequest
from datetime import datetime
from metascapes.web2cache.config import *
from metascapes.web2cache.interfaces.utility import IWeb2Flickr, \
    IWeb2Delicious, IWeb2Wordpress, IWeb2Twitter, IWeb2Facebook, IWeb2Slideshare, \
    IWeb2Vimeo, IWeb2
from plone.memoize import forever, ram
from zope.interface import classProvides, implements
from zope.schema.fieldproperty import FieldProperty
import feedparser
import flickrapi
                                                    


# FLICKR_API_KEY = "f03b940f009d5e3813c92619d9e46a25"

ID = "portal_web2cache"

RSS_VALUE_LENGTH = 200

MONTHS = {u'Jan':1,
          u'Feb':2,
          u'Mar':3,
          u'Apr':4,
          u'May':5,
          u'Jun':6,
          u'Jul':7,
          u'Aug':8,
          u'Sep':9,
          u'Oct':10,
          u'Nov':11,
          u'Dec':12}

class MetascapesWeb2Tool(UniqueObject, SimpleItem):
    """
    """
    security = ClassSecurityInfo()

    implements(IWeb2)
    classProvides(
        IWeb2Flickr,
        IWeb2Delicious,
        IWeb2Wordpress,
        IWeb2Twitter,
        IWeb2Facebook,
        IWeb2Slideshare,
        IWeb2Vimeo
        )
    
    id  = ID
    title = 'Web 2.0 Cache Tool'
    meta_type = 'Web 2.0 Cache Tool'
    
    manage_options=(
        ({ 'label'  : 'Web2.0CacheConfig',
           'action' : 'manage_configForm',
           },
         ) + SimpleItem.manage_options
        )
    
    manage_configForm = PageTemplateFile('www/web20cache_tool_config', globals())

    last_facebook_item = None
    last_wordpress_post = None
    last_tweet = None
    flickr_items = None
    latest_vimeo_item = None
    last_slideshare_item = None
    delicious_items = None
    
    flickr_api_key = FieldProperty(IWeb2Flickr['flickr_api_key'])
    flickr_user_id = FieldProperty(IWeb2Flickr['flickr_user_id'])
    
    delicious_rss_url = FieldProperty(IWeb2Delicious['delicious_rss_url'])
    
    wordpress_rss_url = FieldProperty(IWeb2Wordpress['wordpress_rss_url'])
    
    twitter_rss_url = FieldProperty(IWeb2Twitter['twitter_rss_url'])
    
    facebook_rss_url = FieldProperty(IWeb2Facebook['facebook_rss_url'])
    
    slideshare_rss_url = FieldProperty(IWeb2Slideshare['slideshare_rss_url']) 

    vimeo_rss_url = FieldProperty(IWeb2Vimeo['vimeo_rss_url'])     
    
    # GETTERS
    
    security.declareProtected(ManagePortal, 'getFlickrApiKey')
    def getFlickrApiKey(self):
        """Returns the alpanumerical key for FLICKR 
        """
        return self.flickr_api_key

    security.declareProtected(ManagePortal, 'getFlickrUserID')
    def getFlickrUserID(self):
        """Returns the user ID for the FLICKR account
        """
        return self.flickr_api_key
    
    security.declareProtected(ManagePortal, 'getDeliciousRssUrl')
    def getDeliciousRssUrl(self):
        """Returns the delicious url
        """
        return self.delicious_rss_url

    security.declareProtected(ManagePortal, 'getWordpressRssUrl')
    def getWordpressRssUrl(self):
        """Returns the delicious url
        """
        return self.wordpress_rss_url

    security.declareProtected(ManagePortal, 'getTwitterRssUrl')
    def getTwitterRssUrl(self):
        """Returns the delicious url
        """
        return self.twitter_rss_url

    security.declareProtected(ManagePortal, 'getFacebookRssUrl')
    def getFacebookRssUrl(self):
        """Returns the delicious url
        """
        return self.facebook_rss_url
    
    security.declareProtected(ManagePortal, 'getSlideshareRssUrl')
    def getSlideshareRssUrl(self):
        """Returns the Slideshare url
        """
        return self.slideshare_rss_url


    security.declareProtected(ManagePortal, 'getVimeoRssUrl')
    def getVimeoRssUrl(self):
        """Returns the Vimeo url
        """
        return self.vimeo_rss_url
    
    security.declareProtected(ManagePortal, 'manage_setWeb2CacheSettings')
    def manage_setWeb2CacheSettings(self, 
                                      bla,
                                      REQUEST=None):
        """Stores the tool settings."""
        
        self.bla = bla
        
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
            
    def manage_beforeDelete(self, item, container):
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            BeforeTraverse.unregisterBeforeTraverse(container, handle)

    def manage_afterAdd(self, item, container):
        if item is self:
            handle = self.meta_type + '/' + self.getId()
            container = container.this()
            nc = BeforeTraverse.NameCaller(self.getId())
            BeforeTraverse.registerBeforeTraverse(container, nc, handle)
            
            
    ##/code-section class-header
    


    # tool-constructors have no id argument, the id is fixed
    def __init__(self, id=None):
        SimpleItem.__init__(self, ID)
#        self.setTitle('')
        self.id = ID
        
        ##code-section constructor-footer #fill in your manual code here
#        self.last_wordpress_post = None 
#        self.last_tweet = None  
#        self.last_facebook_item = None
#        self.flickr_items = None
#        self.latest_vimeo_item = None
#        self.last_slideshare_item = None
        
    def pullWordpress(self):
        """Gets the latest wordpress blogpost
        """ 
        python_wiki_rss_url = self.getWordpressRssUrl()  #"http://kattomenium.wordpress.com/feed/"
        feed = feedparser.parse( python_wiki_rss_url )
        
        items = feed.get("items",[])
        
        
        if len(items) >0:
            last_one = items[0]
            
            self.last_post_value = last_one.get("content")[0].get("value","")
            
#            import pdb;pdb.set_trace()
            
            # building a datettime object from the date
            
            datetime_list = last_one.updated.split(" ")

            try:
                day = int(datetime_list[1])
                month = MONTHS.get(datetime_list[2])
                year = int(datetime_list[3])
                _updated = datetime(year, month, day)
                
            except ValueError:
                _updated = None
                
            
            self.last_wordpress_post = {'title' : last_one.get("title"),
                                        'link' :  last_one.get("link"),
                                        'updated' : _updated
                                        }
            print "wordpress imported"
         
  
    def pullTwitter(self):
        """
        """
        # TWITTER    
          
        twitter_rss_url = self.getTwitterRssUrl()  # "http://twitter.com/statuses/user_timeline/143745357.rss"
        twitter_feed = feedparser.parse( twitter_rss_url )
        
        twitter_items = twitter_feed.get("items",[])
        
        if len(twitter_items) >0:
            self.last_tweet = twitter_items[0]
            
        print "TWITTER imported"
    
    
    def pullFacebook(self):           
        # Facebook 
        
        facebook_product_page_rss_url = self.getFacebookRssUrl() # "http://www.facebook.com/feeds/page.php?format=atom10&id=51495582725"
        facebook_feed = feedparser.parse( facebook_product_page_rss_url )
        
        facebook_items = facebook_feed.get("items",[])
        
        if len(facebook_items) >0:
            self.last_facebook_item = facebook_items[0]
            
    def pullFLICKR(self):          
        # FLICKR
        
        flickr = flickrapi.FlickrAPI(self.getFlickrApiKey())
        
        self.flickr_items = []
        
        for photo in flickr.walk(user_id = self.getFlickrUserID(), # "57701671@N00",
                                 per_page = "8"):
            
            photo_url = "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (photo.get("farm"),
                                                                    photo.get("server"),
                                                                    photo.get("id"),
                                                                    photo.get("secret"),
                                                                    )
            photo_title = photo.get("title")
            
            self.flickr_items.append({'url':photo_url,
                                      'title':photo_title})

    def pullDelicious(self):        
        # delicious
        
        delicious_rss_url = self.getDeliciousRssUrl() #"http://feeds.delicious.com/v2/rss/bsnizek?count=3"
        delicious_feed = feedparser.parse( delicious_rss_url )
        
        self.delicious_items = delicious_feed.get("items",[])


    def pullSlideshare(self):
        # SLIDESHARE
        
        slideshare_rss_url = self.getSlideshareRssUrl() # "http://www.slideshare.net/rss/user/bsnizek"
        slideshare_feed = feedparser.parse( slideshare_rss_url )
        slidershare_items = slideshare_feed.get("items",[])
        
        if len(slidershare_items) >0:
            self.last_slideshare_item = slidershare_items[0]
            

    def pullVimeo(self):
        # VIMEO
        
        vimeo_rss_url = self.getVimeoRssUrl() #"http://vimeo.com/user2009687/videos/rss"
        vimeo_feed = feedparser.parse(vimeo_rss_url)
        vimeo_items = vimeo_feed.get("items", [])
        
        if len(vimeo_items) > 0:
            self.latest_vimeo_item = vimeo_items[0]
        ##/code-section constructor-footer


    # tool should not appear in portal_catalog
    def at_post_edit_script(self):
        self.unindexObject()
        
        ##code-section post-edit-method-footer #fill in your manual code here
        ##/code-section post-edit-method-footer


    # Methods

    security.declarePublic('getLastFacebookStatus')
#    @forever.memoize
    def getLastFacebookStatus(self):
        """
        """
        if self.last_facebook_item == None:
            self.pullFacebook()
            
#        import pdb;pdb.set_trace()
            
        return self.last_facebook_item

    security.declarePublic('getLastRssPost')
    @forever.memoize
    def getLastRssPost(self):
        """
        """
        if self.last_wordpress_post == None:
            self.pullWordpress()
        return self.last_wordpress_post

    security.declarePublic('getLastTweet')
    @forever.memoize
    def getLastTweet(self):
        """
        """
        if self.last_tweet == None:
            self.pullTwitter()
        return self.last_tweet

    security.declarePublic('getLatestSlideShareItem')
    @forever.memoize
    def getLatestSlideShareItem(self):
        """
        """
        if self.last_slideshare_item == None:
            self.pullSlideshare()
        return self.last_slideshare_item

    security.declarePublic('getLatestVimeoItem')
    @forever.memoize
    def getLatestVimeoItem(self):
        """
        """
        if self.latest_vimeo_item == None:
            self.pullVimeo()
        return self.latest_vimeo_item

    security.declarePublic('getLatestFLICKRItems')
    @forever.memoize
    def getLatestFLICKRItems(self,n=3):
        """
        """
        if self.flickr_items == None:
            self.pullFLICKR()
        return self.flickr_items[0:n]

    @forever.memoize
    def getLatestDeliciousItems(self,n=3):        
        """Returns the latest <n> items of del delicious stream as a list of dicts ... 
        """
        
        if self.delicious_items == None:
            self.pullDelicious()
        return self.delicious_items[0:n]

    @forever.memoize
    def getLastRssPostValue(self, n=200):
        
        if self.last_wordpress_post == None:
            self.pullWordpress()
        
        if len(self.last_post_value) > n:
            return self.last_post_value[0:n] + "..."
        else:
            return self.last_post_value

    security.declarePublic('__call__')
    def __call__(self,container,req):
        """
        """
        print "WebTool.__call__()"

InitializeClass(MetascapesWeb2Tool)

