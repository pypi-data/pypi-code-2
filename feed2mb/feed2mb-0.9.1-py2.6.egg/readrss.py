# -*- coding: utf-8 -*-
# feed2mb
# Copyright (C) 2008 EBC - Empresa Brasil de Comunicação
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import feedparser, pickle, time
import os.path
from os import mkdir
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class FeedDateTimeException(Exception):
    pass

class parse(object):

    def __init__(self,feed_url,service, alias):
        self.feed_url = feed_url
        self.service = service
        self.feed = feedparser.parse(feed_url)
        self.alias = alias
        self.directory = os.path.expanduser("~/.feed2mb/")
        try:
            import hashlib
            md = hashlib.md5()
        except ImportError:
            # for Python << 2.5
            import md5
            md = md5.new()
        md.update(self.feed_url + self.service)
	md5name = md.hexdigest()
        self.filename = self.directory + md5name

    def updateLastRead(self,item=None):
        if not os.path.exists(self.directory):
            mkdir(self.directory)
        output = open(self.filename, 'wb')
        key = 'updated_parsed'
        if not item:
            if 'published_parsed' in self.feed['items'][0]:
                key = 'published_parsed'
            pickle.dump(self.feed['items'][0][key], output)
        else:
            if 'published_parsed' in item:
                key = 'published_parsed'
            else:
                key = 'updated_parsed'
            if item[key] is None:
                raise FeedDateTimeException("Your item on " + self.alias+ " doesn't appear to have a valid date of publication. Feed2mb needs it!")
            log.info('updating last time that the feed was read to ' + time.strftime("%Y-%m-%d %H:%M:%S",item[key]))

            pickle.dump(item[key], output)
        output.close()

    def getlastRead(self):
        log.debug('Getting the last time that the feed on ' + self.alias+ ' was published')
        try:
            pick = open(self.filename, 'rb')
        except IOError:
            return False
        try:
            last_read = pickle.load(pick)
        except EOFError:
            return False
	log.debug('source feed for ' + self.alias + ' last read on: '+ time.strftime("%Y-%m-%d %H:%M:%S",last_read))
        return last_read



