# -*- coding: utf-8 -*-

from zope import component
from Products.CMFCore.utils import getToolByName

def setupVarious(context):
    portal = context.getSite()
    
    if context.readDataFile('redturtle.imagedevent_various.txt') is None: 
        return


    