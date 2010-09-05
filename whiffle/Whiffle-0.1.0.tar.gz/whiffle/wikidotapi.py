#! /usr/bin/python

# Whiffle is an interface library for Wikidot.Com

# Copyright (c) 2010 Richard I Urwin

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import ConfigParser
from xmlrpclib import ServerProxy
from utils import Descriptor

## A standard exception to indicate an error in the config file
class ApiError(Exception):
	def __init__(self, desc):
		self.desc = desc
	
	def __str__(self):
		return self.desc

class SemanticError(Exception):
	def __init__(self, desc):
		self.desc = desc
	
	def __str__(self):
		return self.desc

def ReadOnly():
	raise(SemanticError, "Attribute is read-only")
	
class connection(object):
	def __init__(self, user="default", filename="identity.ini"):
		self.user = user			# wikicomma name
		self.filename = filename
		self.pages = None
		self.categories = None
		self.config = ConfigParser.SafeConfigParser({"site":None, "user":None, "key":None})
		self.config.read(filename)
		self.username = self.config.get(user+"@wikidot", "user")
		if self.username == None:
			raise ApiError("User "+user+" not found in "+filename)
		self.defaultsite = self.config.get(user+"@wikidot", "site")
		self.currentsite = self.defaultsite
		self.key = self.config.get(user+"@wikidot", "key")
		if self.key == None:
			raise ApiError("Key not found in section ["+user+"@wikidot] of file "+filename)
		self.server = ServerProxy("https://"+self.username+":"+self.key+"@www.wikidot.com/xml-rpc-api.php")
		# print "I am ", self.username, " with key ", self.key
	
	def page_is_valid(self,name):
		return len(name) < 100 and "/" not in name

	def site_is_valid(self,name):
		return len(name) < 20 and "/" not in name

	def category_is_valid(self,name):
		return len(name) < 100 and "/" not in name and ":" not in name

	def get_site(self):
		if self.site_is_valid(self.currentsite):
			 return self.currentsite
		else:
			raise ApiError("Site name is invalid")
	def set_site(self, site):
		if self.site_is_valid(site):
			self.currentsite = site
		else:
			raise ApiError("Site name is invalid")
	Site = Descriptor(get_site, set_site)
	
	def get_username(self):
		return self.currentsite
	def get_username(self, site):
		self.currentsite = site
	Username = Descriptor(get_username, get_username)


	def refresh_pages(self):
		self.pages = self.server.site.pages ({"site": self.Site})
		return self.pages

	def get_pages(self):
		if self.pages == None:
			self.refresh_pages()
		return self.pages
	Pages = Descriptor(get_pages, ReadOnly)
	
	def mark_new_page(self, page, category="_default"):
		if self.pages != None:
			if self.page_exists(page, category):
				# page already existed
				return
			else:
				 # page was new so invalidate page list
				self.pages = None
		
	def refresh_categories(self):
		self.categories = self.server.site.categories ({"site": self.Site})
		return self.categories

	def get_categories(self):
		if self.categories == None:
			self.refresh_categories()
		return self.categories
	Categories = Descriptor(get_categories, ReadOnly)

	def mark_new_category(self, category):
		if self.categories != None:
			if len(filter (lambda x: x["name"] == category, self.categories)) > 0:
				# category already existed
				return
			else:
				 # category was new so invalidate page list
				self.categories = None

	def general_page_category(self, page, category):
		if category == "_default" and ":" in page:
			p = page.find(":")
			category = page[:p]
			page = page[p+1:]
		return page, category
		
	def fullname(self, page, category="_default"):
		if category =="_default":
			return page
		else:
			return category+":"+page

	def page_exists(self, page, category="_default"):
		page, category = self.general_page_category(page, category)
		return len(filter (lambda x:  x["name"] == page and x["category"] == category, self.Pages)) > 0
		
	def get_page_item(self, page, item, category="_default"):
		page, category = self.general_page_category(page, category)
		p = filter(lambda x:  x["name"] == page and x["category"] == category, self.Pages)
		if len(p) > 1:
			raise ApiError("Two pages with the same name! ("+page+":"+category+")")
		elif len(p) == 0:
			raise ApiError("Page "+page+":"+category+" does not exist")
		else:
			return p[0][item]
		
	def set_page_item(self, page, item, value, create=False, category="_default"):
		page, category = self.general_page_category(page, category)
		if not create:
			p = filter(lambda x:  x["name"] == page and x["category"] == category, self.Pages)
			if len(p) == 0:
				raise ApiError("Page "+page+":"+category+" does not exist")
		
		if not self.page_is_valid(page):
			raise ApiError("Page "+page+":"+category+" is not a valid page name")
		if not self.category_is_valid(category):
			raise ApiError("Page "+page+":"+category+" is not a valid category name")
		self.server.page.save ({"site":self.Site, "page":self.fullname(page, category), item:value})
		
	def add_tag(self, page, tag, category="_default", ErrorIfRedundant=True):
		if not self.page_exists(page, category=category):
			raise ApiError("Page "+page+":"+category+" does not exist")
			
		tags = self.get_page_item(page, "tag_array", category=category)

		if ErrorIfRedundant:
			if tag in tags:
				raise ApiError("Page "+page+":"+category+" already has tag "+tag)
		tags.append(tag)

		self.set_page_item(page, "tags", tags)
		
	def remove_tag(self, page, tag, category="_default", ErrorIfRedundant=True):
		if not self.page_exists(page, category=category):
			raise ApiError("Page "+page+":"+category+" does not exist")
			
		tags = self.get_page_item(page, "tag_array", category=category)

		if ErrorIfRedundant:
			if tag not in tags:
				raise ApiError("Page "+page+":"+category+" does not have tag "+tag)
		if tag in tags:
			tags.remove(tag)

		self.set_page_item(page, "tags", tags)
		
			
		

if __name__ == "__main__":

	api = connection("rurwin")
	
	print api.get_page_item("start","tag_array")
	api.add_tag("start","fred")
	print api.get_page_item("start","tag_array")
	api.remove_tag("start","fred")
	print api.get_page_item("start","tag_array")
	
