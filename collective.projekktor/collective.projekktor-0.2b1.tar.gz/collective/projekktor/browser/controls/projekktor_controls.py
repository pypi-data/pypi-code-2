
from zope.interface import implements
from zope.i18nmessageid import MessageFactory
from plone.fieldsets.fieldsets import FormFieldsets
from plone.app.controlpanel.form import ControlPanelForm

from collective.projekktor.interfaces import IProjekktorVideoConfig
from collective.projekktor.interfaces import IProjekktorAudioConfig

from collective.projekktor.browser.interfaces import IProjekktorControlPanelForm

_ = MessageFactory('collective.projekktor')

class ProjekktorControlPanelForm(ControlPanelForm):
    """Projekktor Control Panel Form"""
    implements(IProjekktorControlPanelForm)

    projekktorvideoconfig = FormFieldsets(IProjekktorVideoConfig)
    projekktorvideoconfig.id = 'projekktorvideoconfig'
    projekktorvideoconfig.label = _(u'Video')

    projekktoraudioconfig = FormFieldsets(IProjekktorAudioConfig)
    projekktoraudioconfig.id = 'projekktoraudioconfig'
    projekktoraudioconfig.label = _(u'Audio')

    form_fields = FormFieldsets(projekktorvideoconfig,projekktoraudioconfig)
    label = _(u"Projekktor Settings")
    description = _(u"Settings for the Projekktor HTML5 media player")
    form_name = _("Projekktor Settings")

