# -*- coding: utf-8 -*-

import json
import socket
import urllib2
from contextlib import closing, nested
from urllib import urlencode

__all__ = [
    "GoogleTranslator",
]

class GoogleTranslator(object):
    """
    Translator with Google Translate API
    http://code.google.com/intl/ja/apis/language/translate/overview.html
    see also
    Google Translate API Terms of Use
    http://code.google.com/intl/ja/apis/language/translate/terms.html
    """
    domain = "ajax.googleapis.com"
    common_path = "/ajax/services/language/"
    key = "ABQIAAAAK6kpHnylgmAYtO7ZX01XXRSvW2ISZ2KI4wU-F"\
          "k6WlRk77d73EhTtYeI1LUl3BfkKv-17KKEWzdRTMw"
    userip = socket.gethostbyname(socket.gethostname())

    def __init__(self, lang_from, lang_to, handler):
        self.lang_from = lang_from
        self.lang_to = lang_to
        self.handler = handler
        self._url = "http://{0}{1}".format(self.domain, self.common_path)

    def get_api_path(self, func):
        return "{0}?".format(func.func_name)

    def get_url(self, func, query):
        return "{0}{1}{2}".format(self._url,
                self.get_api_path(func), urlencode(query))

    def request(self, url):
        req = urllib2.Request(url)
        with closing(urllib2.urlopen(req)) as res:
            res_json = json.loads(res.read())
            if res_json["responseStatus"] == 200:
                response = res_json["responseData"]
            else:
                raise RuntimeError(res_json)
        return response

    def call_api(self, func, query, key=None):
        """high-level method to make url and request"""
        url = self.get_url(func, query)
        response = self.request(url)
        if key:
            response = response[key]
        return self.api(), response

    def detect(self, text):
        """ JSON Developer's Guide for Language Detect
        http://code.google.com/intl/ja/apis/language/translate/v1/\
        using_rest_langdetect.html
        """
        query = {
            "v": "1.0",
            "q": text.encode("utf-8"),
            "key": self.key,
            "userip": self.userip,
        }
        api, response = self.call_api(self.detect, query, "language")
        yield api, response

    def translate(self, text):
        """ JSON Developer's Guide for Translate
        http://code.google.com/intl/ja/apis/language/translate/v1/\
        using_rest_translate.html
        """
        query = {
            "v": "1.0",
            "q": text.encode("utf-8"),
            "langpair": "{0}|{1}".format(self.lang_from, self.lang_to),
            "key": self.key,
            "userip": self.userip,
        }
        _key = "translatedText"
        api, response = self.call_api(self.translate, query, _key)
        yield api, response
