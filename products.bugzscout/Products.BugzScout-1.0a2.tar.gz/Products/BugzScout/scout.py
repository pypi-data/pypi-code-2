# -*- coding: utf-8 -*-
import urllib
import urllib2
from xml.etree.ElementTree import XML
from zope.interface import implements
from Products.BugzScout.interfaces import IBugzScoutReporter


class BugzScoutReporter(object):
    implements(IBugzScoutReporter)

    def report(self, uri, username, email, project, area, description):
        uri = uri.rstrip('/')
        bugzscout_uri = '/'.join([uri, 'ScoutSubmit.asp'])
        data = {'ScoutUserName': username,
                'ScoutProject': project,
                'ScoutArea': area,
                'Description': description,
                ##'Extra': '',
                'Email': email,
                'ForceNewBug': 0,  # 0=appendOrCreate 1=alwaysCreateNew
                ##'ScoutDefaultMessage': '',
                'FriendlyResponse': 0,  # 0=xml 1=html
                }
        data = urllib.urlencode(data)
        try:
            response = urllib2.urlopen(bugzscout_uri, data)
        except urllib2.HTTPError, err:
            return False
        response_message = XML(response.read())
        return response_message.tag == 'Success'


def bugz_scout_reporter_factory():
    return BugzScoutReporter()
