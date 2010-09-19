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

from linkexchange.django import support
from linkexchange.utils import rearrange_blocks, parse_rearrange_map

def linkexchange(request):
    if support.platform is None:
        return {}

    page_request = support.convert_request(request)
    result = {}

    if support.formatters:
        result['linkexchange_blocks'] = support.platform.get_blocks(
                page_request, support.formatters)
        try:
            rearrange_map = parse_rearrange_map(support.options['rearrange_map'])
        except KeyError:
            pass
        except ValueError:
            log.warning("Unable to parse rearrange_map")
        else:
            result['linkexchange_blocks'] = rearrange_blocks(page_request,
                    result['linkexchange_blocks'], rearrange_map)

    if support.options.get('use_raw_links', False):
        result['linkexchange_links'] = support.platform.get_raw_links(
                page_request)

    return result
