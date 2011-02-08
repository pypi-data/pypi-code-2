from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from plone.app.controlpanel.form import ControlPanelForm

from collective.alerts.interfaces import IAlertsConfiguration

_ = MessageFactory('plone')

class AlertsConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IAlertsConfiguration)

    form_name = _(u"Custom Alerts Control Panel")
    label = _(u"Configuration settings for Plone Custom Alerts")
    description = (u"Here you can configure various settings regarding the \
    custom Plone Alerts product (collective.alerts).")


