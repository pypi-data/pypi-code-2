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

import sys
import logging
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site

import linkexchange
from linkexchange.utils import configure_logger
configure_logger()
from linkexchange.django import support

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
            make_option('--host', '-d', dest = 'host',
                help = 'Request host.'),
            make_option('--uri', '-i', dest = 'uri',
                help = 'Request URI.'),
            )
    help = "Force to refresh LinkExchange clients databases."

    def handle(self, *args, **options):
        logger = logging.getLogger('linkexchange')
        log_level = min(50, max(10,
            10 + 20 * (2 - int(options.get('verbosity', 1)))))
        logger.setLevel(log_level)

        uri = options.get('uri', '/')
        host = options.get('host', support.options.get('host', None))

        if support.platform is None:
            sys.stderr.write(self.style.ERROR("No platform defined\n"))
            sys.exit(1)

        if host is None:
            if Site._meta.installed:
                current_site = Site.objects.get_current()
                if current_site is not None:
                    host = current_site.domain
            if host is None:
                sys.stderr.write(self.style.ERROR("No host configured\n"))
                sys.exit(1)

        page_request = linkexchange.PageRequest(host = host, uri = uri)
        support.platform.refresh_db(page_request)

