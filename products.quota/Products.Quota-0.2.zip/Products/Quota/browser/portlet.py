# -*- coding: utf-8 -*-
from Acquisition import aq_inner, aq_parent
from zope import schema
from zope.interface import implements
from zope.component import getUtility
from zope.formlib import form
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.Quota.interfaces import IQuotaAware, IQuotaService
from Products.Quota import QuotaMessageFactory as _
from Products.CMFPlone.CatalogTool import SIZE_ORDER, SIZE_CONST


class IQuotaPortlet(IPortletDataProvider):
    """A portlet displaying current quota"""

    public = schema.Bool(
        title=_(u"Display quota publically"),
        description=_(u"If disabled quota portlet will only be visible for "
                       "Managers and Owner of the container object."),

        )


class Assignment(base.Assignment):
    implements(IQuotaPortlet)

    title = u"Quota portlet"

    def __init__(self, public=False):
        self.public = public


class Renderer(base.Renderer):

    @property
    def available(self):
        if self.data.public:
            return True
        else:
            mtool = getToolByName(self.context, 'portal_membership')
            return mtool.checkPermission('Modify portal content',
                                  self._find_container(aq_inner(self.context)))

    def _find_container(self, context=None):
        assert context is not None

        if not IQuotaAware.providedBy(context):
            return self._find_container(aq_parent(context))

        return context

    def format(self, size):

        # if the size is a float, then make it an int
        # happens for large files
        try:
            size = long(size)
        except (ValueError, TypeError):
            pass

        # The code in Products.CMFPlone.CatalogTool for getObjSize is not
        # really reuseable, so i copied the lines below...
        smaller = SIZE_ORDER[-1]
        if isinstance(size, (int, long)):
            if size < SIZE_CONST[smaller]:
                return '1 %s' % smaller
            for c in SIZE_ORDER:
                if size/SIZE_CONST[c] > 0:
                    break
            return '%.1f %s' % (float(size/float(SIZE_CONST[c])), c)

        return size

    def update(self):
        container = self._find_container(aq_inner(self.context))
        sizer = getUtility(IQuotaService)

        self.quota = sizer.max_size(container)
        self.threshold = sizer.size_threshold(container)
        self.hard_limit = self.quota + self.threshold
        self.size = sizer.get_size(container)
        self.total = sizer.get_total(container)

        # Percentage usage for easier handling in page template
        self.percent_size = 100.0 / self.hard_limit * self.size
        self.percent_total = 100.0 / self.hard_limit * self.total
        self.percent_quota = 100.0 / self.hard_limit * self.quota

    render = ViewPageTemplateFile('portlet.pt')


class AddForm(base.AddForm):
    form_fields = form.Fields(IQuotaPortlet)
    label = _(u"Add Quota Portlet")

    def create(self, data):
        return Assignment(public=data.get('public', False))


class EditForm(base.EditForm):
    form_fields = form.Fields(IQuotaPortlet)
    label = _(u"Edit Quota Portlet")
