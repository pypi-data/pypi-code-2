# encoding: utf-8

'''
Created on 2010/09/24

@author: nagai
'''
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFCore.interfaces import ISiteRoot
from plone.app.controlpanel.form import ControlPanelForm
from ngi.theme.simple.interfaces import IPrefForm
from ngi.theme.simple.config import LOGO_NAME
from ngi.theme.simple import _

class PrefHeaderFooterFormAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IPrefForm)

    def __init__(self, context):
        super(PrefHeaderFooterFormAdapter, self).__init__(context)

    def get_picture(self):
#        portal =  getUtility(ISiteRoot)
#        if hasattr(portal, LOGO_NAME):
#            obj = portal.restrictedTraverse(LOGO_NAME)
#            return obj.getField('image').get(obj)
#        return None
        registry = getUtility(IRegistry)
        if 'ngi.theme.simple.logo' in registry:
            return registry['ngi.theme.simple.logo']
        else:
            return _(u'Please set the logo file.')


        
    def set_picture(self, value):
        portal =  getUtility(ISiteRoot)
        if hasattr(portal, LOGO_NAME):
            obj = portal.restrictedTraverse(LOGO_NAME)
        else:
            name = portal.invokeFactory('Image', id = LOGO_NAME, title = LOGO_NAME)
            obj = portal[name]
        if value:
            obj.getField('image').set(obj, value)
        obj.getField('excludeFromNav').set(obj, True)
        obj.reindexObject()

        registry = getUtility(IRegistry)
        registry['ngi.theme.simple.logo'] = value


    picture = property(get_picture,
                                  set_picture)

    def get_footer_text(self):
        registry = getUtility(IRegistry)
        if 'ngi.theme.simple.footer' in registry:
            return registry['ngi.theme.simple.footer']
        else:
            return _(u'Please input footer text.')

    def set_footer_text(self, value):
        registry = getUtility(IRegistry)
        registry['ngi.theme.simple.footer'] = value

    footer_text = property(get_footer_text,
                                  set_footer_text)


class PrefHeaderFooterForm(ControlPanelForm):
    """"""
    label = _("Simple theme settings")
    description = _("Logo & Footer settings for this site.")
    form_name = _("Logo & Footer settings")
    form_fields = form.FormFields(IPrefForm)
    
