# -*- coding: utf-8 -*-

try:
    import pysrt
except ImportError:
    pysrt = False

from Products.CMFCore.utils import getToolByName
from collective.subrip2html.transform import SrtToHtml
from collective.subrip2html.mimetype import SubRipMimetype

def setupVarious(context):
    if not context.readDataFile('collective.subrip2html_various.txt'):
        return
    
    site=context.getSite()
    addMimetype(site)
    addTransforms(site)

def addMimetype(site):
    mr_tool = getToolByName(site, 'mimetypes_registry')
    mr_tool.register(SubRipMimetype())

def addTransforms(site):
    if not pysrt:
        site.plone_log("Can't install srt_to_html transform: pysrt module not found")
        raise ImportError("Can't install srt_to_html transform: pysrt module not found")
    pt_tool = getToolByName(site, 'portal_transforms')
    pt_tool.registerTransform(SrtToHtml())
    site.plone_log("Installed srt_to_html transform")
