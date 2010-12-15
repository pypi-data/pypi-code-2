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
from pool import Pool, PoolElement


class Cluster(PoolElement):
    METHODS = {
        'info'     : 'cluster.info',
        'allocate' : 'cluster.allocate',
        'delete'   : 'cluster.delete',
        'add'      : 'cluster.add',
        'remove'   : 'cluster.remove',
    }

    XML_TYPES = {
            'id'       : int,
            'name'     : str,
    }

    @staticmethod
    def allocate(client, name):
        '''
        Creates a new cluster in the pool.

        Arguments

        ``client``
           oca.Client object

        ``name``
           new cluster name
        '''
        cluster_id = client.call(Cluster.METHODS['allocate'], name)
        return cluster_id

    def __init__(self, xml, client):
        super(Cluster, self).__init__(xml, client)
        self.element_name = 'CLUSTER'
        self.id = self['ID'] if self['ID'] else None

    def add(self, host_id):
        '''
        Adds a host to a cluster.

        Arguments

        ``host_id``
           host id
        '''
        self.client.call(self.METHODS['add'], host_id, self.id)

    def remove(self, host_id):
        '''
        Removes a host from its cluster.

        Arguments

        ``host_id``
           host id
        '''
        self.client.call(self.METHODS['remove'], host_id)

    def __repr__(self):
        return '<oca.Cluster("%s")>' % self.name


class ClusterPool(Pool):
    METHODS = {
            'info' : 'clusterpool.info',
    }

    def __init__(self, client):
        super(ClusterPool, self).__init__('CLUSTER_POOL', 'CLUSTER', client)

    def factory(self, xml):
        c = Cluster(xml, self.client)
        c.convert_types()
        return c

    def __repr__(self):
        return '<oca.ClusterPool()>'

