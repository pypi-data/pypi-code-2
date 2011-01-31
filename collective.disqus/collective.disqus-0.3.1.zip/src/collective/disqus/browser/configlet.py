from plone.app.controlpanel.form import ControlPanelForm
from zope.component import adapts
from zope.schema import TextLine, Bool
from zope.formlib.form import Fields
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, implements

from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

_ = MessageFactory('collective.disqus')


class IDisqusSettings(Interface):
    """
    Defines configurable options of collective.disqus.
    """
    forum_id = TextLine(
        title=_(u'Website short name'),
        description=_(u'This short name is used to uniquely identify your '
                        u'website on DISQUS.'),
        required=True)

    dev_mode = Bool(
        title=_(u'Developer mode'),
        description=_(u'Enables developer mode, which allows testing to be '
                        u'done on local, protected, or otherwise inaccessible '
                        u'servers. '),
        required=True)


class DisqusControlPanel(ControlPanelForm):
    """
    Configlet for collective.disqus.
    """
    form_fields = Fields(IDisqusSettings)
    label = _(u"DISQUS comment system")
    description = _(u'Allow to configure options required to integrate DISQUS '
                    u'comment system with Plone.')


class DisqusControlPanelAdapter(SchemaAdapterBase):
    """
    Store values of IDisqusConfiguration.
    """
    adapts(IPloneSiteRoot)
    implements(IDisqusSettings)

    forum_id = ProxyFieldProperty(IDisqusSettings['forum_id'])
    dev_mode = ProxyFieldProperty(IDisqusSettings['dev_mode'])
