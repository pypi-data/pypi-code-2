# -*- coding: utf-8 -*-
import urllib
from httplib2 import Http
from urlparse import urlparse

class html_jumping(object):
    def get(self, config, headers = {}):
        rest = Http()
        cookie = ''
        url = ''
        if headers.get('Cookie'):
            cookie = headers.get('Cookie')
        if headers.get('Referer'):
            headers['Referer'] = headers.get('Referer')
    
        for config_el in config['route']:
            headers = {}
            if cookie != '':
                headers['Cookie'] = cookie
            if url != '':
                headers['Referer'] = url
            if len(config_el) == 3:
                if not headers.get('Content-Type'):
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                if config_el[1] == "GET":
                    baseUrl = config_el[0]
                    parsedUrl = urlparse(baseUrl)
                    if not parsedUrl.query:
                        baseUrl += "?%s" % urllib.urlencode(config_el[2])
                    else:
                        baseUrl += "&%s" % urllib.urlencode(config_el[2])
                    response, content = rest.request(baseUrl, config_el[1], headers=headers)
                else:
                    response, content = rest.request(config_el[0], config_el[1], headers=headers, body=urllib.urlencode(config_el[2]))
            elif len(config_el) == 2:
                response, content = rest.request(config_el[0], config_el[1], headers=headers)
            else:
                raise Exception()
            if response.get('set-cookie'):
                cookie = response['set-cookie']
            url = config_el[0]
        return response, content