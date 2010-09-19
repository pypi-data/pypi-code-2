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

import os
import os.path
import urllib
import logging

from django.conf import settings
from django.contrib.sites.models import Site, RequestSite
from django.utils.encoding import iri_to_uri

import linkexchange as lx
from linkexchange.utils import normalize_uri

log = logging.getLogger('linkexchange.django')

platform = None
formatters = None
options = None

def configure():
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
        cfg_fn = settings.LINKEXCHANGE_CONFIG
    except AttributeError:
        cfg_fn = None
    if not cfg_fn:
        try:
            cfg_fn = check_mod_dir(os.environ['DJANGO_SETTINGS_MODULE'])
        except KeyError:
            pass
    if not cfg_fn:
        cfg_fn = check_mod_dir(settings.ROOT_URLCONF)

    if cfg_fn:
        defaults = dict(
                basedir = os.path.abspath(os.path.dirname(cfg_fn)))
        try:
            if not lx.file_config(globals(), cfg_fn, defaults = defaults):
                log.error("Unable to read configuration file: %s", cfg_fn)
        except lx.ConfigError, e:
            log.error("Configuration error: %s", str(e))

    global platform
    global formatters
    global options

    try:
        platform = lx.Platform(settings.LINKEXCHANGE_CLIENTS)
    except AttributeError:
        pass
    try:
        formatters = settings.LINKEXCHANGE_FORMATTERS
    except AttributeError:
        pass
    if options is None:
        options = {}
    try:
        options.update(settings.LINKEXCHANGE_OPTIONS)
    except AttributeError:
        pass

    if platform is None:
        log.warning("LinkExchange is not configured")

def convert_request(request):
    if Site._meta.installed:
        current_site = Site.objects.get_current()
    else:
        current_site = RequestSite(request)

    path = request.path
    if type(path) == unicode:
        path = path.encode('utf-8')
    query_string = iri_to_uri(request.environ.get('QUERY_STRING', ''))
    request_uri = urllib.quote(path) + (query_string and
            ('?' + query_string) or '')

    request = lx.PageRequest(
            host = options.get('host', current_site.domain),
            uri = normalize_uri(request_uri),
            cookies = request.COOKIES,
            remote_addr = request.META.get('REMOTE_ADDR', None))
    return request

configure()
