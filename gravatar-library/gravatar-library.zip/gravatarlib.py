#!/usr/bin/python
# -*- coding: utf-8 -*-



##################################################
#       GRavatar Library
#-------------------------------------------------
#   Copyright:    (c) 2011 by Damjan Krstevski.
#   License:      GNU General Public License (GPL)
#   Feedback:     krstevsky[at]gmail[dot]com
##################################################




"""
    GRavatar Library - Python
    http://en.gravatar.com/
    This module will help you to communicate with the web services from the GRavatar!
    The module will allows you to get the avatars and profile information from GRavatar.
    FeedBack: krstevsky[at]gmail[dot]com

    Usage:
    import GRavatarLib
    try:
        grav = GRavatarLib.GRavatar()
        avatar = grav.avatar(email)
        profil = grav.profile(user) # or email
    except Exception as ex:
        print str( ex )

    Exceptions:
        GRavatarException()
"""


# Public Symbols
__all__ 		= ["avatar", "profile", "data"]

__version__             = "1.0.0"



# Import required modules
import re, sys, hashlib

try:
    if sys.version[0] == '2':
        import urllib2, urllib
    else:
        import urllib.request as urllib2
except:
    raise ImportError("Some modules can not be imported!")



# Class GRavatarException. Exception Message
class GRavatarException(Exception):
    ''' Class GRavatarException. Exception Message '''
    pass



# Class GRavatar
class GRavatar(object):
    ''' Class GRavatar '''

    # Class Constructor
    def __init__(self):
        ''' Class Constructor '''
        self.data = None


    # Class Destructor
    def __del__(self):
        ''' Class Destructor '''
        self.data = None


    # Set the data value
    def __set_data(self, data):
        ''' Set the data value '''
        self.__data = data


    # Get the data value
    def data(self):
        ''' Get the data value '''
        return self.__data

    
    # Set the exception message
    def __set_error(error):
        ''' Set the exception message '''
        raise GRavatarException(error)


    # Get the opener
    def __get_opener( self, ua = 'GRavatar Agent - Python' ):
        ''' Get the opener '''
        opener = None
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', ua)]
        except Exception as ex:
            raise GRavatarException( str(ex) )
        return opener


    # Read the data from URL
    def __read(self, url = None):
        ''' Read the data from URL '''
        if not url:
            raise GRavatarException('URL must have a value!')

        try:
            req = self.__get_opener()
            tdata = req.open(url).read()
            req.close()

            ''' Set the data value '''
            self.__set_data(tdata)
            
            return tdata
        except Exception as ex:
            raise GRavatarException( str(ex) )

        
    # E-Mail Validation
    def __is_email( self, email, minlen = 7, maxlen = 45 ):
        ''' E-Mail Validation '''
        _len = len( email )
        if _len > minlen and _len < maxlen:
            regex = '^(\\[?)[a-zA-Z0-9\\-\\.\\_]+\\@(\\[?)[a-zA-Z0-9\\-]+\\.([a-zA-Z]{2,4})(\\]?)$'
            if re.match(regex, email) != None:
                return True
        return False


    # Get the user's avatar from the gravatar
    def avatar(self, email = None, size = 40, default = 'http://www.example.com/default.jpg'):
        ''' Get the user's avatar from the gravatar '''
        if not email:
            raise GRavatarException("User must have a value!")

        try:
            ''' Validate E-Mail Address '''
            if self.__is_email(email) == False:
                raise GRavatarException("Invalid E-Mail address!")

            ''' Generate the image link '''
            gurl = "http://www.gravatar.com/avatar/" + hashlib.md5( email.lower() ).hexdigest() + "?"
            gurl += urllib.urlencode( {'d' : default, 's' : str( size )} )

            ''' Set the data value '''
            self.__set_data(gurl)
            return gurl
        except Exception as ex:
            raise GRavatarException( str(ex) )


    # Get the user's profile from the gravatar
    def profile(self, user = None):
        ''' Get the user's profile from the gravatar (XML Format)'''
        if not user:
            raise GRavatarException("User must have a value!")

        try:
            gurl = None
            if self.__is_email( user ) == True:
                gurl = "http://www.gravatar.com/" + hashlib.md5( user.lower() ).hexdigest() + ".xml"
                return self.__read( gurl )
            else:
                gurl = "http://www.gravatar.com/" + user.lower().strip() + ".xml"
                return self.__read( gurl )
        except Exception as ex:
            raise GRavatarException( str(ex) )
