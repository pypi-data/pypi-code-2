from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.content import DocumentActionsViewlet
from zope.component import getMultiAdapter 

import datetime

class DatumText(ViewletBase):
    index = ViewPageTemplateFile('viewlet.pt')
	
    def update(self):
        super(DatumText, self).update()
        self.DatumJetzt = datetime.date.today()