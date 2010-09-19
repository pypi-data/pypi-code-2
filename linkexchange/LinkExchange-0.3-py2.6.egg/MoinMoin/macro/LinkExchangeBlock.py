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

import logging

from linkexchange.MoinMoin import support
from linkexchange.utils import rearrange_blocks, parse_rearrange_map

log = logging.getLogger('linkexchange.MoinMoin')

Dependencies = ['time']

def execute(macro, num):
    request = macro.request
    cfg = request.cfg

    try:
	num = int(num)
    except (TypeError, ValueError):
        log.error("LinkExchangeBlock requires a single numeric argument")
	return "Required single numeric argument!"

    try:
        platform = cfg.linkexchange_platform
    except AttributeError:
        support.configure(cfg)
        platform = cfg.linkexchange_platform

    if platform is None:
	return ""

    formatters = getattr(cfg, 'linkexchange_formatters', None)
    if not formatters:
        log.error("No formatters defined for LinkExchangeBlock")
	return "No formatters defined!"

    try:
	return request.linkexchange_blocks[num]
    except AttributeError:
	pass

    page_request = support.convert_request(request)
    request.linkexchange_blocks = platform.get_blocks(
            page_request, formatters)
    try:
        rearrange_map = parse_rearrange_map(
                cfg.linkexchange_options['rearrange_map'])
    except KeyError:
        pass
    except ValueError:
        log.warning("Unable to parse rearrange_map")
    else:
        request.linkexchange_blocks = rearrange_blocks(page_request,
                request.linkexchange_blocks, rearrange_map)
    
    return request.linkexchange_blocks[num]
