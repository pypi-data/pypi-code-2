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


class Host(PoolElement):
    METHODS = {
        'info'     : 'host.info',
        'allocate' : 'host.allocate',
        'delete'   : 'host.delete',
        'enable'   : 'host.enable'
    }

    HOST_STATES = ['INIT', 'MONITORING', 'MONITORED', 'ERROR', 'DISABLED']

    SHORT_HOST_STATES = {
        'INIT'          : 'on',
        'MONITORING'    : 'on',
        'MONITORED'     : 'on',
        'ERROR'         : 'err',
        'DISABLED'      : 'off'
    }

    XML_TYPES = {
        'id'            : int,
        'name'          : str,
        'state'         : int,
        'im_mad'        : str,
        'vm_mad'        : str,
        'tm_mad'        : str,
        'last_mon_time' : int,
        'cluster'       : str,
        'host_share'    : ET.tostring,
        'template'      : ET.tostring,
    }

    @staticmethod
    def allocate(client, hostname, im, vmm, tm):
        '''
        Adds a host to the host list

        Arguments

        ``hostname``
           Hostname machine to add

        ``im``
           Information manager'

        ``vmm``
           Virtual machine manager.

        ``tm``
           Transfer manager
        '''
        host_id = client.call(Host.METHODS['allocate'], hostname, im, vmm, tm)
        return host_id

    def __init__(self, xml, client):
        super(Host, self).__init__(xml, client)
        self.element_name = 'HOST'
        self.id = self['ID'] if self['ID'] else None

    def enable(self):
        '''
        Enable this host
        '''
        self.client.call(self.METHODS['enable'], self.id, True)

    def disable(self):
        '''
        Disable this host.
        '''
        self.client.call(self.METHODS['enable'], self.id, False)

    @property
    def str_state(self):
        '''
        String representation of host state. One of 'INIT', 'MONITORING', 'MONITORED', 'ERROR', 'DISABLED'
        '''
        return self.HOST_STATES[int(self.state)]

    @property
    def short_state(self):
        '''
        Short string representation of host state. One of 'on', 'off', 'err'
        '''
        return self.SHORT_HOST_STATES[self.str_state]

    def __repr__(self):
        return '<oca.Host("%s")>' % self.name


class HostPool(Pool):
    METHODS = {
            'info' : 'hostpool.info',
    }

    def __init__(self, client):
        super(HostPool, self).__init__('HOST_POOL', 'HOST', client)

    def factory(self, xml):
        h = Host(xml, self.client)
        h.convert_types()
        return h

    def __repr__(self):
        return '<oca.HostPool()>'

