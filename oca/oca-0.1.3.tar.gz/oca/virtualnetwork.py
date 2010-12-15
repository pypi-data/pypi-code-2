# -*- coding: UTF-8 -*-
# -------------------------------------------------------------------------- #
# Copyright 2010, Łukasz Oleś                                                #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
#--------------------------------------------------------------------------- #
from pool import Pool, PoolElement, ET


class VirtualNetwork(PoolElement):
    METHODS = {
        'info'     : 'vn.info',
        'allocate' : 'vn.allocate',
        'delete'   : 'vn.delete',
        'publish'  : 'vn.publish',
    }

    XML_TYPES = {
            'id'       : int,
            'uid'      : int,
            'name'     : str,
            'type'     : int,
            'bridge'   : str,
            'public'   : bool,
            'template' : ET.tostring,
            'leases'   : ET.tostring,
    }

    @staticmethod
    def allocate(client, template):
        '''
        allocates a new virtual network in OpenNebula

        Arguments

        ``template``
           a string containing the template of the virtual network
        '''
        vn_id = client.call(VirtualNetwork.METHODS['allocate'], template)
        return vn_id

    def __init__(self, xml, client):
        super(VirtualNetwork, self).__init__(xml, client)
        self.element_name = 'VNET'
        self.id = self['ID'] if self['ID'] else None

    def publish(self):
        '''
        Publishes a virtual network.
        '''
        self.client.call(self.METHODS['publish'], True)

    def unpublish(self):
        '''
        Unpublishes a virtual network.
        '''
        self.client.call(self.METHODS['publish'], False)

    def __repr__(self):
        return '<oca.VirtualNetwork("%s")>' % self.name


class VirtualNetworkPool(Pool):
    METHODS = {
            'info' : 'vnpool.info',
    }

    def __init__(self, client):
        super(VirtualNetworkPool, self).__init__('VNET_POOL', 'VNET', client)

    def factory(self, xml):
        v = VirtualNetwork(xml, self.client)
        v.convert_types()
        return v

    def __repr__(self):
        return '<oca.VirtualNetworkPool()>'

