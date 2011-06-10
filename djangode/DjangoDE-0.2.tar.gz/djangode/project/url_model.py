# DjangoDE, an integrated development environment for Django
# Copyright (C) 2010-2011 Andrew Wilkinson
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

class UrlModel(object):
    def  __init__(self, urls=None):
        self.urls = urls

        self.root_url = UrlInclude("^/")

        if self.urls is not None:
            self.parse_urls(self.root_url, self.urls)

    def parse_urls(self, parent, urls):
        for url in urls:
            if len(url) == 2:
                inc = UrlInclude(url[0])
                self.parse_urls(inc, url[1])

                parent.children.append(inc)
            else:
                parent.children.append(Url(url[0], url[1], url[2]))

class Url(object):
    def __init__(self, re_text, func_name, url_name):
        self.re_text = re_text
        self.func_name = func_name
        self.url_name = url_name

    def __repr__(self):
        return "%s (%s)" % (self.re_text, self.func_name)

class UrlInclude(object):
    def __init__(self, re_text):
        self.re_text = re_text
        self.children = []

    def __repr__(self):
        return "%s (%s)" % (self.re_text, repr(self.children))
