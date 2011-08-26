#
# Copyright (C) 2010-2011 Platform Computing
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA
#
'''
An OCCI based negotiation service.

Created on Aug 26, 2011

@author: tmetsch
'''

from occi.backend import KindBackend
from occi.core_model import Kind, Resource


AGREEMENT = Kind('http://dgsi.d-grid.de/occi#', 'agreement',
                 related=[Resource.kind])


class AgreementHandler(KindBackend):
    '''
    Handles Agreement instances.
    '''

    agreements = {}

    def create(self, entity):
        self.agreements[entity.identifier] = entity

    def retrieve(self, entity):
        pass

    def update(self, old, new):
        raise AttributeError('Updates on agreements are not supported.')

    def replace(self, old, new):
        raise AttributeError('Full-updates on agreements are not supported.')

    def delete(self, entity):
        self.agreements.pop(entity.identifier)
