# author: marc goetz
# API for realmstatus
# based on armory_api

import urllib2,urllib
import xml.dom.minidom

class Realmstatus(object):
    """ Realmstatus Sniffer """

    def __init__(self):

        # needed so we can get the xml-file and not some styled html shit
        self.userAgent = "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4"

    def _get_xml(self):

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
    def get_realm_status(self, *names):

        self.oDoc = xml.dom.minidom.parseString(self._get_xml())
        self.realms = self.oDoc.getElementsByTagName("item")
        self.realmstatus = {}

        for name in names:
            for status in self.realms:
                if status.getElementsByTagName("title")[0].childNodes[0].data == name:
                    self.realmstatus[name] = status.getElementsByTagName("category")[0].childNodes[0].data

        return self.realmstatus

    # returns something like "PvP" or "PvE"
    def get_realm_type(self, *names):

        self.realmtype = {}

        for name in names:
            for type in self.realms:
                if type.getElementsByTagName("title")[0].childNodes[0].data == name:
                    self.realmtype[name] = type.getElementsByTagName("category")[2].childNodes[0].data

        return self.realmtype
