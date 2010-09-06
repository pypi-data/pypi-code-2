import os
import pkg_resources

from zope.interface import implements
from zope.interface import Interface

from mako.lookup import TemplateLookup

from repoze.bfg.interfaces import ITemplateRenderer

from repoze.bfg.exceptions import ConfigurationError
from repoze.bfg.threadlocal import get_current_registry
from repoze.bfg.settings import get_settings

class IMakoLookup(Interface):
    pass

def renderer_factory(path):
    registry = get_current_registry()
    lookup = registry.queryUtility(IMakoLookup)
    if lookup is None:
        settings = get_settings() or {}
        reload_templates = settings.get('reload_templates', False)
        directories = settings.get('mako.directories')
        input_encoding = settings.get('mako.input_encoding', 'utf-8')
        if directories is None:
            raise ConfigurationError(
                'Mako template used without a lookup path')
        directories = directories.splitlines()
        directories = [ abspath_from_resource_spec(d) for d in directories ]
        lookup = TemplateLookup(directories=directories,
                                input_encoding=input_encoding,
                                filesystem_checks=reload_templates)
        registry.registerUtility(lookup, IMakoLookup)
    _, path = resolve_resource_spec(path)
    return MakoLookupTemplateRenderer(path, lookup)

class MakoLookupTemplateRenderer(object):
    implements(ITemplateRenderer)
    def __init__(self, path, lookup):
        self.path = path
        self.lookup = lookup
 
    def implementation(self):
        return self.template

    @property
    def template(self):
        return self.lookup.get_template(self.path)
   
    def __call__(self, value, system):
        context = system.pop('context', None)
        if context is not None:
            system['_context'] = context
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        template = self.template
        result = template.render_unicode(**system)
        return result

def resolve_resource_spec(spec, pname='__main__'):
    if os.path.isabs(spec):
        return None, spec
    filename = spec
    if ':' in spec:
        pname, filename = spec.split(':', 1)
    elif pname is None:
        pname, filename = None, spec
    return pname, filename

def abspath_from_resource_spec(spec, pname='__main__'):
    if pname is None:
        return spec
    pname, filename = resolve_resource_spec(spec, pname)
    if pname is None:
        return filename
    return pkg_resources.resource_filename(pname, filename)
