'''CKAN Extension Data API - preview and access package resources through data transformation proxy service.

Data API is a CKAN extension - http://ckan.org/wiki/Extensions.

Enable by adding to your ckan.plugins line in the CKAN config::

  ckan.plugins = dataapi datapreview

Optional configuration options::

    ## a data proxy URL
    ## Default proxy URL is http://jsonpdataproxy.appspot.com
    ckanext.dataapi.data_proxy_url = http://...
    
This extension provides two distinct sets of functionality in relation to Packge Resources (i.e. urls pointing to datasets):

  1. Provision of a new API: /api/data
  2. Data preview functionality for package resources (using javascript)

Both items depend on the existence of a data proxy service as a way to access data in a standard json format.
'''
__version__ = '0.1'
# this is a namespace package
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)

import os
import urllib
import urlparse
from logging import getLogger

from pylons import config
from pylons.decorators import jsonify
from genshi.input import HTML
from genshi.filters import Transformer

import ckan.model as model
from ckan.plugins import implements, SingletonPlugin, IConfigurable
from ckan.plugins import IGenshiStreamFilter, IRoutes, IConfigurer
from ckan.lib.base import BaseController, c, g, request, response, session

log = getLogger(__name__)

default_data_proxy_url = 'http://jsonpdataproxy.appspot.com'


class DataPreviewPlugin(SingletonPlugin):
    """Insert javascript fragments into package pages to allow users to preview
    a package resource."""
    
    implements(IConfigurable)
    implements(IGenshiStreamFilter)
    implements(IConfigurer, inherit=True)
    
    def configure(self, config):
        """Called upon CKAN setup, will pass current configuration dict to the
        plugin to read custom options.
        """
        self.data_proxy_url = config.get('ckanext.dataapi.data_proxy_url',
                default_data_proxy_url)

    def update_config(self, config):
        here = os.path.dirname(__file__)
        rootdir = os.path.dirname(os.path.dirname(here))
        our_public_dir = os.path.join(rootdir, 'public')
        config['extra_public_paths'] = ','.join([our_public_dir,
                config.get('extra_public_paths', '')])

    BOTTOM_CODE = """
<div id="ckanext-dataapi-data-preview-dialog"></div>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.8/jquery-ui.min.js"></script>
<script type="text/javascript">
var dataproxy = '%(data_proxy_url)s';
var dataproxyDialogId = 'ckanext-dataapi-data-preview-dialog';
</script>
<script type="text/javascript" src="/ckanext/dataapi/data-preview.js"></script>
"""
    
    HEAD_CODE = '''
<link rel="stylesheet"
    href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/themes/ui-lightness/jquery-ui.css"
    type="text/css" media="screen, print" />
'''
        
    def filter(self, stream):
        """Required to implement IGenshiStreamFilter; will apply some HTML
        transformations to the page currently rendered.
        """
        
        from pylons import request, tmpl_context as c 
        routes = request.environ.get('pylons.routes_dict')
        
        if routes.get('controller') == 'package' and \
            routes.get('action') == 'read' and c.pkg.id:
            data = {
                'data_proxy_url': self.data_proxy_url,
                }
            stream = stream | Transformer('body')\
                .append(HTML(self.BOTTOM_CODE % data))
            stream = stream | Transformer('head')\
                .append(HTML(self.HEAD_CODE))
        
        return stream


class DataAPIPlugin(SingletonPlugin):
    '''Data API plugin.
    '''
    implements(IRoutes, inherit=True)

    def before_map(self, map):
        map.connect('dataapi', '/api/data',
            controller='ckanext.dataapi:DataAPIController',
            action='index')
        map.connect('dataapi_resource', '/api/data/{id}',
            controller='ckanext.dataapi:DataAPIController',
            action='resource')
        return map


class DataAPIController(BaseController):
    @jsonify
    def index(self):
        return {
            'doc': __doc__,
            'doc_url': 'http://ckan.org/wiki/Extensions'
            }

    @jsonify
    def resource(self, id):
        proxy_url = config.get('ckanext.dataapi.data_proxy_url',
                default_data_proxy_url)

        if id == None:
            response.status_int = 400
            return {'error': "No resource reference specified"}

        res = self._get_resource(id)
        if res == None:
            response.status_int = 404
            return {'error': 'CKAN package resource not found'}

        resource_url = res.url
        if resource_url != None:
            proxy_params = request.params.copy()
            proxy_params["url"] = resource_url
            redirect_url =  '%s?%s' % (proxy_url, urllib.urlencode(proxy_params))

            response.status_int = 302
            response.headers['Location'] = redirect_url
            return "Redirected to %s" % redirect_url
                
    def _get_resource(self, id):
        '''Returns a package object referenced by its id or name.'''
        query = model.Session.query(model.PackageResource).filter(model.PackageResource.id==id)
        return query.first()
        
