# -*- coding: utf-8 -*-
# feed2twitter
# Copyright (C) 2009 EBC - Empresa Brasil de Comunicação
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

import urllib
from xml.dom.minidom import parseString

class ShortenerException(Exception):
    pass

class TinyURL(object):
    def short(self,url):
        try:
            params = urllib.urlencode({'url':url})
            fp = urllib.urlopen("http://tinyurl.com/api-create.php", params)
	    short_url = fp.read()
	    if 'http' not in short_url:
                raise ShortenerException('tinyurl error')
            return short_url

        except IOError, e:
            raise ShortenerException('tinyurl error')


class MiudIn(object):
    def short(self,url):
        try:
            params = urllib.urlencode({'url':url})
            fp = urllib.urlopen("http://miud.in/api-create.php", params)
	    short_url = fp.read()
	    if 'http' not in short_url:
                raise ShortenerException('miud.in error')
            return short_url

        except IOError, e:
            raise ShortenerException('miud.in error')


class IsGD(object):
    def short(self,url):
        try:
            params = urllib.urlencode({'longurl':url})
            url = "http://is.gd/api.php?%s" % params
            fp = urllib.urlopen(url)
	    short_url = fp.read()
	    if 'http' not in short_url:
                raise ShortenerException('tinyurl error')
	    return short_url

        except IOError, e:
            raise ShortenerException('Is.gd error')

class MigreME(object):
    def short(self,url):
        try:
            params = urllib.urlencode({'url':url})
            url = "http://migre.me/api.xml?%s" % params
            fp = urllib.urlopen(url)
            dom = parseString(fp.read())
	    short_url = dom.getElementsByTagName('migre')[0].childNodes[0].data
	    if 'http' not in short_url:
                raise ShortenerException('tinyurl error')
	    return short_url

        except IOError, e:
            raise ShortenerException('migreme error')

services = {
    'tinyurl' : TinyURL,
    'is.gd' : IsGD,
    'migre.me' : MigreME,
    'miud.in' : MiudIn
}
