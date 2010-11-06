# -*- coding: utf-8 -*-
# Copyright © 2010 Ryan Senkbeil
# 
# This file is part of repoze.what.plugins.mongodb.
#
#    repoze.what.plugins.mongodb is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    repoze.what.plugins.mongodb is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with repoze.what.plugins.mongodb.  If not, see <http://www.gnu.org/licenses/>.
"""Provides repoze.what plugins for MongoDB.

For more information, visit the `BitBucket page`_.

.. _BitBucket page: https://bitbucket.org/rsenk330/repoze.what.plugins.mongodb

"""
from repoze.what.adapters import BaseSourceAdapter

__version__ = '0.1.1'
__author__ = 'Ryan Senkbeil <rsenk330@gmail.com'
__license__ = 'GPL v3'

class MongoBaseSourceAdapter(BaseSourceAdapter):
    """Base source adapter for MongoDB."""
    def __init__(self, db):
        self._db = db
        
        self._translations = {}
        
    @property
    def translations(self):
        """Gets the database translations.
        
        :returns: A dictionary containing the database translations.
        
        """
        return self._translations
        
    @translations.setter
    def translations(self, translations):
        """Sets the database translations.
        
        This should be a dictionary and can contain the following keys:
        
        * ``username``: The field containing the user's username. Default: `username`.
        * ``usergroups``: The field containing the groups of an individual user. Default: `groups`.
        * ``grouppermissions``: The field containing the permissions of an individual group. Default: `permissions`.
        * ``permissionsname``: The field containing the permission names. Default: `name`.
        * ``groupsname``: The field containing the group names. Default: `name`.
        * ``groupdoc``: The document containing the groups. Default: `auth.groups`.
        * ``permissiondoc``: The document containing the permissions. Default: `auth.permissions`.
        * ``userdoc``: The document containing the users. Default: `auth.users`.
        
        :param dict translations: The database translations dictionary.
        
        """
        self._translations = translations
        
    def _username(self):
        """Gets the User's 'username' field name."""
        return self._translations.get('username', 'username')
        
    def _usergroups(self):
        """Gets the User's 'groups' field name."""
        return self._translations.get('usergroups', 'groups')
        
    def _grouppermissions(self):
        """Gets the Group's 'permissions' field name."""
        return self._translations.get('grouppermissions', 'permissions')
        
    def _permissionname(self):
        """Gets the Permission's 'name' field name."""
        return self._translations.get('permissionname', 'name')
        
    def _groupsname(self):
        """Gets the Group's 'name' field name."""
        return self._translations.get('groupsname', 'name')
        
    def _groupdoc(self):
        """Gets the Group Document name."""
        return self._translations.get('groupdoc', 'auth.groups')
        
    def _permissiondoc(self):
        """Gets the Permission Document name."""
        return self._translations.get('permissiondoc', 'auth.permissions')
        
    def _userdoc(self):
        """Gets the User Document name."""
        return self._translations.get('userdoc', 'auth.users')

class MongoGroupAdapter(MongoBaseSourceAdapter):
    """Group adapter for MongoDB."""
    def _get_section_items(self, section):
        """Gets a list of permissions in the group specified by `section`."""
        group = self._db[self._groupdoc()].find_one({self._groupsname(): section})
        
        if group:
            return [document[self._permissionname()] for document in group.get(self._grouppermissions(), [])]
        else:
            return []

    def _find_sections(self, hint):
        """Gets a list of groups that the user specified by `hint` belongs to."""
        user = self._db[self._userdoc()].find_one({self._username(): hint['repoze.what.userid']})
        
        if user:
            return [document[self._groupsname()] for document in user.get(self._usergroups(), [])]
        else:
            return []

    def _get_all_sections(self):
        raise NotImplementedError()
        
    def _include_items(self, section, items):
        raise NotImplementedError()

    def _item_is_included(self, section, item):
        raise NotImplementedError()

    def _section_exists(self, section):
        raise NotImplementedError()

class MongoPermissionAdapter(MongoBaseSourceAdapter):
    """Permission adapter for MongoDB."""
    def _find_sections(self, hint):
        """Gets a list of permissions in the group specified by `hint`."""
        group = self._db[self._groupdoc()].find_one({self._groupsname(): hint})
        
        if group:
            return [document[self._permissionname()] for document in group.get(self._grouppermissions(), [])]
        else:
            return []

    def _get_all_sections(self):
        raise NotImplementedError()

    def _get_section_items(self, section):
        raise NotImplementedError()

    def _include_items(self, section, items):
        raise NotImplementedError()

    def _item_is_included(self, section, item):
        raise NotImplementedError()

    def _section_exists(self, section):
        raise NotImplementedError()
