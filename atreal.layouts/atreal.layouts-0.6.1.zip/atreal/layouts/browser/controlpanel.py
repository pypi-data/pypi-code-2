from zope.interface import Interface
from zope.component import adapts
from zope.interface import implements
from zope.schema import SourceText, TextLine, Choice, Bool, List, Text
from zope.formlib import form

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from atreal.layouts import atRealLayoutsMessageFactory as _
from plone.app.controlpanel.form import ControlPanelForm


class IatRealLayoutsSchema(Interface):

    atreallayouts_restricted_access_anonurls = Text(
        title=_(u'label_atreallayouts_restricted_access_anonurls',
                default=u"Anonym URLs"),
        description=_(u"help_atreallayouts_restricted_access_anonurls",
                      default=u"One by line"),
        default=u'mail_password\npasswordreset\npwreset\naccessibility-info\ncontact-info\nsitemap',
        required=True)


class atRealLayoutsControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IatRealLayoutsSchema)

    def __init__(self, context):
        super(atRealLayoutsControlPanelAdapter, self).__init__(context)

    atreallayouts_restricted_access_anonurls = ProxyFieldProperty(IatRealLayoutsSchema['atreallayouts_restricted_access_anonurls'])


class atRealLayoutsControlPanel(ControlPanelForm):
    form_fields = form.FormFields(IatRealLayoutsSchema)
    label = _("atRealLayouts settings")
    description = _("atRealLayouts settings for this site. Global settings for the package, may be useless for the profile you use.")
    form_name = _("atRealLayouts settings")
