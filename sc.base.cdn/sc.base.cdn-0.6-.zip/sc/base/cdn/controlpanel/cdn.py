from zope import schema
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase

from zope.formlib.form import FormFields
from plone.app.controlpanel.form import ControlPanelForm

from sc.base.cdn import CDNMessageFactory as _


class ICDNSchema(Interface):

    enable_cdn = schema.Bool(
                          title=_(u'Use CDN'),
                          description=_(u'help_cdn_use',
                                      default=_(u"Should we use a CDN to delivery the resource registries content?"),
                          ),
                          default=False,
                          required=False,
    )
    enable_cdn_js = schema.Bool(
                          title=_(u'Use CDN for Portal Javascripts'),
                          description=_(u'help_cdn_use_js',
                                      default=_(u"Should we use a CDN to delivery the resource registries for portal_javascripts content?"),
                          ),
                          default=False,
                          required=False,
    )
    cdn_provider = schema.Choice(
                                title=_(u'CDN Provider'),
                                description=_(u'help_cdn_provider',
                                    default=_(u"A CDN Provider."),
                                ),
                                vocabulary='sc.base.cdn.Providers',
                                default= _(u'CoralCDN'),
                                required = False,
    )
    
    cdn_hostname = schema.List(
                                title=_(u'CDN Hostnames'),
                                description=_(u'help_cdn_hostname',
                                    default=_(u"Hostnames to be used on cdn mapping."),
                                ),
                                default= [],
                                value_type=schema.TextLine(),
                                required = False,
    )
    
    cdn_port = schema.Int(title=_(u'CDN Port'),
                                description=_(u'help_cdn_port',
                                    default=_(u"Port to be used on cdn mapping."),
                                ),
                                default=80,
                                required = False,
    )
    
    cdn_path = schema.TextLine(
                                title=_(u'CDN Path'),
                                description=_(u'help_cdn_path',
                                    default=_(u"Path."),
                                ),
                                default= _(u''),
                                required = False,
    )
class CDNControlPanelAdapter(SchemaAdapterBase):
    
    adapts(IPloneSiteRoot)
    implements(ICDNSchema)
    
    def __init__(self, context):
        super(CDNControlPanelAdapter, self).__init__(context)
        portal_properties = getToolByName(context, 'portal_properties')
        self.context = portal_properties.cdn_properties
    
    enable_cdn = ProxyFieldProperty(ICDNSchema['enable_cdn'])
    enable_cdn_js = ProxyFieldProperty(ICDNSchema['enable_cdn_js'])
    cdn_provider = ProxyFieldProperty(ICDNSchema['cdn_provider'])
    cdn_hostname = ProxyFieldProperty(ICDNSchema['cdn_hostname'])
    cdn_port = ProxyFieldProperty(ICDNSchema['cdn_port'])
    cdn_path = ProxyFieldProperty(ICDNSchema['cdn_path'])
    

class CDNControlPanel(ControlPanelForm):

    form_fields = FormFields(ICDNSchema)
    label = _('CDN Configuration')
    description = _('Define here if you will use a CDN.')
    form_name = _('CDN use settings')
