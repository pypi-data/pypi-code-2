# -*- coding: utf-8 -*-
## Copyright (C) 2011 Jean-Michel CEZ - all rights reserved
## No publication or distribution without authorization.

               
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.app.component.hooks import getSite
from Acquisition import aq_parent, aq_inner

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView

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
		
		
	def unlockItemsObj(self, itemsObj = []):
		""" method for unlocking items """
		items_url = itemsObj
		for item in items_url:
		    obj = self.getPortal().unrestrictedTraverse(item)
		    obj.wl_clearLocks()
		
		return self.request.RESPONSE.redirect(self.getPortal().absolute_url()+'/@@findlockedItems')
		