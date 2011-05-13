# LinkExchange.Zope - Zope integration with LinkExchange library
# Copyright (C) 2011 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import os
import os.path
import urllib
import Cookie
import logging

from linkexchange.utils import normalize_uri
from linkexchange.utils import rearrange_blocks, parse_rearrange_map
from linkexchange.config import file_config, ConfigError
from linkexchange.clients import PageRequest

log = logging.getLogger('linkexchange.zope')

platform = None
formatters = None
options = None

def configure():
    """
    Configures the module: reads linkexchange.cfg file and setups platform,
    formatters and options.
    """
    try:
        cfg_fn = os.environ['LINKEXCHANGE_CONFIG']
    except KeyError:
        cfg_fn = os.path.join(os.getcwd(), 'linkexchange.cfg')
        if not os.path.exists(cfg_fn):
            cfg_fn = None

    if cfg_fn:
        defaults = dict(
                basedir=os.path.abspath(os.path.dirname(cfg_fn)))
        try:
            if not file_config(globals(), cfg_fn, defaults=defaults):
                log.error("Unable to read configuration file: %s", cfg_fn)
        except ConfigError, e:
            log.error("Configuration error: %s", str(e))

    global platform
    global formatters
    global options

    if options is None:
        options = {}

    if platform is None:
        log.warning("LinkExchange is not configured")

def convert_request(request):
    """
    Converts Zope Request object to LinkExchange PageRequest object.
    """
    host = request['HTTP_HOST']
    path = request['PATH_INFO']
    if type(path) == unicode:
        path = path.encode('utf-8')
    path_list = path.split('/')
    del path_list[1:1+int(options.get('remove_path_components', '0'))]
    query_string = request['QUERY_STRING']
    request_uri = urllib.quote('/'.join(path_list)) + (query_string and
            ('?' + query_string) or '')

    cookies = Cookie.SimpleCookie(
            request.get_header('HTTP_COOKIE', ''))

    request = PageRequest(
            host=options.get('host', host),
            uri=normalize_uri(request_uri), cookies=cookies,
            remote_addr=request.get_header('REMOTE_ADDR', None),
            meta=request)
    return request

def get_blocks(request):
    """
    Returns links blocks for request.
    """
    if platform is None:
        return []
    if formatters is None:
        log.warning("No formatters defined")
        return []

    if request.has_key('LINKEXCHANGE_BLOCKS'):
        return request['LINKEXCHANGE_BLOCKS']

    lx_request = convert_request(request)

    blocks = platform.get_blocks(lx_request, formatters)
    try:
        rearrange_map = parse_rearrange_map(options['rearrange_map'])
    except KeyError:
        pass
    except ValueError:
        log.warning("Unable to parse rearrange_map")
    else:
        blocks = rearrange_blocks(lx_request, blocks, rearrange_map)

    request.set('LINKEXCHANGE_BLOCKS', blocks)
    return blocks

def get_links(request):
    """
    Returns raw links for request.
    """
    if platform is None:
        return []

    if request.has_key('LINKEXCHANGE_LINKS'):
        return request['LINKEXCHANGE_LINKS']

    lx_request = convert_request(request)

    links = platform.get_raw_links(lx_request)
    request.set('LINKEXCHANGE_LINKS', links)
    return links

def content_filter(request, content):
    """
    Filters content through clients content_filter().
    """
    if platform is None:
        return content

    lx_request = convert_request(request)
    return platform.content_filter(lx_request, content)

configure()
