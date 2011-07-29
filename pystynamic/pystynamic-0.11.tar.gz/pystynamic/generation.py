import os
import imp
import codecs
import logging

logger = logging.getLogger('pystynamic')

from pystynamic.exceptions import (
    ResourceNotFound,
    TooManyTemplatesFound, 
    CircularDependency,
)
from mako.template import Template
from mako.lookup import TemplateLookup

def _get_python_attributes(python_filename):
    """
    Imports a python module and grabs the attributes
    that do not start with an underscore.
    """
    results = {}
    module = imp.load_source(python_filename, python_filename)
    for attribute in [x for x in dir(module) if not x.startswith('_')]:
        value = getattr(module, attribute)
        results[attribute] = value

    return results
    
class Context(object):
    def __init__(self, **args):
        self.__dict__.update(args)

class ContextFromDirectorySource(object):
    SPECIAL_ATTRIBUTES = ['initialize']

    def __init__(self, source_path):
        self.source_path = source_path

    def _find_files(self):
        """
        Gets a list of absolute paths to non-ignored files in the resource's directory 
        """
        if not os.path.exists(self.source_path):
            return {}
        else:
            filenames = filter(lambda x: not x.startswith('_'), os.listdir(self.source_path))
            return map(lambda x: os.path.join(self.source_path, x), filenames)
        
    def __call__(self, site, context):
        filenames = self._find_files()
        # TODO: Split out handling of the file extensions into outside object.
        python_filenames = [x for x in filenames if os.path.splitext(x)[-1] == '.py']
        other_filenames = [x for x in filenames if os.path.splitext(x)[-1] not in ['.py', '.pyc']]

        special_attributes = dict( [(x, None) for x in self.SPECIAL_ATTRIBUTES] )

        for python_filename in python_filenames:
            # load_source needs a module name that is unique for each of the files,
            # otherwise one will simply "overwrite" another with their additional
            # attributes. To make sure they are unique, I'll just use the full path
            # name as the first argument (module name).
            # http://stackoverflow.com/questions/6802986/creating-anonymous-modules-in-python
            attributes = _get_python_attributes(python_filename)
            for attribute, value in attributes.items():
                if attribute in special_attributes:
                    special_attributes[attribute] = value
                else:
                    setattr(context, attribute, value)
                    
        for other_filename in other_filenames:
            attribute_name = os.path.splitext(os.path.basename(other_filename))[0]
            data = codecs.open(other_filename, encoding='utf-8').read()
            setattr(context, attribute_name, data)
        initialize_func = special_attributes.get('initialize', None)
        if initialize_func:
            initialize_func(site)


class Site(object):
    def __init__(self, resource_path):
        self.resources = {}
        self.initialize_stack = []

        self._resource_path = resource_path

    def add_resource(self, uri, template_filename, source=None):
        # Use the uri as the source (handy for when the uri is '/about',
        # and the source directory is '/about'.
        if source == None:
            source = uri

        # If the source is a none or string-like type, then the caller is using
        # the shorthand for a directory.
        if type(source) == str or type(source) == unicode:
            source_path = os.path.join(self._resource_path, source[1:])
            source = ContextFromDirectorySource(source_path)

        self.resources[uri] = Resource(uri, template_filename, source)

    def add_resource_group(self, uri, template_filename, source=None):
        # Note that we're sort of assuming that "source" will be a string-type here.
        if not source:
            source = uri

        source = os.path.join(self._resource_path, source[1:])
        sub_directories = [x for x in os.listdir(source) if os.path.isdir(os.path.join(source, x))]
        for sub_directory in sub_directories:
            resource_uri = uri.format(sub_directory)
            resource_source_path = os.path.join(source, sub_directory)
            resource_source = ContextFromDirectorySource(resource_source_path)
            self.add_resource(resource_uri, template_filename, resource_source)

    def __contains__(self, path_name):
        return path_name in self.resources

    def _initialize_if_necessary(self, resource):
        if resource.is_initialized:
            return

        if resource.uri in self.initialize_stack:
            raise CircularDependency(self.initialize_stack)

        self.initialize_stack.append(resource.uri)
        logger.debug('Initializing resource "{0}"'.format(resource.uri))
        resource.initialize(self)
        self.initialize_stack.pop()

    def __getitem__(self, path_name):
        """
        Find a resource by an exact path.
        """
        resource = self.resources[path_name]
        self._initialize_if_necessary(resource)

        return resource

    @property
    def names(self):
        """
        Returns an iterable of strings containing the names of any resources known.
        """
        for resource_name in self.resources.keys():
            yield resource_name 

    def find_resources(self, func):
        """
        Returns a list of context object of all resources whose path matches
        the test function `func`.
        """
        results = []
        for key, value in self.resources.items():
            if func(key):
                self._initialize_if_necessary(value)
                results.append(value.context)

        return results

class SiteGenerator(object):
    @staticmethod
    def build_for_path(root_path):
        generator = SiteGenerator(root_path)
        generator.initialize()
        return generator

    def __init__(self, root_path):
        self.root_path = root_path
        self.resource_path = os.path.join(self.root_path, 'resources')
        self.template_path = os.path.join(self.root_path, 'templates')
        self.template_lookup = TemplateLookup(directories=[self.template_path])

    def initialize(self):
        self._generate_resource_list()
        self._generate_global_context()

    def _generate_resource_list(self):
        site_filename = os.path.join(self.root_path, 'site.py')
        attributes = _get_python_attributes(site_filename)

        initialize_func = attributes['initialize']

        self.site = Site(self.resource_path)
        initialize_func(self.site)

    def _generate_global_context(self):
        global_filename = os.path.join(self.root_path, 'global.py')
        self.global_context = Context()
        if os.path.exists(global_filename):
            for attribute, value in _get_python_attributes(global_filename).items():
                setattr(self.global_context, attribute, value)
            
    def generate_resource(self, resource_name):
        logger.debug('Generating resource "{0}"'.format(resource_name))
        if resource_name not in self.site:
            raise ResourceNotFound(resource_name) 

        resource = self.site[resource_name]
        return resource.render(self.global_context, self.template_lookup)

    def generate_all(self):
        """
        Returns an iterator of (filename, unicode) tuples of the site.
        """
        for resource_name in self.site.names:
            result = self.generate_resource(resource_name)
            yield resource_name, result


class Resource(object):
    def __init__(self, uri, template_filename, source):
        self.uri = uri

        self._template_filename = template_filename
        self._source = source

    @property
    def is_initialized(self):
        return hasattr(self, 'context')

    def initialize(self, site):
        """
        Gathers information such as context and template name about the resource.
        After, the context attribute can be used if needed for another resources, or the
        template can be rendered using the "render" function.
        """
        self.context = Context(uri=self.uri)

        self._source(site, self.context)

    def render(self, global_context, template_lookup):
        if not self.is_initialized:
            raise ResourceNotInitialized(self)

        logger.debug('Rendering "{0}"'.format(self.uri))

        template = template_lookup.get_template(self._template_filename)
        return template.render(c=self.context, g=global_context)

