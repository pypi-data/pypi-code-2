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

import re
import Cookie
import os
import os.path
import logging

import linkexchange as lx
from linkexchange.utils import normalize_uri

log = logging.getLogger('linkexchange.MoinMoin')

def configure(config):
    def check_mod_dir(mod):
        try:
            mod = __import__(mod, {}, {}, [''])
        except ImportError:
            return None
        fn = os.path.join(os.path.dirname(mod.__file__), 'linkexchange.cfg')
        if not os.path.exists(fn):
            return None
        return fn

    try:
        cfg_fn = config.linkexchange_config
    except AttributeError:
        cfg_fn = None
    if not cfg_fn:
        cfg_fn = check_mod_dir('farmconfig')
    if not cfg_fn:
        cfg_fn = check_mod_dir('wikiconfig')

    vars = dict(
            linkexchange_options = {},
            linkexchange_platform = None)
    if cfg_fn:
        defaults = dict(
                basedir = os.path.abspath(os.path.dirname(cfg_fn)))
        try:
            if not lx.file_config(vars, cfg_fn,
                    defaults = defaults, prefix = 'linkexchange_'):
                log.error("Unable to read configuration file: %s", cfg_fn)
        except lx.ConfigError, e:
            log.error("Configuration error: %s", str(e))

    for k, v in vars.items():
        if k == 'linkexchange_options':
            config.__dict__.setdefault(k, {})
            for o, ov in v.items():
                config.linkexchange_options.setdefault(o, ov)
        else:
            config.__dict__.setdefault(k, v)
    try:
        config.linkexchange_platform = lx.Platform(config.linkexchange_clients)
    except AttributeError:
        pass

    if config.linkexchange_platform is None:
        log.warning("LinkExchange is not configured")

def convert_request(request):
    """
    Converts MoinMoin request object to linkexchange.PageRequest

    @param request: MoinMoin request object
    @return: linkexchange.PageRequest object
    """
    request = lx.PageRequest(
	    host = request.cfg.linkexchange_options.get(
                'host', request.http_host),
            uri = normalize_uri(request.request_uri),
            cookies = Cookie.SimpleCookie(request.saved_cookie),
            remote_addr = request.remote_addr)
    return request
