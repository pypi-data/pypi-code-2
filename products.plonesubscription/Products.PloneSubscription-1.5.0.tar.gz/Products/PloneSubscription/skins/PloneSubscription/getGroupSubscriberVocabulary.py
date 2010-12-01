## Script (Python) "getGroupSubscriberVocabulary"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##
# -*- coding: utf-8 -*-
""" Wrapper for getGroupSubscriberVocabulary method """

from Products.CMFCore.utils import getToolByName

return getToolByName(context, 'portal_subscription').getGroupSubscriberVocabulary()
