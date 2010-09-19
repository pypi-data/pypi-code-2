# LinkExchange - Universal link exchange service client
# Copyright (C) 2009 Konstantin Korikov
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

import os.path
import urllib
import logging

try:
    import kid
except ImportError:
    kid = None

from turbogears import config
from cherrypy import request
import linkexchange as lx
from linkexchange.utils import rearrange_blocks, parse_rearrange_map
from linkexchange.utils import normalize_uri

log = logging.getLogger('linkexchange.turbogears')

configured = False
platform = None
formatters = None
options = None

def configure():
    def check_mod_dir(mod, parent = False):
        try:
            mod = __import__(mod, {}, {}, [''])
        except (ImportError, ValueError):
            return None
        dir = os.path.dirname(mod.__file__)
        if parent:
            dir = os.path.dirname(dir)
        fn = os.path.join(dir, 'linkexchange.cfg')
        if not os.path.exists(fn):
            return None
        return fn

    cfg_fn = config.get('linkexchange.config', None)
    if not cfg_fn:
        cfg_fn = check_mod_dir(config.get('package', ''), True)

    if cfg_fn:
        defaults = dict(
                basedir = os.path.abspath(os.path.dirname(cfg_fn)))
        try:
            if not lx.file_config(globals(), cfg_fn, defaults = defaults):
                log.error("Unable to read configuration file: %s", cfg_fn)
        except lx.ConfigError, e:
            log.error("Configuration error: %s", str(e))
    else:
        log.warning("No configuration file found")

    global configured
    configured = True

def convert_request(request):
    """
    Converts cherrypy.request object to linkexchange.PageRequest object.
    """
    try:
        script_name = request.script_name
    except AttributeError:
        script_name = ''
    try:
        path = request.original_path
    except AttributeError:
        path = request.path_info
    try:
        cookies = request.cookie
    except AttributeError:
        cookies = request.simple_cookie
    try:
        remote_addr = request.remote.ip
    except AttributeError:
        remote_addr = request.remote_host

    request_uri = script_name + path
    if type(request_uri) == unicode:
        request_uri = request_uri.encode('utf-8')
    request_uri = urllib.quote(request_uri)
    if request.query_string:
        request_uri += '?' + request.query_string

    request = lx.PageRequest(
            host = options.get('host', request.headers['Host']),
            uri = normalize_uri(request_uri),
            cookies = cookies, remote_addr = remote_addr)
    return request

def content_filter(content):
    if not configured:
        configure()

    if platform is None:
        return content

    as_kid_xml = False
    if kid is not None:
        if isinstance(content, kid.ElementStream):
            content = content.expand()
        if hasattr(content, 'tag') and hasattr(content, 'attrib'):
            content = [content]
        if type(content) == list:
            as_kid_xml = True
            orig_content = content
            s = kid.XMLSerializer(
                    namespaces = {'http://www.w3.org/1999/xhtml': ''})
            def serialize(item):
                if isinstance(item, basestring):
                    return s.escape_cdata(item)
                return unicode(s.serialize(kid.ElementStream(item),
                    encoding = 'utf-8', fragment = True), 'utf-8')
            content = u''.join(map(serialize, content))

    content = platform.content_filter(convert_request(request), content)

    if as_kid_xml:
        try:
            content = kid.XML(content).expand()
        except Exception, e:
            log.error("Error parsing XML", exc_info = True)
            return orig_content

    return content

def add_stdvars(varss):
    def as_kid_xml(value):
        try:
            return kid.XML(value).expand()
        except Exception, e:
            log.error("Error parsing XML", exc_info = True)
            return kid.XML('<!-- Error parsing XML -->')

    if not configured:
        configure()

    if platform is None:
        return

    lx_request = convert_request(request)
    vars = {}

    if formatters:
        vars['linkexchange_blocks'] = platform.get_blocks(
                lx_request, formatters)
        try:
            rearrange_map = parse_rearrange_map(options['rearrange_map'])
        except KeyError:
            pass
        except ValueError:
            log.warning("Unable to parse rearrange_map")
        else:
            vars['linkexchange_blocks'] = rearrange_blocks(lx_request,
                    vars['linkexchange_blocks'], rearrange_map)
        if options.get('as_kid_xml', False):
            vars['linkexchange_blocks'] = map(as_kid_xml,
                    vars['linkexchange_blocks'])

    if options.get('use_raw_links', False):
        vars['linkexchange_links'] = platform.get_raw_links(
                lx_request)
        if options.get('as_kid_xml', False):
            vars['linkexchange_links'] = map(as_kid_xml,
                    vars['linkexchange_links'])

    vars['linkexchange_filter'] = content_filter
    return varss.update(vars)
