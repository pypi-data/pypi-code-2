#! /usr/bin/env python
# coding:utf-8

'''
A module that provide a Python interface to the Twitter API
'''

# to use OAuth
import oauth2 as oauth

# import urllib for using urllib.urlencode when using 'POST' method 
import urllib

# to parse xml
from xml.dom import minidom

# to use datetime.datetime, datetime.timedelta class
import datetime

# next modules are used in GetOauth class
import webbrowser
import urlparse



# Tiwtter Api URL
_UPDATE_URL = 'http://api.twitter.com/1/statuses/update.xml'
_FRIENDS_TIMELINE_URL = 'http://api.twitter.com/1/statuses/friends_timeline.xml'
_USER_TIMELINE_URL = 'http://api.twitter.com/1/statuses/user_timeline.xml'
_REPLIES_URL = 'http://api.twitter.com/1/statuses/replies.xml'
_DESTROY_URL = 'http://api.twitter.com/1/statuses/destroy/%s.xml'


# these constants are used in the GetOuath class.
_REQUEST_TOKEN_URL = 'http://twitter.com/oauth/request_token'
_ACCESS_TOKEN_URL = 'http://twitter.com/oauth/access_token'
_AUTHORIZE_URL = 'http://twitter.com/oauth/authorize'

#post URL
#post_url = 'http://twitter.com/statuses/update.xml'



class GetOauth:
    '''
    A class for getting consumer_key and consumer_secret.
    '''

    def __init__(self, consumer_key, consumer_secret):
        '''
        GetOauth initializer.
        '''
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

    # for python2.5
    def _parse_qsl(self, url):
        '''
        Parse_qsl method.

        for python 2.5
        '''
        param = {}
        for i in url.split('&'):
            p = i.split('=')
            param.update({p[0]:p[1]})
        return param
    
    def get_oauth(self):
        '''
        Get consumer_key and consumer_secret.

        How to use:
        
        >>> import twitter_oauth
        >>> consumer_key = '***'
        >>> consumer_secret = '***'
        >>> get_oauth_obj = twitter_oauth.GetOauht(consumer_key, consumer_secret)
        >>> get_oauth_obj.get_oauth()
        '''

        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        client = oauth.Client(consumer)
        
        #Step1: Get a request token.
        resp, content = client.request(_REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception('Invalid response %s' % resp['status'])
    
        request_token = dict(self._parse_qsl(content))
        
        print "Request Token:"
        print "  - oauth_token        = %s" % request_token['oauth_token']
        print "  - oauth_token_secret = %s" % request_token['oauth_token_secret']
    
    
        #step2 Redirect to the provider
    
        print "Go to the following link in your browser"
        print '%s?oauth_token=%s' % (_AUTHORIZE_URL, request_token['oauth_token'])
        print 
    
        webbrowser.open('%s?oauth_token=%s' % (_AUTHORIZE_URL, request_token['oauth_token']))
    
        # accepted = 'n'
        # while accepted != 'y':
        #     accepted = raw_input('Have you authorized me? (y/n) ')
    
        oauth_verifier = raw_input('What is the PIN? ')
    
        #step3
        token = oauth.Token(request_token['oauth_token'], 
                            request_token['oauth_token_secret'])
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)
    
        resp, content = client.request(_ACCESS_TOKEN_URL, "POST")
        access_token = dict(self._parse_qsl(content))

        oauth_token = access_token['oauth_token']
        oauth_token_secret = access_token['oauth_token_secret']
        
        print "Access Token:"
        print "  - oauth_token        = %s" % oauth_token
        print "  - oauth_token_secret = %s" % oauth_token_secret
        print
        print "You may now access protected resources using the access token above"
        print
     
        return {'consumer_key':self.consumer_key, 
                'consumer_secret':self.consumer_secret, 
                'oauth_token':oauth_token, 
                'oauth_token_secret':oauth_token_secret}




class XMLParser:
    '''
    A class for parsing XML
    '''

    def __init__(self):
        pass

    def _get_non_null_list(self, item):
        '''
        _parse_status_xml, _parse_user_xmlで使われる関数
        
        for 
        getElementByTagName('tag_name').childNodes == [].

        If a above list is empty list, the next code shold raise error

        getElementByTagName('tag_name').childNodes[0].data
        

        To sovle this problem, use this method.

        _get_non_null_list(getElementByTagName('tag_name')[0].childNodes)

        
        CONSTANTS:
        
        Set a next constant if a value is not defined.

        _not_defined_cont

        '''
        _not_defined_cont = None
    
        if item:
            return item[0].data
        else:
            return _not_defined_cont

    def _get_element(self, xml, tag_name):
        '''
        This method is used in _parse_status_xml, _parse_user_xml.
        '''
        return self._get_non_null_list(xml.getElementsByTagName(tag_name)[0].childNodes)


    
    def _parse_status_xml(self, xml):
        '''
        Status XML parser.

        input : status XML
        return : dictionary
    

        XML example which this method takes.

        xml = """
        <status>
          <created_at>...</created_at>
          ...
        </status>
        """
        
        '''

        return_dict = {}
    
        return_dict['created_at'] = self._get_element(xml, 'created_at')
        return_dict['id'] = self._get_element(xml, 'id')
        return_dict['text'] = self._get_element(xml, 'text')
        return_dict['source'] = self._get_element(xml, 'source')
        return_dict['truncated'] = self._get_element(xml, 'truncated')
        return_dict['truncated'] = self._get_element(xml, 'truncated')
        return_dict['in_reply_to_status_id'] = self._get_element(xml, 'in_reply_to_status_id')
        return_dict['in_reply_to_user_id'] = self._get_element(xml, 'in_reply_to_user_id')
        return_dict['favorited'] = self._get_element(xml, 'favorited')
        return_dict['user'] = xml.getElementsByTagName('user')[0]
        return_dict['geo'] = self._get_element(xml, 'geo')
        return_dict['contributors'] = self._get_element(xml, 'contributors')

    
        return return_dict


    def _parse_user_xml(self, xml):
        '''
        User XML parser.

        input : user XML
        return : dictionary
    

        XML example which this method takes.

        xml = """
        <user>
          <created_at>...</created_at>
          ...
        </user>
        """
        
        '''


        return_dict = {}

        return_dict['id'] = self._get_element(xml, 'id')
        return_dict['name'] = self._get_element(xml, 'name')
        return_dict['screen_name'] = self._get_element(xml, 'screen_name')
        return_dict['created_at'] = self._get_element(xml, 'created_at')
        return_dict['location'] = self._get_element(xml, 'location')
        return_dict['description'] = self._get_element(xml, 'description')
        return_dict['url'] = self._get_element(xml, 'url')
        return_dict['protected'] = self._get_element(xml, 'protected')
        return_dict['followers_count'] = self._get_element(xml, 'followers_count')
        return_dict['friends_count'] = self._get_element(xml, 'friends_count')
        return_dict['favourites_count'] = self._get_element(xml, 'favourites_count')
        return_dict['statuses_count'] = self._get_element(xml, 'statuses_count')
        return_dict['profile_image_url'] = self._get_element(xml, 'profile_image_url')
        return_dict['profile_background_color'] = self._get_element(xml, 'profile_background_color')
        return_dict['profile_text_color'] = self._get_element(xml, 'profile_text_color')
        return_dict['profile_link_color'] = self._get_element(xml, 'profile_link_color')
        return_dict['profile_sidebar_fill_color'] = self._get_element(xml, 'profile_sidebar_fill_color')
        return_dict['profile_sidebar_border_color'] = self._get_element(xml, 'profile_sidebar_border_color')
        return_dict['profile_background_image_url'] = self._get_element(xml, 'profile_background_image_url')
        return_dict['profile_background_tile'] = self._get_element(xml, 'profile_background_tile')
        return_dict['utc_offset'] = self._get_element(xml, 'utc_offset')
        return_dict['time_zone'] = self._get_element(xml, 'time_zone')
        return_dict['lang'] = self._get_element(xml, 'lang')
        return_dict['geo_enabled'] = self._get_element(xml, 'geo_enabled')
        return_dict['verified'] = self._get_element(xml, 'verified')
        return_dict['notifications'] = self._get_element(xml, 'notifications')
        return_dict['following'] = self._get_element(xml, 'following')
        return_dict['contributors_enabled'] = self._get_element(xml, 'contributors_enabled')


        return return_dict
    

    def create_status_object(self,xml):
        '''
        Create a Status object from xml.getElementsByTagName('status')[i]
        '''
        status_dict = self._parse_status_xml(xml)

        status_obj = Status(created_at=status_dict['created_at'], 
                            id=status_dict['id'], 
                            text=status_dict['text'],
                            source=status_dict['source'],
                            truncated=status_dict['truncated'], 
                            in_reply_to_status_id=status_dict['in_reply_to_status_id'],
                            in_reply_to_user_id=status_dict['in_reply_to_user_id'],
                            favorited=status_dict['favorited'], 
                            user=self.create_user_object(status_dict['user']),
                            geo=status_dict['geo'],
                            contributors=status_dict['contributors'])

        return status_obj

    def create_status_object_list(self, xml_list):
        '''
        Create a Status object list from xml.getElementsByTagName['status']
        '''
        return [self.create_status_object(i) for i in xml_list]

    def create_user_object(self, xml):
        '''
        Create a User object from xml.getElementsByTagName('user')[i]
        '''
        user_dict = self._parse_user_xml(xml)
    
        user_obj = User(id=user_dict['id'], name=user_dict['name'],
                        screen_name=user_dict['screen_name'], 
                        created_at=user_dict['created_at'],
                        location=user_dict['location'],
                        description=user_dict['description'],
                        url=user_dict['url'],
                        protected=user_dict['protected'], 
                        followers_count=user_dict['followers_count'],
                        friends_count=user_dict['friends_count'], 
                        favourites_count=user_dict['favourites_count'],
                        statuses_count=user_dict['statuses_count'],
                        profile_image_url=user_dict['profile_image_url'],
                        profile_background_color=user_dict['profile_background_color'],
                        profile_text_color=user_dict['profile_text_color'],
                        profile_link_color=user_dict['profile_link_color'],
                        profile_sidebar_fill_color=user_dict['profile_sidebar_fill_color'],
                        profile_sidebar_border_color=user_dict['profile_sidebar_border_color'],
                        profile_background_image_url=user_dict['profile_background_image_url'],
                        profile_background_tile=user_dict['profile_background_tile'],
                        utc_offset=user_dict['utc_offset'],
                        time_zone=user_dict['time_zone'],
                        lang=user_dict['lang'],
                        geo_enabled=user_dict['geo_enabled'],
                        verified=user_dict['verified'],
                        notifications=user_dict['notifications'],
                        following=user_dict['following'], 
                        contributors_enabled=user_dict['contributors_enabled'])

        return user_obj

    def create_user_object_list(self, xml_list):
        '''
        Create a User object list from xml.getElementsByTagName('user')
        '''
        return [self.create_user_object[i] for i in xml_list]


class Status:
    '''
    A class representing a status.

    The Status class have next attributes:

        stauts.created_at
        stauts.id
        stauts.text
        stauts.source
        stauts.truncated
        stauts.in_reply_to_status_id
        stauts.in_reply_to_user_id
        stauts.favorited
        stauts.user
        stauts.geo
        stauts.contributors

    The Status class have next methods:

        status.get_created_at_from_now()
        status.get_created_at_in_utc()
        status.get_created_at_in_jsp()

    '''

    def __init__(self, 
                 created_at=None, id=None, text=None,
                 source=None, truncated=None, in_reply_to_status_id=None,
                 in_reply_to_user_id=None,
                 favorited=None, user=None,
                 geo=None, contributors=None):
        '''
        Status class initializer.
        '''
        
        self.created_at = created_at
        self.id = id
        self.text = text
        self.source = source
        self.truncated = truncated
        self.in_reply_to_status_id = in_reply_to_status_id
        self.in_reply_to_user_id = in_reply_to_user_id
        self.favorited = favorited
        self.user = user
        self.geo = geo
        self.contributors = contributors

    def _create_datetime_obj(self, utc_datetime):
        '''
        Create datetime object
        
        
        input : utc_datetime = u'Sun Jul 25 14:12:06 +0000 2010'
        return : str(datetime.datetime(2010,07,26,23,12)
        '''
        month_str = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 
                     'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        
        
        utc_datetime_list = utc_datetime.split()
        utc_time = utc_datetime_list[3].split(':')

        utc_now = datetime.datetime(int(utc_datetime_list[5]), 
                                    int(month_str[utc_datetime_list[1]]),
                                    int(utc_datetime_list[2]),
                                    int(utc_time[0]),
                                    int(utc_time[1]))

                                              
        return utc_now


    def get_created_at_from_now(self):
        '''
        When created from now
        '''

        t = datetime.datetime.utcnow() - self._create_datetime_obj(self.created_at)
        #return [t.days, t.seconds]
        #return t
        
        day = t.days
        sec = t.seconds
        min = sec / 60
        hour = min / 60
        
        
        if t.days >= 1:
            return u'%s days ago' % str(day)
        elif hour >= 1:
            return u'%s hours ago' % str(hour)
        elif min >= 1:
            return u'%s minutes ago' % (str(min))
        else:
            return u'%s seconds ago' % (str(sec))
        

        



    def get_created_at_in_utc(self):
        '''
        return datetime.datetime object in UTC
        '''

        return self._create_datetime_obj(self.created_at)
    
    def get_created_at_in_jsp(self):
        '''
        return datetime.datetime object in JSP
        '''

        return self._create_datetime_obj(self.created_at) + datetime.timedelta(hours=9)

class User:
    '''
    A class representing User.

    The User class have next attributes:

        user.id
        user.name
        user.screen_name
        user.created_at
        user.location
        user.description
        user.url
        user.protected
        user.followers_count
        user.friends_count
        user.favourites_count
        user.statuses_count
        user.profile_image_url
        user.profile_background_color
        user.profile_text_color
        user.profile_link_color
        user.profile_sidebar_fill_color
        user.profile_sidebar_border_color
        user.profile_background_image_url
        user.profile_background_tile
        user.utc_offset
        user.time_zone
        user.lang
        user.geo_enabled
        user.verified
        user.notifications
        user.following
        user.contributors_enabled


    The Status class have next methods:

        status.get_created_at_in_utc()
        status.get_created_at_in_jsp()

    '''
    def __init__(self, 
                 id=None, name=None, screen_name=None, 
                 created_at=None, location=None, description=None,
                 url=None, protected=None, followers_count=None, friends_count=None, 
                 favourites_count=None, statuses_count=None, profile_image_url=None,
                 profile_background_color=None, profile_text_color=None,
                 profile_link_color=None, profile_sidebar_fill_color=None,
                 profile_sidebar_border_color=None,
                 profile_background_image_url=None,
                 profile_background_tile=None,
                 utc_offset=None, time_zone=None, lang=None, geo_enabled=None,
                 verified=None, notifications=None, following=None, 
                 contributors_enabled=None):

        self.id = id
        self.name = name
        self.screen_name = screen_name
        self.created_at = created_at
        self.location = location
        self.description = description
        self.url = url
        self.protected = protected
        self.followers_count = followers_count
        self.friends_count = friends_count
        self.favourites_count = favourites_count
        self.statuses_count = statuses_count
        self.profile_image_url = profile_image_url
        self.profile_background_color = profile_background_color
        self.profile_text_color = profile_text_color
        self.profile_link_color = profile_link_color
        self.profile_sidebar_fill_color = profile_sidebar_fill_color
        self.profile_sidebar_border_color = profile_sidebar_border_color
        self.profile_background_image_url = profile_background_image_url
        self.profile_background_tile = profile_background_tile
        self.utc_offset = utc_offset
        self.time_zone = time_zone
        self.lang = lang
        self.geo_enabled = geo_enabled
        self.verified = verified
        self.notifications = notifications
        self.following = following
        self.contributors_enabled = contributors_enabled

    def _create_datetime_obj(self, utc_datetime):
        '''
        Create a datetime object.
        
        
        input : utc_datetime = u'Sun Jul 25 14:12:06 +0000 2010'
        return : str(datetime.datetime(2010,07,26,23,12)
        '''
        month_str = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 
                     'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
        
        
        utc_datetime_list = utc_datetime.split()
        utc_time = utc_datetime_list[3].split(':')

        utc_now = datetime.datetime(int(utc_datetime_list[5]), 
                                    int(month_str[utc_datetime_list[1]]),
                                    int(utc_datetime_list[2]),
                                    int(utc_time[0]),
                                    int(utc_time[1]))

                                              
        return utc_now


    # def get_created_at_from_now(self):
    #     '''
    #     return datetime.timedelta object
        
    #     使用例
    #     t = get_created_at_from_now()
    #     [t.days, t.seconds]
    #     '''
    #     t = datetime.datetime.utcnow() - self._create_datetime_obj(self.created_at)
    #     #return [t.days, t.seconds]
    #     return t
    

    def get_created_at_in_utc(self):
        '''
        return datetime.datetime object in UTC
        '''
        return self._create_datetime_obj(self.created_at)
    
    def get_created_at_in_jsp(self):
        '''
        return datetime.datetime object in JSP
        '''
        return self._create_datetime_obj(self.created_at) + datetime.timedelta(hours=9)

    
class TwitterError(Exception):
    '''
    A class representing twitter error.

    A TwitterError is raised when a status code is not 200 returned from Twitter.
    '''
    
    def __init__(self, status=None, content=None):
        '''
        res : status code
        content : XML
        '''
        Exception.__init__(self)
        
        self.status = status
        self.content = content

    def get_response(self):
        '''
        Return status code
        '''

        return self.status
		
    def get_content(self):
        '''
        Return XML.
        '''

    def __str__(self):
        return 'status_code:%s' % self.status
        



class Api:
    '''
    A Python interface to the Twitter API

    How To Use:

    First, you shold have two keys, 
    'consumer key', 'consumer secret'.

    If you don't have 'consumer key' and 'consumer secret', 
    you cat get these keys to register your application to Twitter.
    You cat register your application at next URL.

    http://twitter.com/apps



    Second, you shold get two keys,
    'oauth_token', and 'oauth_token_secret'

    To get these keys, you use GetOauth class in this module.

    >>> import twitter_oauth

    >>> # write your key and secret
    >>> consumer_key = '***'
    >>> consumer_secret = '***'

    >>> get_oauth_obj = twitter_oauth.GetOauth(consumer_key, consumer_secret)


    Then, you get 'oauth_token' and 'oauth_token_secret' by using get_oauth method.
    This method returns a dictionary that contain 'consumer key', 'consumer secret',
    'oauth_token' and 'oauth_token_secret'


    >>> get_oauth_obj.get_oauth()
      Request Token:
        - oauth_token        = ***
        - oauth_token_secret = ***
      Go to the following link in your browser
      http://twitter.com/oauth/authorize?oauth_token=***
      
      What is the PIN? ***
      Access Token:
        - oauth_token        = ***
        - oauth_token_secret = ***
      
      You may now access protected resources using the access token above
     


    Now, you can use twitter_oauth.Api class.
    To use this class, you can post update, or get friends timeline, etc...
    
    Next example is how to use twitter_oauth.Api class


    >>> # import twitter_oauth module
    >>> import twitter_oauth

    write yoru consumer_key, consumer_secret,
    oauth_token, oauth_token_secret

    >>> consumer_key = '***'
    >>> consumer_secret = '***'
    >>> oauth_token        = '***'
    >>> oauth_token_secret = '***'

    Then, create Api instance

    >>> api = twitter_oauth.Api(consumer_key, consumer_secret,
    >>>                         oauth_token, oauth_token_secret)

    Use get_friends_timeline method.
    You can get friends timeline to use this method.

    >>> friends_timeline = api.get_friends_timeline()
    >>> print [stauts.text for status in friends_timeline]

    Use get_user_timeline method.
    You can get user timeline to use this method.

    >>> user_timeline = api.get_user_timeline()
    >>> print [stauts.text for status in user_timeline]

    Use get_replies method.
    You can get replies to use this method.

    >>> replies = api.get_replies()
    >>> print [stauts.text for status in replies]


    Use post_update method 
    You can post message to Twitter.

    CAUTION : post_update method shold take a unicode.
    Especially, you can post a Japanese text.

    >>> post_update(u'Hello, Twitter')
    >>> post_update(u'こんにちは、Twitter')


    Methods:
        You can use next methods

        post_update()
        get_user_timeline()
        get_friends_timeline()
        get_replies()
        destroy_status()

    '''



    def __init__(self,
                 consumer_key, consumer_secret,
                 oauth_token, oauth_token_secret):
        '''
        The Api class initializer.
        '''

        self.xml_parser = XMLParser()

        self.client = oauth.Client(oauth.Consumer(consumer_key, consumer_secret),
                              oauth.Token(oauth_token, oauth_token_secret))

    def post_update(self, tweet=''):
        '''
        Post your tweet.
        '''

        res, content = self.client.request(_UPDATE_URL, 'POST', 
                                      urllib.urlencode({'status' : tweet.encode('utf-8')}))


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            doc = minidom.parseString(content)
            self.xml_parser.create_status_object(doc.getElementsByTagName('status')[0])
        

    def get_user_timeline(self, id=None, since_id=None, max_id=None,
                             count=None, page=None):
        
        # parse args
        arg_dict = {'id':id , 'since_id':since_id, 'max_id':max_id,
                    'count':count, 'page':page}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        param = '&'.join(url_param_list)
        if param:
            url = _USER_TIMELINE_URL + '?' + param
        else:
            url = _USER_TIMELINE_URL


        # GET request to Twitter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            doc = minidom.parseString(content)
            return self.xml_parser.create_status_object_list(doc.getElementsByTagName('status'))
         
        

    def get_friends_timeline(self, id=None, since_id=None, max_id=None,
                             count=None, page=None):
        
        # parse args
        arg_dict = {'id':id , 'since_id':since_id, 'max_id':max_id,
                    'count':count, 'page':page}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        param = '&'.join(url_param_list)
        if param:
            url = _FRIENDS_TIMELINE_URL + '?' + param
        else:
            url = _FRIENDS_TIMELINE_URL

        print url

        # GET request to Twtter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            doc = minidom.parseString(content)
            return self.xml_parser.create_status_object_list(doc.getElementsByTagName('status'))
            

    def get_replies(self, id=None, since_id=None, max_id=None,
                    count=None, page=None):

        # parse args
        arg_dict = {'id':id , 'since_id':since_id, 'max_id':max_id,
                    'count':count, 'page':page}

        url_param_list = []

        for (key, item) in arg_dict.iteritems():
            if item != None:
                url_param_list.append(key + '=' + str(item))

        # create URL. append querry to a URL
        #url = _REPLIES_URL + '?' + '&'.join(url_param_list)
         
        param = '&'.join(url_param_list)
        if param:
            url = _REPLIES_URL + '?' + param
        else:
            url = _REPLIES_URL 


        # GET request to Twitter
        res, content = self.client.request(url, 'GET')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            doc = minidom.parseString(content)
            return self.xml_parser.create_status_object_list(doc.getElementsByTagName('status'))


    def destroy_status(self, id):
        
        # create URL. Append querry to a URL
        url = _DESTROY_URL % id

        # POST request to Twitter
        res, content = self.client.request(url, 'POST')


        if res['status'] != '200':
            raise TwitterError(res['status'], content)
        else:
            # parse XML
            doc = minidom.parseString(content)
            return self.xml_parser.create_status_object(doc.getElementsByTagName('status')[0])

        




