################################################################
# vs.org (C) 2011, Veit Schiele
################################################################

# $Id: employeefolder.py 2981 2011-03-16 10:54:12Z carsten $

"""
Define a browser view for the Employeefolder content type. In the FTI
configured in profiles/default/types/Employeefolder.xml, this is being set as
the default view of that content type.
"""

from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.memoize.instance import memoize

class EmployeefolderView(BrowserView):
    """Default view of an employeefolder """

    __call__ = ViewPageTemplateFile('employeefolder_view.pt')
