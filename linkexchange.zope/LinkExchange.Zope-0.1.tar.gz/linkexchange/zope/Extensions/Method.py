# LinkExchange.Zope - Zope integration with LinkExchange library
# Copyright (C) 2011 Konstantin Korikov
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

from linkexchange.zope import support as lx_support

def get_block(self, request, num):
    """
    Returns links block #num for specified request. Use this function as Zope
    External Method with following parameters:

        Id: LinkExchangeBlock
        Module Name: linkexchange.zope.Method
        Function Name: get_block

    Then you can use in in templates:

        <div tal:content="structure python: context.LinkExchangeBlock(request,0)"></div>
    """
    return lx_support.get_blocks(request)[num]

def get_links(self, request):
    """
    Returns raw links for specified request.
    """
    return lx_support.get_links(request)

def content_filter(self, request, content):
    """
    Filters content through clients content_filter().
    """
    return lx_support.content_filter(request, content)
