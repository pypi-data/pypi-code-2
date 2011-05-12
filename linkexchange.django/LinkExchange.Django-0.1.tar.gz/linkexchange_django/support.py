# LinkExchange.Django - Django integration with LinkExchange library
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

import os
import os.path
import urllib
import logging

from django.conf import settings
from django.contrib.sites.models import Site, RequestSite
from django.utils.encoding import iri_to_uri

from linkexchange.config import file_config, ConfigError
from linkexchange.utils import normalize_uri
from linkexchange.platform import Platform
from linkexchange.clients import PageRequest

log = logging.getLogger('linkexchange.django')

platform = None
formatters = None
options = None

def configure():
    def check_mod_dir(mod):
        if isinstance(mod, basestring):
            try:
                mod = __import__(mod, {}, {}, [''])
            except ImportError:
                return None
        fn = os.path.join(os.path.dirname(mod.__file__), 'linkexchange.cfg')
        if not os.path.exists(fn):
            return None
        return fn

    try:
        real_settings = __import__(os.environ['DJANGO_SETTINGS_MODULE'],
                {}, {}, [''])
    except KeyError:
        real_settings = None

    try:
        cfgfile = settings.LINKEXCHANGE_CONFIG
    except AttributeError:
        cfgfile = None
    if not cfgfile and real_settings:
        cfgfile = check_mod_dir(real_settings)
    if not cfgfile:
        cfgfile = check_mod_dir(settings.ROOT_URLCONF)

    if cfgfile:
        defaults = {}
        if isinstance(cfgfile, basestring):
            defaults['basedir'] = os.path.abspath(
                    os.path.dirname(cfgfile))
        elif real_settings:
            defaults['basedir'] = os.path.abspath(
                    os.path.dirname(real_settings.__file__))
        else:
            defaults['basedir'] = os.getcwd()
        try:
            if not file_config(globals(), cfgfile, defaults=defaults):
                log.error("Unable to read configuration file: %s", cfgfile)
        except ConfigError, e:
            log.error("Configuration error: %s", str(e))

    global platform
    global formatters
    global options

    try:
        platform = Platform(settings.LINKEXCHANGE_CLIENTS)
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

    request = PageRequest(
            host=options.get('host', current_site.domain),
            uri=normalize_uri(request_uri),
            cookies=request.COOKIES,
            remote_addr=request.META.get('REMOTE_ADDR', None),
            meta=request.META)
    return request

configure()
