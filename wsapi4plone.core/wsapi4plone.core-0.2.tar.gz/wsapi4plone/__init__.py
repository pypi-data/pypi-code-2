# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

# from interfaces import IScrubber, IContextBuilder, IFormatQueryResults, IService, IServiceContainer, IServiceLookup
# from service import Service, ServiceContainer
# from services.plone_service import PloneService, PloneServiceContainer
# from services.archetype_service import ATFolderService, ATObjectService
