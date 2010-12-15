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


class User(PoolElement):
    METHODS = {
        'info'     : 'user.info',
        'allocate' : 'user.allocate',
        'delete'   : 'user.delete',
        'passwd'   : 'user.passwd',
    }

    XML_TYPES = {
            'id'       : int,
            'name'     : str,
            'password' : str,
            'enabled'  : bool,
    }

    @staticmethod
    def allocate(client, user, password):
        '''
        allocates a new user in OpenNebula

        Arguments

        ``user``
           username for the new user

        ``password``
           password for the new user
        '''
        user_id = client.call(User.METHODS['allocate'], user, password)
        return user_id

    def __init__(self, xml, client):
        super(User, self).__init__(xml, client)
        self.element_name = 'USER'
        self.id = self['ID'] if self['ID'] else None

    def change_passwd(self, new_password):
        '''
        Changes the password for the given user.

        Arguments

        ``new_password``
           The new password
        '''
        self.client.call(User.METHODS['passwd'], self.id, new_password)

    def __repr__(self):
        return '<oca.User("%s")>' % self.name


class UserPool(Pool):
    METHODS = {
            'info' : 'userpool.info',
    }

    def __init__(self, client):
        super(UserPool, self).__init__('USER_POOL', 'POOL', client)

    def factory(self, xml):
        u = User(xml, self.client)
        u.convert_types()
        return u

    def __repr__(self):
        return '<oca.UserPool()>'

