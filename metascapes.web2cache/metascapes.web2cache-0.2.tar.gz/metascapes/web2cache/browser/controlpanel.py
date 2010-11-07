# -*- coding: utf-8 -*-
#
# File: controlpanel.py
#
# Copyright (c) 2010 by Bernhard Snizek <bs@metascapes.org>
#
# GNU General Public License (GPL)
#

__author__ = """Bernhard <unknown>"""
__docformat__ = 'plaintext'

from zope.interface import implements
from metascapes.web2cache.interfaces import IMetascapesWeb2ControlPanelForm
from metascapes.web2cache.interfaces.utility import IWeb2Flickr, IWeb2Delicious, \
                                                    IWeb2Wordpress, IWeb2Twitter, \
                                                    IWeb2Facebook, IWeb2Slideshare, IWeb2Vimeo
from zope.i18nmessageid import MessageFactory
from plone.app.controlpanel.form import ControlPanelForm
from plone.fieldsets.fieldsets import FormFieldsets

_ = MessageFactory('metascapes.web2cache')

class MetascapesWeb2CacheControlPanelForm( ControlPanelForm ):
    """The configlet in the control panel
    """
    implements(IMetascapesWeb2ControlPanelForm)
    
    flickr = FormFieldsets(IWeb2Flickr)
    flickr.id = 'flickr'
    flickr.label = _(u'FLICKR')
    
    delicious = FormFieldsets(IWeb2Delicious)
    delicious.id = "delicious"
    delicious.label = _(u"delicious")

    wordpress = FormFieldsets(IWeb2Wordpress)
    wordpress.id = "wordpress"
    wordpress.label = _(u"Wordpress")

    twitter = FormFieldsets(IWeb2Twitter)
    twitter.id = "twitter"
    twitter.label = _(u"Twitter")
    
    facebook = FormFieldsets(IWeb2Facebook)
    facebook.id = "facebook"
    facebook.label = _(u"Facebook")

    slideshare = FormFieldsets(IWeb2Slideshare)
    slideshare.id = "slideshare"
    slideshare.label = _(u"Slideshare")
    
    vimeo = FormFieldsets(IWeb2Vimeo)
    vimeo.id = "vimeo"
    vimeo.label = _(u"Vimeo")
    
    form_fields = FormFieldsets(facebook, flickr, delicious, wordpress, twitter, slideshare, vimeo)

    label = _(u"Web 2.0 Cache Settings")
    description = _(u"Settings for the Web 2.0 Cache")
    form_name = "web2cache"