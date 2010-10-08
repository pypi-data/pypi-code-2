#!/usr/bin/env python

import sys, time, os, urllib2, shelve, string, xmltramp, mimetools, mimetypes, md5, traceback
#
#   uploadr.py
#
#   Upload images to your Flickr account.
#
#   Requires:
#       xmltramp http://www.aaronsw.com/2002/xmltramp/
#       flickr account http://flickr.com
#
#   Inspired by:
#        http://micampe.it/things/flickruploadr
#        http://berserk.org/uploadr/
#
#   Usage:
#
#   October 2005
#   Cameron Mallory   cmallory/berserk.org
#   Jean-François Roche - Plone Integration - jfroche@jfroche.be
#
#   This code has been updated to use the new Auth API from flickr.
#   This code has beeen updated to be used inside Plone
#
#   This code has been adapted by David Jonas to be used for the Products.republisher


class APIConstants:
    base = "http://flickr.com/services/"
    rest   = base + "rest/"
    auth   = base + "auth/"
    upload = base + "upload/"
    token = "auth_token"
    secret = "secret"
    key = "api_key"
    sig = "api_sig"
    frob = "frob"
    perms = "perms"
    method = "method"

    def __init__( self ):
       pass

api = APIConstants()

class Uploadr:
    FLICKR = {"title": "",
        "description": "",
        "tags": "auto-upload",
        "is_public": "1",
        "is_friend": "0",
        "is_family": "0",
        "secret":    "",
        "api_key":   ""
        }

    token = None
    perms = ""

    def __init__( self, frob=None, token=None):
        self.uploaded = {}
        if(frob):
            self.FLICKR[api.frob]=frob
        self.token = token

    def setIsPublic(self, bool):
        self.FLICKR["is_public"] = str(bool)

    def setIsFriend(self, bool):
        self.FLICKR["is_friend"] = str(bool)

    def setIsFamily(self, bool):
        self.FLICKR["is_family"] = str(bool)

    def setTag(self,tag):
        self.FLICKR["tags"] = str(tag)

    def setTitle(self,title):
        self.FLICKR["title"] = str(title)

    def setDescription(self,description):
        self.FLICKR["description"] = str(description)
        
    #Adapted by David Jonas for Products.republisher Plone Product
    def setAPIKeyAndSecret(self, key, secret):
        self.FLICKR["api_key"] = str(key)
        self.FLICKR["secret"] = str(secret)

    """
    Signs args via md5 per http://www.flickr.com/services/api/auth.spec.html (Section 8)
    """
    def signCall( self, data):
        keys = data.keys()
        keys.sort()
        foo = ""
        for a in keys:
            foo += (a + data[a])

        f = self.FLICKR[ api.secret ] + api.key + self.FLICKR[ api.key ] + foo
        #f = api.key + FLICKR[ api.key ] + foo
        return md5.new( f ).hexdigest()

    def urlGen( self , base,data, sig ):
        foo = base + "?"
        for d in data:
            foo += d + "=" + data[d] + "&"
        return foo + api.key + "=" + self.FLICKR[ api.key ] + "&" + api.sig + "=" + sig

    #
    #   Authenticate user so we can upload images
    #
    def authenticate( self ):
        #print "Getting new Token"
        frob = self.getFrob()
        url = self.getAuthKey()
        self.getToken()

    """
    flickr.auth.getFrob

    Returns a frob to be used during authentication. This method call must be
    signed.

    This method does not require authentication.
    Arguments

    api.key (Required)
    Your API application key. See here for more details.
    """
    def getFrob( self ):
        d = { 
            api.method  : "flickr.auth.getFrob"
            }
        sig = self.signCall( d )
        url = self.urlGen( api.rest, d, sig )
        try:
            response = self.getResponse( url )
            if ( self.isGood( response ) ):
                self.FLICKR[ api.frob ] = str(response.frob)
                return response.frob
            else:
                self.reportError( response )
                return None
        except:
            print "Error getting frob:"
            traceback.print_exc()


    """
    Checks to see if the user has authenticated this application
    """
    def getAuthKey( self ):
        d =  {
            api.frob : self.FLICKR[ api.frob ],
            api.perms : "write"
            }
        sig = self.signCall( d )
        url = self.urlGen( api.auth, d, sig )
        ans = ""
        return url
    
    def getTokenValue(self):
        return self.token


    """
    http://www.flickr.com/services/api/flickr.auth.getToken.html
    flickr.auth.getToken
    Returns the auth token for the given frob, if one has been attached. This method call must be signed.
    Authentication
    This method does not require authentication.
    Arguments
    NTC: We need to store the token in a file so we can get it and then check it insted of
    getting a new on all the time.
    api.key (Required)
       Your API application key. See here for more details.
    frob (Required)
       The frob to check.
    """
    def getToken( self ):
        d = {
            api.method : "flickr.auth.getToken",
            api.frob : str(self.FLICKR[ api.frob ])
        }
        sig = self.signCall( d )
        url = self.urlGen( api.rest, d, sig )
        try:
            res = self.getResponse( url )
            if ( self.isGood( res ) ):
                self.token = str(res.auth.token)
                self.perms = str(res.auth.perms)
                return 1
            else :
                self.reportError( res )
                return 0
        except:
            traceback.print_exc()

    """
    flickr.auth.checkToken

    Returns the credentials attached to an authentication token.
    Authentication
    This method does not require authentication.
    Arguments
    api.key (Required)
        Your API application key. See here for more details.
    auth_token (Required)
        The authentication token to check.
    """
    def checkToken( self ):
        if ( self.token == None ):
            return False
        else :
            d = {
                api.token  :  str(self.token) ,
                api.method :  "flickr.auth.checkToken"
            }
            sig = self.signCall( d )
            url = self.urlGen( api.rest, d, sig )
            try:
                res = self.getResponse( url )
                if ( self.isGood( res ) ):
                    self.token = res.auth.token
                    self.perms = res.auth.perms
                    return True
                else :
                    self.reportError( res )
            except:
                traceback.print_exc()
            return False

    def uploadImageFromData(self, data, filename):
        #print "Uploading data"
        try:
            photo = ('photo', filename, data)
            d = {
                api.token   : str(self.token),
                api.perms   : str(self.perms),
                "title"     : str( self.FLICKR["title"]),
                "description":str( self.FLICKR["description"]),
                "tags"      : str( self.FLICKR["tags"] ),
                "is_public" : str( self.FLICKR["is_public"] ),
                "is_friend" : str( self.FLICKR["is_friend"] ),
                "is_family" : str( self.FLICKR["is_family"] )
            }
            sig = self.signCall( d )
            d[ api.sig ] = sig
            d[ api.key ] = self.FLICKR[ api.key ]
            url = self.build_request(api.upload, d, (photo,))
            xml = urllib2.urlopen( url ).read()
            res = xmltramp.parse(xml)
            if ( self.isGood( res ) ):
                #print "successful: " + str(res)
                self.logUpload( res.photoid, filename )
                return res.photoid
            else :
                #print "problem... " + str(res)
                self.reportError( res )
                return 0
        except:
            traceback.print_exc()

    def logUpload( self, photoID, imageName ):
        photoID = str( photoID )
        imageName = str( imageName )
        self.uploaded[ imageName ] = photoID
        self.uploaded[ photoID ] = imageName

    #
    #
    # build_request/encode_multipart_formdata code is from www.voidspace.org.uk/atlantibots/pythonutils.html
    #
    #
    def build_request(self, theurl, fields, files, txheaders=None):
        """
        Given the fields to set and the files to encode it returns a fully formed urllib2.Request object.
        You can optionally pass in additional headers to encode into the opject. (Content-type and Content-length will be overridden if they are set).
        fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
        """
        content_type, body = self.encode_multipart_formdata(fields, files)
        if not txheaders: txheaders = {}
        txheaders['Content-type'] = content_type
        txheaders['Content-length'] = str(len(body))

        return urllib2.Request(theurl, body, txheaders)

    def encode_multipart_formdata(self,fields, files, BOUNDARY = '-----'+mimetools.choose_boundary()+'-----'):
        """ Encodes fields and files for uploading.
        fields is a sequence of (name, value) elements for regular form fields - or a dictionary.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files.
        Return (content_type, body) ready for urllib2.Request instance
        You can optionally pass in a boundary string to use or we'll let mimetools provide one.
        """
        CRLF = '\r\n'
        L = []
        if isinstance(fields, dict):
            fields = fields.items()
        for (key, value) in fields:
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"' % key)
            L.append('')
            L.append(value)
        for (key, filename, value) in files:
            filetype = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            L.append('--' + BOUNDARY)
            L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
            L.append('Content-Type: %s' % filetype)
            L.append('')
            L.append(value)
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY        # XXX what if no files are encoded
        return content_type, body


    def isGood( self, res ):
        if ( not res == "" and res('stat') == "ok" ):
            return True
        else :
            return False

    def reportError( self, res ):
        try:
            self.ErrMsg = "Error:", str( res.err('code') + " " + res.err('msg') )
            print self.ErrMsg
        except:
            self.ErrMsg = "Error: " + str( res )
            return self.ErrMsg

    def getError(self):
        return self.ErrMsg

    """
    Send the url and get a response.  Let errors float up
    """
    def getResponse( self, url ):
        xml = urllib2.urlopen( url ).read()
        #print xml
        return xmltramp.parse( xml )

    def getSetList(self):
        d = {
                api.token  :  str(self.token) ,
                api.method :  "flickr.photosets.getList"
        }
        sig = self.signCall( d )
        url = self.urlGen( api.rest, d, sig )
        res = self.getResponse( url )
        listOfSets = []
        for set in res.photosets:
            dict = {}
            dict['id'] = str(set('id'))
            dict['title'] = str(set.title)
            dict['description'] = str(set.description)
            listOfSets.append(dict)
        return listOfSets

    def getSetPhotos(self, setName, photoSizeInSet='Large'):
        d = {
            api.token : str(self.token),
            api.method : "flickr.photosets.getPhotos",
            "photoset_id" : setName
        }
        sig = self.signCall( d )
        url = self.urlGen( api.rest, d, sig )
        photosSets = self.getResponse( url )
        listPhotos = []
        for photosSet in photosSets:
            for photo in photosSet:
                dict = {}
                dict['id'] = photo('id')
                dict['title'] = photo('title')
                dict['url'] = self.getPhotoURL(dict['id'], photoSizeInSet)
                dict['data'] = urllib2.urlopen( dict['url'] ).read()
                listPhotos.append(dict)
        return listPhotos

    def getPhotoURL(self, photoId, photoSize='Large'):
        d = {
            api.token : str(self.token),
            api.method : "flickr.photos.getSizes",
            "photo_id" : photoId
        }
        sig = self.signCall( d )
        url = self.urlGen( api.rest, d, sig )
        photoSizes = self.getResponse( url )
        for sizes in photoSizes:
            for size in sizes:
                if (str(size('label')) == photoSize):
                    return str(size('source'))

if __name__ == "__main__":
    flick = Uploadr()
    file = open('/opt/zope2.7.8/Products/ATPhoto/tests/input/canoneye.jpg','rb')
    frob = flick.getFrob()
    print "Frob: %s" % frob
    url = flick.getAuthKey()
    print "Url: %s" % url
#    flick.upload()
    print "sleeping.."
    time.sleep(20)
    print "back"
    flick2 = Uploadr(frob=str(frob))
    url = flick2.getAuthKey()
    print "Url After: %s" % url
    flick2.getToken()
    res = flick2.getSetList()
    photoDict = flick2.getSetPhotos(res[0]['id'])
#    flick2.setDescription("c'est genial!!!")
#    flick2.setTitle("My eye")
#    flick2.setTag("eye nice")
#    flick2.uploadImageFromData(file.read(),'canoneye.jpg')
#    flick.run()
