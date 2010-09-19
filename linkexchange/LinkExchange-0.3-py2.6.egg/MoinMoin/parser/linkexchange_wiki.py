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
import logging

try:
    from MoinMoin.parser.text_moin_wiki import Parser as WikiParser
except ImportError:
    from MoinMoin.parser.wiki import Parser as WikiParser

from linkexchange.MoinMoin import support

log = logging.getLogger('linkexchange.MoinMoin')

Dependencies = ['time']

class Parser(WikiParser):
    """
    Parser to perform content filtering, e.g. calls platform.content_filter()
    on generated content.
    """

    Dependencies = Dependencies

    _fix_empty_span = re.compile(r'<span\b[^>]*></span>', re.S)

    def format(self, formatter):
        request = self.request

        try:
            platform = request.cfg.linkexchange_platform
        except AttributeError:
            support.configure(request.cfg)
            platform = request.cfg.linkexchange_platform

        if platform is None:
            return WikiParser.format(self, formatter)

        content = request.redirectedOutput(
                WikiParser.format, self, formatter)
        content = self._fix_empty_span.sub('', content)
        content = content.replace('<<<>>>', '<!--<<<>>>-->')
        try:
            content = platform.content_filter(
                    support.convert_request(request), content)
        except Exception, e:
            content += '<!-- Content filter error -->'
            log.error("Content filter error", exc_info = True)
        content = content.replace('<!--<<<>>>-->', '<<<>>>')
        request.write(content)
