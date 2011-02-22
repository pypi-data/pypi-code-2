from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope.formlib import form

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from datetime import datetime

from wpd.mmxi.countdown import MessageFactory as _


class IWPDcountdown(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IWPDcountdown)

    @property
    def title(self):
        """
        """
        return _(u"WPD Countdown")

class AddForm(base.NullAddForm):
    """Portlet add form.
    """
    def create(self):
        return Assignment()

class Renderer(base.Renderer):
    """Portlet renderer.
    """
    
    day = datetime(2011, 4, 27)
    
    def days(self):
        now = datetime.now()
        today = datetime(now.year,now.month,now.day)
        return (self.day - today).days

    @property
    def isToday(self):
        return self.days()==0

    @property
    def isPast(self):
        return self.days()<0
    
    @property
    def isFuture(self):
        return self.days()>0
        

    render = ViewPageTemplateFile('wpdcountdown.pt')


