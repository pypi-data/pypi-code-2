from zope.interface import implements
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone import PloneMessageFactory as _

class IAboutmePortlet(IPortletDataProvider):
    """To initalized & provide a interface

    """


class Assignment(base.Assignment):
    implements(IAboutmePortlet)

    @property
    def title(self):
        return "About me"

class Renderer(base.Renderer):
    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)

        self.membership = getToolByName(self.context, 'portal_membership')

        self.context_state = getMultiAdapter((context, request), name=u'plone_context_state')
        self.portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.pas_info = getMultiAdapter((context, request), name=u'pas_info')

   
    @property
    def Aboutme(self):
        site_description=self.portal_state.portal().Description()
        if site_description is not None:
              return site_description
        else :
	      return 'Please add a site Description!'

    def update(self):
        pass

    render = ViewPageTemplateFile('Aboutme.pt')




class AddForm(base.NullAddForm):
    def create(self):
        return Assignment()


