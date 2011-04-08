# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.salesforce.query import queryMessageFactory as _


class ISalesforceQueryView(Interface):
    """
    SalesforceQueryView view interface
    """

    def getHeaders():
        """
        get all fields from the given data type
        """

    def getEntries():
        """
        get all content for the given datatype
        """

    def test():
        """method that does the same as test on old page templates"""

_marker = object()
class SalesforceQueryView(BrowserView):
    """
    SalesforceQueryView browser view
    """
    implements(ISalesforceQueryView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def listing_mode(self,entries=_marker):
        if entries == _marker:
            entries = self.getEntries()
        return len(entries) != 1

    def getHeaders(self):
        """
        get all fields from the given data type
        """
        context = aq_inner(self.context)
        return context.getHeaders()

    def getEntries(self):
        """
        get all content for the given datatype
        """
        context = aq_inner(self.context)
        data = context.data().values()

        return data

    def get_member_unique_identifier(self):
        member = self._get_member()
        cid = member.getProperty('salesforce_unique_identifier', '') or ''
        cid.strip()
        return cid

    def update_allowed(self):
        member = self._get_member()
        return 'Manager' in member.getRoles()

    def _get_member(self):
        portal_membership = getToolByName(aq_inner(self.context), 'portal_membership')
        return portal_membership.getAuthenticatedMember()

    def test(self, condition, true_value, false_value):
        """
        method that does the same as test on old page templates
        """
        if condition:
            return true_value
        else:
            return false_value


class SalesforceDetailsView(SalesforceQueryView):

    details_raw_template = ViewPageTemplateFile('salesforce_details_raw.pt')

    def fields(self):
        context = aq_inner(self.context)
        item_id = self.request.get('item_id','')

        headers = context.getHeaders(details=True)
        all_data = context.data()

        item_data = all_data.get(item_id,None)

        if item_data is not None:
            item_data = [(field.label,item_data[k]) for k,field in headers]
        return item_data

    def item_details(self):
        return self.details_raw_template()

    def __call__(self,simple=False,item_id=None):
        self.request.set('disable_border', True)
        if simple:
            self.request.form['item_id'] = item_id
            return self.item_details()
        return super(SalesforceDetailsView,self).__call__()
