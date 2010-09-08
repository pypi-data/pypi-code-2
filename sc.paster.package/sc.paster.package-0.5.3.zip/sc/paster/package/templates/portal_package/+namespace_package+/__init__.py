# See http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
try:
    __import__('pkg_resources').declare_namespace(__name__)
except ImportError:
    from pkgutil import extend_path
    __path__ = extend_path(__path__, __name__)

try:
    from zopeskel.localcommands.plone import *
    from zopeskel.localcommands.archetype import *

    ArchetypeSubTemplate.parent_templates.append('portal_package')
    PloneSubTemplate.parent_templates.append('portal_package')
except ImportError:
    pass
