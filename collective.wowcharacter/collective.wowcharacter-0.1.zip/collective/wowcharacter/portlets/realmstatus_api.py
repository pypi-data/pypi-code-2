# author: marc goetz
# API for realmstatus
# based on armory_api

import urllib2,urllib
import xml.dom.minidom

class Realmstatus(object):
    """ Realmstatus Sniffer """

    def __init__(self):

        self.status = ""
        # needed so we can get the xml-file and not some styled html shit
        self.userAgent = "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4"

    def _getXML(self):

        strFile = ""

        try:
            url = "http://www.wow-europe.com/realmstatus/index.xml"
            values = {}
            headers = { 'User-Agent' : "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4" }
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data, headers)
            response = urllib2.urlopen(req)
            strFile = response.read()
        except Exception, e:
            raise e
        return strFile

    # returns "Realm Up" or "Realm Down"
    def get_realm_status(self, name):

        self.oDoc = xml.dom.minidom.parseString( self._getXML() )
        self.realms = self.oDoc.getElementsByTagName("item")

        for title in self.realms:
            if title.getElementsByTagName("title")[0].childNodes[0].data == name:
                return title.getElementsByTagName("category")[0].childNodes[0].data

        return "Realm not found"

    # returns something like "PvP" or "PvE"
    def get_realm_type(self, name):

        for type in self.realms:
            if type.getElementsByTagName("title")[0].childNodes[0].data == name:
                return type.getElementsByTagName("category")[2].childNodes[0].data

        return "Realm not found"
