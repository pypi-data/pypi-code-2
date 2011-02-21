from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, PersonalBarViewlet
from Products.CMFCore.utils import getToolByName

from collective.fsdsimplifier.browser.interfaces import IFsdSimplifierLayer

class FSDPersonalBarViewlet(PersonalBarViewlet):

   layer = IFsdSimplifierLayer

   def update(self):
       super(FSDPersonalBarViewlet, self).update()
       
       fsdtool = getToolByName(self.context, 'facultystaffdirectory_tool')
       if not self.anonymous and fsdtool.fsdShowMyFolder():
           self.homelink_url = fsdtool.fsdMyFolder()
