#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import base64
import json
import urllib
import urllib2

# I use the json format (yo can use XML too)
IMGUR_UPLOAD_URL = 'http://api.imgur.com/2/upload.json'
# Note: This key is specific for Scru.
# If you want to use the Imgur API in your application,
# please apply for an API key at: http://imgur.com/register/api/
API_KEY = '60bbfaa8c24ff3428c4591ed252523ff'


class ApiKeyNotSpecified(Exception):
    """'No API key is specified"""


def upload(image, api_key=API_KEY):
    """Upload a image to imgur using the public API"""
    # If the image is a file only read the image
    # If is a path open the file and read it
    if getattr(image, 'read'):
        im = image.read()
        image.close()
    else:
        with open(image, 'rb') as f:
            im = f.read()
    # Error when no AI key is specified
    if not api_key:
        raise ApiKeyNotSpecified
    else:
        # The image need to be encoded to base64
        data = {
            'key': api_key,
            'image': im.encode('base64'),
            }
        request = urllib2.Request(IMGUR_UPLOAD_URL, urllib.urlencode(data))
        response = urllib2.urlopen(request)
        data = json.loads(response.read())
        response.close()
        return data
