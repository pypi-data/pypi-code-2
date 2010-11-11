from logging import getLogger
from persistent import Persistent
from zope.interface import implements
from collective.gsa.interfaces import IGSAConnectionConfig

logger = getLogger('collective.gsa.utilities')


class GSAConnectionConfig(Persistent):
    """ utility to hold the connection configuration for the gsa server """
    implements(IGSAConnectionConfig)

    def __init__(self):
        self.active = None
        self.host = None
        self.port_index = 19900
        self.port_psearch = 80
        self.port_ssearch = 443
        self.only_public = None
        self.public_search = None
        self.secure_search = None
        self.source = 'site'
        self.site = 'default_collection'
        self.client = 'default_frontend'
        self.search_timeout = 0
        self.index_timeout = 0
        self.max_results = 100
        self.dual_site = None
        self.dual_collection = None
        self.advanced_search = None

    def getId(self):
        """ return a unique id to be used with GenericSetup """
        return 'gsa'
