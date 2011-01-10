
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.form import named_template_adapter

_template = ViewPageTemplateFile('control-panel.pt')
controlpanel_named_template_adapter = named_template_adapter(_template)
