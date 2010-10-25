# -*- coding: utf-8 -*-
#
# lj-api.py
#
# This a simple interface to livejournal's flat client/server protocol
#
# Source: http://thinkpython.blogspot.com/2007/02/livejournal-flat-api.html
#
# Updated and extended by Andy Mikhailenko, http://neithere.net
#
#
# The documentation for the Client/Sertver protocols:
# http://www.livejournal.com/doc/server/ljp.csp.protocol.html
#
# The documentation for the flat Client/Server Protocol:
# http://www.livejournal.com/doc/server/ljp.csp.flat.protocol.html
#
#

### EDIT THESE IF NEEDED:

HEADERS = {'User-agent': 'django-ljsync; http://bitbucket.org/neithere/django-ljsync'}

### PLEASE DO NOT EDIT CODE BELOW

import urllib
import datetime
import urllib2
import re

try:
    from hashlib import md5
except ImportError:
    # Python < 2.5
    from md5 import md5


class LiveJournalError(Exception):
    "Exception for protocol errors."
    pass


class LiveJournalClient(object):
    """Pythonic API for LiveJournal. Preserves original glossary.

    Usage::

        >>> username = 'john_doe'
        >>> password = 'mypassword'
        >>> password_md5 = hashlib.md5(password).hexdigest()
        >>> c = LiveJournalClient(username, password_md5)
        >>> c.get_friends()

    .. seealso::

        `LJ FCSP Reference <http://livejournal.com/doc/server/ljp.csp.flat.protocol.html>`_
            LiveJournal Flat Client/Server Protocol Reference.
            This class is a pythonic abstraction for FCSP.
    """
    def __init__(self, username, password_md5):
        if not username or not password_md5:
            raise LiveJournalError('Please specify your LiveJournal username and'
                                   ' MD5 hash of your password.')
        self.username     = username
        self.password_md5 = password_md5

    __repr__ = lambda self: '<LiveJournalClient for %s>' % self.username

    def _do_call(self, args):
        if __debug__: print '_do_call(%s)' % unicode(args)
        request = urllib2.Request("http://livejournal.com/interface/flat",
                                  urllib.urlencode(args), HEADERS)
        resp    = urllib2.urlopen(request)
        l = resp.read().split("\n");
        return dict(zip(l[::2], l[1::2]))

    def _method_call(self, methodname, params):
        challenge = self._do_call({"mode":"getchallenge"})["challenge"]
        data = dict(
            mode           = methodname,
            user           = self.username,
            auth_method    = "challenge",
            auth_challenge = challenge,
            auth_response  = md5(challenge+self.password_md5).hexdigest(),
            ver            = 1,   # only ver=1 supports Unicode
            lineendings    = "unix",
        )
        data.update(params)
        return self._do_call(data)

    def get_events(self, **params):
        """Queries LiveJournal for events (posts) with respect to given params.

        Returns a dictionary::

            {'events': [ {...}, {...}, ... ]}

        :param params: key/value pairs according to LJ FCSP.
        """

        # TODO: use _get_details()
        
        data = self._method_call("getevents", params)

        if data.get('success') != 'OK':
            raise LiveJournalError(data.get('errmsg', 'No error message provided'))

        r = re.compile("(events|prop)_(\\d+)_(\\w+)")
        events = [{} for i in range(int(data["events_count"]))]
        props  = [{} for i in range(int(data["prop_count"]))]

        details = {"events":events}
        for name, value in data.items():
            match = r.match(name)
            if match:
                number = int(match.group(2))
                field = match.group(3)
                if match.group(1)=="events":
                    events[number-1][field] = value
                else:
                    props[number-1][field] = value
            else:
                details[name] = value

        propdict = {}
        for p in props:
            propdict.setdefault(p['itemid'], {})[p['name']] = p['value']
        #print propdict.keys()
        #print [event['itemid'] for event in events]
        for event in events:
            eventprops = propdict.get(event.get('itemid'),{})
            event.update(eventprops)
        return details

    def add_event(self, event, subject, date=datetime.datetime.now(), security=''):
        params = dict(
            subject  = subject.encode('utf-8'),
            event    = event.encode('utf-8'),   #urllib.quote_plus(event.encode('utf-8')),
            year     = date.year,
            mon      = date.month,
            day      = date.day,
            hour     = date.hour,
            min      = date.minute,
            security = security,
        )
        data = self._method_call("postevent", params)
        
        if data.get('success') != 'OK':
            raise LiveJournalError(data.get('errmsg', 'No error message provided'))
        return data.get('itemid', None)

    def edit_event(self, event):
        raise NotImplementedError

    def _get_details(self, meth, params):
        """ Calls given method and parses returned details into nested
        dictionaries. If the server cannot return requested data, LiveJournalError
        exception is raised.

        All parameters should be given according to the LJ FCSP.

        :param meth: method name
        :param params: key/value pairs
        """
        data = self._method_call(meth, params)

        try:
            if data.pop('success') != 'OK':
                message = data.get('errmsg', 'No error message provided')
                raise LiveJournalError(message)
        except KeyError:
            raise LiveJournalError('No success flag in returned data')

        # resolve data into nested dictionaries
        details = {}
        for name, value in data.items():
            bits = name.split('_')
            if len(bits) > 2 and bits[1].isdigit():
                # "article_123_title" or "friend_n_identity_display"
                kind = bits.pop(0)
                num  = int(bits.pop(0))
                attr = '_'.join(bits)
                # {'article': {123: {'title': value}}}
                details.setdefault(kind,{}).setdefault(int(num),{})[attr] = value
            else:
                details[name] = value
        return details

    def get_groups(self, **params):
        """ Retrieves a list of the user's defined groups of friends.

        :param params: key/value pairs according to LJ FCSP.

        Example of returned data for 1..n records::

            {'max_num': n,
             'items': [
                 {'name': 'buddies', 'sortorder': '5'},
                 {'name': 'colleagues', 'sortorder': '10'},
                 ...
                ]
            }

        .. note::

            `max_num` not necessarily equals the number of currently existing groups.
        """
        data = self._get_details('getfriendgroups', params)
        items = [item for num, item in data['frgrp'].iteritems()]
        return {'items': items,
                'max_num': data['frgrp_maxnum']}

    def get_friends(self, **params):
        """ Returns a list of which other LiveJournal users this user lists as
        their friend.

        :param params: key/value pairs according to LJ FCSP.

        Example of returned data for 1..n records::

            {'count': n,
             'items': [
                 {'user': 'john_doe', 'name': 'John Doe',
                  'groupmask': '17', 'bg': '#ffffff', 'fg': '#000000'},
                 ...
                ]
            }

        """
        data = self._get_details('getfriends', params)
        items = [item for num, item in data['friend'].iteritems()]
        return {'items': items,
                'count': data['friend_count']}

    def get_daycounts(self, **params):
        """ This mode retrieves the number of journal entries per day. Useful for
        populating calendar widgets in GUI clients.

        :param params: key/value pairs according to LJ FCSP.

        Example of returned data::

            {'2007-10-22': 2, '2007-10-25': 1}

        Days with no entries are omitted in the results.
        """
        data = self._get_details('getdaycounts', params)
        return dict((dt, int(cnt)) for dt, cnt in data.iteritems())
