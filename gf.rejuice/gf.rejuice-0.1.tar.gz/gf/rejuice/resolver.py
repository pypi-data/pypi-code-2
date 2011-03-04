"""Resolver

This does the work of exploding the minified and concatenated resources
into separate development sources.
"""

from config import JuicerConfigParser
from config import listify_param
from config import get_ini_section
from config import get_filepath_path
import re
import os
from urlparse import urljoin

class Resolver(object):

    def __init__(self, base_urls, url_prefix, filepath, resources, sections=None):
        self.base_urls = base_urls
        assert not url_prefix.startswith('/') and not url_prefix.endswith('/')
        self.url_prefix = url_prefix
        self.filepath = filepath
        self.resources = resources
        self.sections = sections

    re_js_depends = re.compile(r'@depends\s+([^\s\*]+)')

    def _request_base_urls(self, request_base_url):
        if request_base_url is None:
            return self.base_urls
        assert request_base_url[-1] != '/'
        base_urls = list(self.base_urls)
        for i in range(len(base_urls)):
            if base_urls[i] is None:
                base_urls[i] = request_base_url
                if request_base_url.endswith(':80'):
                    # we accept it with or without the port
                    base_urls.append(request_base_url[:-3])
        return base_urls

    def _js_dependencies(self, devel_resource_path, devel_resource_url):
        devel_resource_dir = os.path.dirname(devel_resource_path)
        results = []
        for line in file(devel_resource_path):
            match = self.re_js_depends.search(line)
            if match:
                new_res = match.group(1)
                new_res_path = os.path.join(devel_resource_dir, new_res)
                new_res_url = urljoin(devel_resource_url, new_res)
                #print "MATCH", new_res_path, new_res_url
                results.extend(self._js_dependencies(new_res_path, new_res_url))
                results.append(new_res_url)
        return results

    def resolve_js(self, minified_resource, request_base_url=None):
        # Resolve only for js resources
        if not minified_resource.endswith('.js'):
            return [minified_resource]
        else:
            return self._resolve_one(minified_resource, 
                request_base_url=request_base_url, is_js=True)
     
    def resolve_css(self, minified_resource, request_base_url=None):
        # Resolve only for css resources
        if not minified_resource.endswith('.css'):
            return [minified_resource]
        else:
            return self._resolve_one(minified_resource,
                request_base_url=request_base_url, is_js=False)

    def _resolve_one(self, minified_resource, request_base_url, is_js):
        base_urls = self._request_base_urls(request_base_url)
        # Resolve only for selected domain prefixes
        for base_url in base_urls:
            prefix = base_url
            # avoid double // if prefix is empty
            if self.url_prefix:
                prefix += '/' + self.url_prefix
            if minified_resource.startswith(prefix):
                matching_prefix = prefix
                matching_base_url = base_url
                break
        else:
            return [minified_resource]
        assert not matching_base_url.endswith('/') and not matching_prefix.endswith('/')
        # find the urls to replace
        for res2, res1_list in self.resources.items():
            full_res2 = urljoin(matching_prefix + '/', res2, True)
            if minified_resource == full_res2:
                devel_resources = res1_list
                break
        else:
            return [minified_resource]
        # We now have a resource.
        devel_resource_urls = []
        for devel_resource in devel_resources:
            devel_resource_name, extend_inifile, extend_section = devel_resource
            if extend_inifile is not None:
                assert extend_section is not None
                resolver = self.sections[(extend_inifile, extend_section)]
            else:
                assert extend_section is None
                resolver = self
            add_url_prefix = resolver.url_prefix
            # avoid double // if prefix is empty
            if add_url_prefix:
                add_url_prefix += '/'
            devel_resource_url = urljoin(matching_base_url + '/' + add_url_prefix, devel_resource_name, True)
            # is this a produced resource in the resolver?
            if devel_resource_name in resolver.resources:
                # if yes, we need to resolve it recursively
                more_urls = resolver.resolve_css(devel_resource_url, request_base_url=request_base_url)
                devel_resource_urls.extend(more_urls)
            else:
                # if no, then we just produce the development resource
                if is_js:
                    # only for js: need to resolve @depends lines from the source
                    devel_resource_path = os.path.join(resolver.filepath, devel_resource_name)
                    new_resources = self._js_dependencies(devel_resource_path, devel_resource_url)
                    devel_resource_urls.extend(new_resources)
                devel_resource_urls.append(devel_resource_url)
        return devel_resource_urls

class ResolverList(list):

    def __init__(self, base_urls, JuicerConfigParser=JuicerConfigParser, Resolver=Resolver, *arg, **kw):
        self.base_urls = base_urls
        self.Parser = JuicerConfigParser
        self.Resolver = Resolver
        self.sections = {}
        list.__init__(self, *arg, **kw)

    def resolve_js(self, minified_resource, request_base_url=None):
        for resolver in self:
            devel_resource_url_list = resolver.resolve_js(minified_resource, request_base_url=request_base_url)
            devel_resource_url = devel_resource_url_list[-1]
            dependencies = devel_resource_url_list[:-1]
            if devel_resource_url or dependencies:
                return devel_resource_url_list
            else:
                return [minified_resource]

    def resolve_css(self, minified_resource, request_base_url=None):
        for resolver in self:
            devel_resource_url_list = resolver.resolve_css(minified_resource, request_base_url=request_base_url)
            devel_resource_url = devel_resource_url_list[0]
            if devel_resource_url:
                return devel_resource_url_list


    def add_new_section(self, inifile, section_name, allow_filter_section_keys=False):
        """Add a new section identified by `inifile` and `section_name`,
        and any extensions defined from it.
        The dictionary in `defaults` will be used as defaults.
        """
        config_parser = self.Parser(inifile)
        config_parser.load()
        config = config_parser.get_section(section_name)
        self.add_current_section(config, inifile, section_name, allow_filter_section_keys)

    def add_current_section(self, config, inifile, section_name, allow_filter_section_keys=False):
        """Add the section, and any extensions defined from it.

        `config`        contains the configuration.
        `section_name`  is used only for displaying errors, and 
                        is None when we process the initial 
                        middleware section.
        `inifile`       is only used for traversing base to the next extension
                        (in case extent_resources is present)

        This is called directly when we set up the middleware, since
        by then we already have the configuration loaded.
        """
        # Check recursive conf 
        if (inifile, section_name) in self.sections.keys():
            return 
        #else:
        #    self.sections.update({(inifile, section_name): True})

        # get some info for displaying errors
        if section_name is None:
            error_info = ''
        else:
            error_info = '(inifile: "%s", section: [%s])' % (inifile, section_name)
        # Check for mandatory parameters
        url_prefix = config.get('url_prefix', None)
        filepath = config.get('filepath', None)

        resources = {}
        resource_keys = []
        for config_param in config:
            if (config_param.endswith('.css') or config_param.endswith('.js')):
                new_resource = []
                resource_list = listify_param(config.get(config_param))
                for resource in resource_list:
                    resource = resource.split(' ')
                    if len(resource) > 1:
                        new_inifile, new_section = get_ini_section(inifile, resource[1])
                    else:
                        new_inifile, new_section = None, None
                    new_resource.append([resource[0], new_inifile, new_section])
                resources[config_param] = new_resource
                resource_keys.append(config_param)
        extend_resources = config.get('extend_resources', None)
        if url_prefix is None:
            raise ValueError('Must configure url_prefix (`url_prefix`). %s' % (error_info, ))
        ##if not resources and extend_resources is None:
        ##    raise ValueError('Must configure either the resources or an extension section (`min_resource = devel_resource` or `extend_resources`). %s' % (error_info, ))
        if filepath is None:
            raise ValueError('Must configure file path (`filepath`). %s' % (error_info, ))
        if url_prefix[0] == '/':
            url_prefix = url_prefix[1:]
        # check for excess resources
        allowed_keys =  set(['url_prefix', 'filepath', 'extend_resources'] + resource_keys)
        if allow_filter_section_keys:
            allowed_keys.add('base_urls')
            allowed_keys.add('use')
        keyset = set(config.keys())
        if not allowed_keys.issuperset(keyset):
            raise ValueError('Excess keys in the configuration: %s %s' % (
                keyset.difference(allowed_keys), error_info))
        # Add this section
        filepath = get_filepath_path(inifile, filepath)
        r = self.Resolver(self.base_urls, url_prefix, filepath, resources, self.sections)
        self.append(r)
        self.sections.update({(inifile, section_name): r})
        # Add extended sections
        #print resources
        if extend_resources is not None:
            extend_resources = listify_param(extend_resources)
            for extension in extend_resources:
                new_inifile, new_section_name = get_ini_section(inifile, extension, error_info)
                self.add_new_section(new_inifile, new_section_name)
        
