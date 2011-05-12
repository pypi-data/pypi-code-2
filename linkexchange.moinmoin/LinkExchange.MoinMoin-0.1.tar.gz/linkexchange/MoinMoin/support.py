# LinkExchange.MoinMoin - MoinMoin integration with LinkExchange library
# Copyright (C) 2009, 2011 Konstantin Korikov
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
import urllib
import logging

import MoinMoin.version

from linkexchange.utils import normalize_uri
from linkexchange.config import file_config, ConfigError
from linkexchange.platform import Platform
from linkexchange.clients import PageRequest

log = logging.getLogger('linkexchange.MoinMoin')

moin_version = tuple([int(x) for x in MoinMoin.version.release.split('.')])

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
            if not file_config(vars, cfg_fn,
                    defaults = defaults, prefix = 'linkexchange_'):
                log.error("Unable to read configuration file: %s", cfg_fn)
        except ConfigError, e:
            log.error("Configuration error: %s", str(e))

    for k, v in vars.items():
        if k == 'linkexchange_options':
            config.__dict__.setdefault(k, {})
            for o, ov in v.items():
                config.linkexchange_options.setdefault(o, ov)
        else:
            config.__dict__.setdefault(k, v)
    try:
        config.linkexchange_platform = Platform(config.linkexchange_clients)
    except AttributeError:
        pass

    if config.linkexchange_platform is None:
        log.warning("LinkExchange is not configured")

def convert_request(request):
    """
    Converts MoinMoin request object to linkexchange.clients.PageRequest

    @param request: MoinMoin request object
    @return: linkexchange.clients.PageRequest object
    """
    if moin_version < (1, 9):
        host = request.http_host
        uri = request.request_uri
        cookies = Cookie.SimpleCookie(request.saved_cookie)
        try:
            meta = request.env
        except AttributeError:
            meta = {}
    else:
        host = request.host
        uri = urllib.quote(request.path.encode('utf-8'), '/')
        if request.query_string:
            uri += '?' + request.query_string
        cookies = request.cookies
        meta = request.environ
    request = PageRequest(
	    host=request.cfg.linkexchange_options.get('host', host),
            uri=normalize_uri(uri), cookies=cookies,
            remote_addr=request.remote_addr, meta=meta)
    return request
