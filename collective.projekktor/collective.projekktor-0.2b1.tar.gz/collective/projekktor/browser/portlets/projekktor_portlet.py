
import os.path

from StringIO import StringIO
from time import localtime

from Acquisition import aq_parent, aq_inner

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress


from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from Acquisition import aq_inner
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName as _t
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PythonScripts.standard import url_quote_plus

from plone.app.portlets import cache
from plone.app.portlets.portlets import base

from plone.portlets.utils import hashPortletInfo

from zope.formlib import form

from zope.formlib import interfaces, namedtemplate
from zope.app.form.interfaces import IInputWidget, IDisplayWidget
from zope.app.form.interfaces import WidgetsError, MissingInputError
from zope.app.form.interfaces import InputErrors, WidgetInputError

from collective.projekktor.provider import ProjekktorProvider
from collective.projekktor.interfaces import IProjekktorMedia
from collective.projekktor.browser.interfaces import IProjekktorPortlet

AVARS = dict(filepath='.',alternativeFilepaths=[],mediaWidth="",mediaHeight="",mediaPoster="")

from collective.projekktor.interfaces import IProjekktorProvider

def _traverse(self,filepath):
    if filepath == '.': target = self.context        
    elif filepath.startswith('http://'): target = filepath
    elif filepath.startswith( '/' ):
        portal = self.context.portal_url.getPortalObject()            
        target =  portal.unrestrictedTraverse(str(filepath[1:]))
    else:
        target = self.context.unrestrictedTraverse(str(filepath))
    if not isinstance(target,str):
        mtool = self.context.portal_membership
        if not mtool.checkPermission( 'Access contents information', target ):
            return
    return target

class ProjekktorPortletProvider(ProjekktorProvider):
    implements(IProjekktorProvider)
    def __init__(self,context,portlet):
        self.context = context
        self.data = portlet.data
            
    @property
    def target(self):
        return _traverse(self,self.data.filepath)

    def getAlternativeFilepaths(self):
        paths = {}
        if self.data.alternativeFilepaths:
            for path in self.data.alternativeFilepaths:
                paths[os.path.basename(path)] = path
        
        return paths or self.projekktor.getAlternativeFilepaths()

    def getPoster(self):
        return self.data.mediaPoster or self.projekktor.getPoster()

    def getWidth(self):
        return self.data.mediaWidth or self.projekktor.getWidth()

    def getHeight(self):
        return self.data.mediaHeight or self.projekktor.getHeight()

class Assignment(base.Assignment):
    implements(IProjekktorPortlet)
    title = u'Projekktor portlet'
    def __init__(self
                 ,title=''
                 ,source=None
                 ,**kwa
                 ):
        self.portlet_title = title
        _kwa = AVARS.copy()
        if source:
            _kwa.update(source.getAssignmentData())
        _kwa.update(kwa)
        [setattr(self,k,_kwa[k])
         for k in AVARS.keys()]
        

class Renderer(base.Renderer):
    _template = ViewPageTemplateFile('projekktor_portlet.pt')
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.updated = False 
            
    @property
    def _target(self):
        return _traverse(self,self.data.filepath)

    def portletClass(self):
        pass

    def portletId(self):
        pass

    def showPortlet( self ):
        return True

    def getTitle( self ):
        target = self._target        
        if not isinstance(self._target,str):
            return IProjekktorMedia(target).getTitle()
        return target.split('/').pop()

    def getDescription( self ):
        target = self._target
        if not isinstance(self._target,str):
            return IProjekktorMedia(target).getDescription()
        return ''

    def render(self):
        return xhtml_compress(self._template())


class AddForm(base.AddForm):
    form_fields = form.Fields(IProjekktorPortlet)
    label = u"Add projekktor portlet"
    description = "An HTML5 media player portlet."

    def create(self, data):
        return Assignment(filepath=data.get('filepath')
                          ,alternativeFilepaths=data.get('alternativeFilepaths')
                          ,mediaPoster=data.get('mediaPoster')
                          ,mediaWidth=data.get('mediaWidth')
                          ,mediaHeight=data.get('mediaHeight'))



class EditForm(base.EditForm):
    form_fields = form.Fields(IProjekktorPortlet)
    label = u"Edit projekktor portlet"
    description = "An HTML5 media player portlet."


