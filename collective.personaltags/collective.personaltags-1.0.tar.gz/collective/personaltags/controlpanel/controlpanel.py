
"""
This is intended to be the controlpanel editor for the site.

For personal tags, we should be able to configure:

    The content on which it is available
    Which storage we use
    The view to use to display the results

Based on:
    http://plone.org/documentation/kb/how-to-create-a-plone-control-panel-with-plone.app.registry
"""

from plone.app.registry.browser import controlpanel

from ..interfaces import IPersonalTagsSettings

class EditForm(controlpanel.RegistryEditForm):

    schema = IPersonalTagsSettings
    label = u"Personal Tags settings"
    description = u""""""

    def updateFields(self):
        super(EditForm, self).updateFields()

    def updateWidgets(self):
        super(EditForm, self).updateWidgets()

class PersonalTagsSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = EditForm
