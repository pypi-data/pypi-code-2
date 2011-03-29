'''CKAN Extension Data Preview - preview package resources.

Data Preview is a CKAN extension - http://ckan.org/wiki/Extensions.

Enable by adding to your ckan.plugins line in the CKAN config::

  ckan.plugins = datapreview

Optional configuration options::

    ## a data proxy URL
    ## Default proxy URL is http://jsonpdataproxy.appspot.com
    ckanext.dataapi.data_proxy_url = http://...
    
This extension provides preview functionality (using javascript) in relation to
Packge Resources (i.e. urls pointing to datasets).
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
<div id="ckanext-datapreview-dialog"></div>
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.8/jquery-ui.min.js"></script>
<script type="text/javascript" src="/ckanext/datapreview/data-preview.js"></script>
<script type="text/javascript">
  jQuery('document').ready(function($) {
    var dataproxyUrl = '%(data_proxy_url)s';
    var dataproxyDialogId = 'ckanext-datapreview-dialog';
    CKANEXT.DATAPREVIEW.initialize(dataproxyUrl, dataproxyDialogId);
  });
</script>
"""
    
    HEAD_CODE = '''
<link rel="stylesheet"
    href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.7.2/themes/ui-lightness/jquery-ui.css"
    type="text/css" media="screen, print" />
<style type="text/css">
a.resource-preview-button {
  float: right;
  padding-right: 2px;
  padding-left: 2px;
  border-top: #d7d7d7 1px solid;
  border-left: #d7d7d7 1px solid;
  border-bottom: #666 1px solid;
  border-right: #666 1px solid;
}
</style>
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

