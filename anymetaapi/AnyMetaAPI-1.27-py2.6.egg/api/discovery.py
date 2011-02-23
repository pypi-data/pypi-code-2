# Copyright (c) 2008,2009  Mediamatic Lab
# See LICENSE for details.

"""
OAuth endpoint discovery.  TODO: discovery of signature methods;
pydataportability does not seem to parse this.
"""

import httplib
import os
import sys
import tempfile
import urllib

from xml.dom import minidom
from pydataportability.xrds import parser as xrdsparser
from oauth.oauth import OAuthError



class OAuthDiscovery:

    @staticmethod
    def discover(uri):
        """
        Discover the OAuth {request,authorize,access} endpoints and
        possibly the static consumer key at the given URI.
        """
        xml = OAuthDiscovery.__discoverXRDS(uri)
        if xml is None:
            raise OAuthError("Could not discover XRDS file")

        fn = tempfile.mktemp()
        fp = open(fn, 'w')
        fp.write(xml)
        fp.close()

        result = {}

        parser = xrdsparser.XRDSParser(open(fn, 'r'))
        os.unlink(fn)

        for service in parser.services:

            if   service.type == 'http://oauth.net/discovery/1.0/consumer-identity/oob':
                result['oob_uri'] = service.uris[0].uri
            elif service.type == 'http://oauth.net/core/1.0/endpoint/request':
                result['request_uri'] = service.uris[0].uri
            elif service.type == 'http://oauth.net/core/1.0/endpoint/access':
                result['access_uri'] = service.uris[0].uri
            elif service.type == 'http://oauth.net/core/1.0/endpoint/authorize':
                result['authorize_uri'] = service.uris[0].uri
            elif service.type == 'http://oauth.net/discovery/1.0/consumer-identity/static':
                if hasattr(service, 'localid'):
                    # pydataportability.xrds < 0.2
                    result['static_key'] = service.localid.text
                elif hasattr(service, 'localids'):
                    # pydataportability.xrds >= 0.2
                    result['static_key'] = service.localids[0].localid

        return result

    @staticmethod
    def __discoverXRDS(uri, recur = 0):

        if recur > 10:
            return None

        try:
            body, headers = OAuthDiscovery.__request(uri)
        except Exception:
            raise OAuthError("HTTP Error discovering")

        headers = dict(headers)

        if "content-type" in headers and headers['content-type'] == 'application/xrds+xml':
            return body

        location = None

        if 'x-xrds-location' in headers:
            location = headers['x-xrds-location']
        elif 'location' in headers:
            location = headers['location']

        if location is None or location == uri:
            return None

        return OAuthDiscovery.__discoverXRDS(location, recur + 1)


    @staticmethod
    def __request(uri):

        host, path = urllib.splithost(urllib.splittype(uri)[1])
        conn = httplib.HTTPConnection(host)

        headers = {'Accept': 'application/xrds+xml'}
        conn.request('GET', path, '', headers)
        response = conn.getresponse()

        return response.read(), response.getheaders()

