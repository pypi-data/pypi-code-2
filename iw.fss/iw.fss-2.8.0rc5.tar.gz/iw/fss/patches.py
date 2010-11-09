# -*- coding: utf-8 -*-
# Copyright (C)2010 Alterway Solutions

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

from Products.Archetypes.utils import contentDispositionHeader
from ZPublisher.Iterators import IStreamIterator
from Products.Archetypes.Field import FileField
from Acquisition import aq_get

from iw.fss.utils import objectImplements

old_download =  FileField.download

def new_download(self, instance, REQUEST=None, RESPONSE=None,
                 no_output=False):
    """Patch download for return an iterator instead of a string
    """

    file = self.get(instance, raw=True)
    if not REQUEST:
        REQUEST = aq_get(instance, 'REQUEST')
    if not RESPONSE:
        RESPONSE = REQUEST.RESPONSE
    RESPONSE = REQUEST.RESPONSE
    if no_output:
        if objectImplements(IStreamIterator, file):
            RESPONSE.setHeader("content-length", len(file))
    return old_download(self, instance, REQUEST, RESPONSE,
                        no_output)

