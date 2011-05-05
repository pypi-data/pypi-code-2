# -*- coding: utf-8 -*-
## Copyright (C) 2011 Jean-Michel CEZ - all rights reserved
## No publication or distribution without authorization.

               
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from Acquisition import aq_parent, aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
try:
	from json import JSONEncoder
except:
	from simplejson import JSONEncoder
import string 
# sample return JSONEncoder().encode(results)

class UnlockItems(BrowserView):
	""" this class search in portalcatalog all documents  and unlock items if they are locked """
	
	def getPortal(self):
		""" return portal object """
		portal = getSite()
		return portal
		
	def getPortalCatalog(self):
		"""return portal catalog"""
		cat = getToolByName(self.getPortal(),'portal_catalog')
		return cat
		
	def searchContents(self):
		""" find contents in site"""
		cat = self.getPortalCatalog()
		path = self.getPortal().id+'/'
		query = {'path':path,'sort_on':'getId'}
		results = self.getPortalCatalog().searchResults(**query)
		return results
	
	def getLockedItems(self):
		""" find and return a list of locked items """
		lockedItems = []
		res = self.searchContents()
		for item in res:
			if item.getObject().wl_isLocked():
				lockedItems.append(item)
		return lockedItems
		
	def unlockItemsObj(self, items_ids = None):
		""" method for unlocking items """
		items = string.split(items_ids,',')
		cat = self.getPortalCatalog()
		path = self.getPortal().id+'/'
		for item in items:
			query = {'path':path, 'id':item, 'sort_on':'getId'}
			res = cat.searchResults(**query)
			for brain in res:
				obj = brain.getObject()
				obj.wl_clearLocks()
		
		return
		
		
		
	
