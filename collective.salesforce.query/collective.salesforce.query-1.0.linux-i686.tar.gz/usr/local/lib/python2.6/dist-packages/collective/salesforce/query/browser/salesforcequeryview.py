# -*- coding: utf-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

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

class SalesforceQueryView(BrowserView):
    """
    SalesforceQueryView browser view
    """
    implements(ISalesforceQueryView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        

    @property
    def salesforce_tool(self):
        return getToolByName(self.context, 'portal_salesforcebaseconnector')
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def getHeaders(self):
        """
        get all fields from the given data type
        """
        result = self.salesforce_tool.describeSObjects([self.context.datatype,])[0]
        fields = result.__dict__['fields'].keys()
        return fields

    def getEntries(self, headers):
        """
        get all content for the given datatype
        """
        results = self.salesforce_tool.query(headers,self.context.datatype)
        return results['records']


    def test(self, condition, true_value, false_value):
        """
        method that does the same as test on old page templates
        """

        if condition:
            return true_value
        else:
            return false_value
