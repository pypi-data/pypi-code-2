import pkg_resources

from lxml import etree

class ResourceResolver(etree.Resolver):
    """Resolver for resource urls
    
    This can resolve resource://dotted.package.name/file/path URLs to paths.
    """
    
    def resolve(self, system_url, public_id, context):
        if system_url[:11] != 'resource://':
            return None
        spec = system_url[11:]
        try:
            package, resource_name = spec.split('/', 1)
        except ValueError:
            return None
        filename = pkg_resources.resource_filename(package, resource_name)
        return self.resolve_filename(filename, context)


class PythonResolver(etree.Resolver):
    """Resolver for python
    
    This can resolve python://dotted.package.name/file/path URLs to paths.
    And py://dotted.package.name:callable?cookie= entries.
    """
    
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    
    def resolve(self, system_url, public_id, context):
        if system_url[:9] != 'python://':
            return None
        spec = system_url[9:]

        if '/' in spec:
            package, resource_name = spec.split('/', 1)
            filename = pkg_resources.resource_filename(package, resource_name)
            return self.resolve_filename(filename, context)
        
        if ':' in spec:
            module_name, attrs = value.split(':', 1)
            attrs = attrs.split('.')
            ep = pkg_resouces.EntryPoint(None, module_name, attrs)
            entry = ep.load(require=False)
            result = entry(*self.args, **self.kwargs)                
            if isinstance(result, basestring):
                return self.resolve_string(result, context)
            if hasattr(result, 'read'):
                return self.resolve_file(result, context)
            if result is None:
                return self.resolve_empty(context)
            raise ValueError('Unknown result type (%r) from %s' % (result, system_url))
            