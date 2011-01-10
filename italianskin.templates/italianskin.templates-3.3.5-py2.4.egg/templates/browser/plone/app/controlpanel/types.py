
from plone.app.controlpanel.types import TypesControlPanel as CustomTypesControlPanel

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class TypesControlPanel(CustomTypesControlPanel):

    template = ViewPageTemplateFile('types.pt')