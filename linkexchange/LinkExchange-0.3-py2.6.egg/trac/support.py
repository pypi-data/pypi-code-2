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
import logging

import linkexchange as lx
from linkexchange.utils import normalize_uri

log = logging.getLogger('linkexchange.trac')

def configure(component):
    config = component.config
    env = component.env

    lx_log = logging.getLogger('linkexchange')
    try:
        lx_log._trac_handler
    except AttributeError:
        try:
            log_hdl = env.log._trac_handler
        except AttributeError:
            pass
        else:
            lx_log.addHandler(log_hdl)
            lx_log._trac_handler = log_hdl
            lx_log.setLevel(env.log.getEffectiveLevel())

    cfg_fn = config.getpath('linkexchange', 'config', None)
    if not cfg_fn:
        cfg_fn = os.path.join(env.path, 'conf', 'linkexchange.cfg')
        if not os.path.exists(cfg_fn):
            cfg_fn = None
    component.lx_platform = None
    component.lx_formatters = None
    component.lx_options = {}
    if cfg_fn:
        defaults = dict(
                basedir = os.path.abspath(os.path.dirname(cfg_fn)),
                envdir = os.path.abspath(env.path))
        try:
            if not lx.file_config(component.__dict__, cfg_fn,
                    defaults = defaults, prefix = 'lx_'):
                log.error("Unable to read configuration file: %s", cfg_fn)
        except lx.ConfigError, e:
            log.error("Configuration error: %s", str(e))
    else:
        log.warning("No configuration file found")

def convert_request(request, options):
    request_uri = request.href(request.path_info)
    query_string = request.query_string
    if not query_string.startswith('?'):
        query_string = '?' + query_string
    request_uri += query_string
    request = lx.PageRequest(
            host = options.get('host', request.environ.get('HTTP_HOST', '')),
            uri = normalize_uri(request_uri),
            cookies = request.incookie,
            remote_addr = request.remote_addr)
    return request
