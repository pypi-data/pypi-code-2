from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

from unweb.watermark.interfaces import IWatermarkSettings
from plone.z3cform import layout

class WatermarkControlPanelForm(RegistryEditForm):
    schema = IWatermarkSettings

WatermarkControlPanelView = layout.wrap_form(WatermarkControlPanelForm, ControlPanelFormWrapper)

