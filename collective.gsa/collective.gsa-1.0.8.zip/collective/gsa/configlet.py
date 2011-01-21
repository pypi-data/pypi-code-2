from zope.component import adapts, queryUtility
from zope.formlib.form import FormFields
from zope.interface import implements
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.form import ControlPanelForm

from collective.gsa import GSAMessageFactory as _
from collective.gsa.interfaces import IGSASchema
from collective.gsa.interfaces import IGSAConnectionConfig


class GSAControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IGSASchema)

    @apply
    def active():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'active', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.active = value 
        return property(get, set)

    @apply
    def host():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'host', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.host = value 
        return property(get, set)

    @apply
    def port_index():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'port_index', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.port_index = value 
        return property(get, set)

    @apply
    def port_psearch():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'port_psearch', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.port_psearch = value 
        return property(get, set)

    @apply
    def only_public():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'only_public', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.only_public = value 
        return property(get, set)


    @apply
    def port_ssearch():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'port_ssearch', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.port_ssearch = value 
        return property(get, set)

    @apply
    def public_search():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'public_search', False)
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.public_search = value 
        return property(get, set)

    @apply
    def secure_search():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'secure_search', False)
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.secure_search = value 
        return property(get, set)

    @apply
    def site():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'site', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.site = value 
        return property(get, set)

    @apply
    def source():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'source', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.source = value 
        return property(get, set)

    @apply
    def client():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'client', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.client = value 
        return property(get, set)

    @apply
    def search_timeout():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'search_timeout', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.search_timeout = value 
        return property(get, set)

    @apply
    def index_timeout():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'index_timeout', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.index_timeout = value 
        return property(get, set)

    @apply
    def max_results():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'max_results', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.max_results = value 
        return property(get, set)

    @apply
    def dual_site():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'dual_site', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.dual_site = value 
        return property(get, set)

    @apply
    def dual_collection():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'dual_collection', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.dual_collection = value 
        return property(get, set)

    @apply
    def advanced_search():
        def get(self):
            util = queryUtility(IGSAConnectionConfig)
            return getattr(util, 'advanced_search', '')
        def set(self, value):
            util = queryUtility(IGSAConnectionConfig)
            if util is not None:
                util.advanced_search = value 
        return property(get, set)
        

class GSAControlPanel(ControlPanelForm):

    form_fields = FormFields(IGSASchema)

    label = _('GSA settings')
    description = _('Settings to enable and configure GSA integration for Plone.')
    form_name = _('GSA settings')