## Script (Python) "subscriptionMaintenance"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Script used by PloneMaintenance
##
# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zLOG import LOG, INFO

stool = getToolByName(context, 'portal_subscription')

stool.mailing()

LOG("Subscription mailing script : ", INFO, "script has run")

return "script has run"
