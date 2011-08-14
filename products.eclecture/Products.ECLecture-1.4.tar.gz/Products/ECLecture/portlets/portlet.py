# -*- coding: utf-8 -*-
# $Id: portlet.py 1542 2011-04-01 07:13:53Z amelung $
#
# Copyright (c) 2006-2011 Otto-von-Guericke-UniversitŠt Magdeburg
#
# This file is part of ECLecture.
#
__author__ = """Mario Amelung <mario.amelung@gmx.de>"""
__docformat__ = 'plaintext'

#from Acquisition import aq_inner

from zope.component import getMultiAdapter#, ComponentLookupError
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.memoize.view import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.ECLecture import ECMessageFactory as _

class IECLecturePortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    pass


class Assignment(base.Assignment):
    """
    Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IECLecturePortlet)

    def __init__(self):
        pass

    @property
    def title(self):
        """
        This property is used to give the title of the portlet in the
        'manage portlets' screen.
        """
        return _(u"Today's Lectures")


class Renderer(base.Renderer):
    """
    Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('portlet.pt')

    def __init__(self, *args):
        """
        """
        base.Renderer.__init__(self, *args)
        
        tools = getMultiAdapter((self.context, self.request),
                                name=u'plone_tools')

        self.catalog = tools.catalog()

        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')

        self.portal = portal_state.portal()
        self.portal_url = portal_state.portal_url()

    @property
    def available(self):
        """
        Determine if the portlet is available at all.
        """
        if self.brains():
            return True

    @memoize
    def brains(self):
        """
        """
        return self.catalog.searchResults(
                                portal_type='ECLecture',
                                end={'query':self.context.ZopeTime(), 'range':'min'},
                                sort_on='getTimePeriod',
                                review_state='published')

    @memoize
    def lectures(self):
        """
        """
        lectureObjects = map(lambda (item): item.getObject(), self.brains());
        
        return filter(lambda (item): item.lectureTakesPlace(), lectureObjects)[:5]



class AddForm(base.NullAddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    def create(self):
        return Assignment()
