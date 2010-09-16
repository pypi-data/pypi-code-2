# author: marc goetz
# API for char activity
# based on armory_api

import urllib2,urllib
import xml.dom.minidom

class Activity(object):
    """Activity Sniffer"""

    def __init__(self):

        self.raider_data = {}
        self.activities = []
        self.recent_activities = []
        # needed so we can get the xml-file and not some styled html shit
        self.user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-GB; rv:1.8.1.4) Gecko/20070515 Firefox/2.0.0.4"

    # added language parameter to change the url depending on the language
    def _get_xml(self, language):

        strFile = ""
        try:

            url_de = "http://"+self.raider_data["zone"].lower()+".wowarmory.com/character-feed.atom?r="+self.raider_data["realm"].replace(" ","+")+"&cn="+self.raider_data["name"]+"&locale=de_DE"
            url_en = "http://"+self.raider_data["zone"].lower()+".wowarmory.com/character-feed.atom?r="+self.raider_data["realm"].replace(" ","+")+"&cn="+self.raider_data["name"]+"&locale=en_GB"
            values = {}
            headers = { 'User-Agent' : self.user_agent }
            data = urllib.urlencode(values)
            if language == "de":
                req = urllib2.Request(url_de, data, headers)
            if language == "en":
                req = urllib2.Request(url_en, data, headers)
            response = urllib2.urlopen(req)
            strFile = response.read()
        except Exception, e:
            raise e
        return strFile

    # returns something like
    # [u'Earned the achievement [Neck-Deep in Vile (10 player)].',
    # u'Has now completed [Victories over the Lich King (Icecrown 10 player)] 4 times.',
    # u'Has now completed [Sindragosa kills (Heroic Icecrown 10 player)] 2 times.',
    # u'Has now completed [Valithria Dreamwalker rescues (Heroic Icecrown 10 player)] 4 times.',
    # u"Has now completed [Blood Queen Lana'thel kills (Heroic Icecrown 10 player)] 6 times."]
    def get_activity(self, name, realm, zone, language, count):

        self.raider_data["name"] = name
        self.raider_data["realm"] = realm
        self.raider_data["zone"] = zone

        self.oDoc = xml.dom.minidom.parseString(self._get_xml(language))
        self.activities = self.oDoc.getElementsByTagName("title")
        self.recent_activities = []

        for activity in self.activities[1:count]:
            self.recent_activities.append(activity.childNodes[0].data)

        return self.recent_activities
