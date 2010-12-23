#!/usr/bin/env python
# -*- coding: utf-8 -*-

# forbi: a TCP-based communication tool
# Copyright (C) 2010  Niels Serup

# This file is part of forbi.
#
# forbi is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# forbi is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with forbi. If not, see
# <http://www.gnu.org/licenses/>.

##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Functions for keeping data

try:
    import cPickle as pickle
except ImportError:
    import pickle
import hashlib
import forbi.misc as misc

class UserSaves(misc.Container):
    """
    Contains usernames together with hashed passwords. Support for
    loading and saving.
    """
    def __init__(self, filename):
        self.path = filename
        self.users = {}

    def load(self):
        """Load data from a file"""
        try:
            with open(self.path, 'rb') as f:
                users = pickle.load(f)
                for user, password in users.iteritems():
                    if user not in self.users:
                        self.users[user] = password
        except IOError:
            pass

    def clear(self):
        self.users = {}

    def save(self):
        """Save data to a file"""
        try:
            with open(self.path, 'wb') as f:
                pickle.dump(self.users, f)
        except IOError:
            pass

    def add(self, user, password):
        """Add a user"""
        assert not self.has(user), 'User %s already exists' % user
        self.set(user, password)

    def change(self, user, password):
        """Change a user's password"""
        assert self.has(user), 'User %s does not exist' % user
        self.set(user, password)

    def set(self, user, password):
        """Set a user's password"""
        self.users[user] = self.hash(password)
        self.save()

    def remove(self, user):
        """Remove a user"""
        assert user in self.users, 'User %s does not exist' % user
        del self.users[user]
        self.save()

    def hash(self, text):
        """Hash digest text"""
        return hashlib.sha256(text).digest()

    def has(self, user):
        """See if user is saved"""
        return user in self.users.iterkeys()

    def match(self, user, password):
        """See if password matches user's password"""
        assert user in self.users, 'User %s does not exist' % user
        return self.users[user] == self.hash(password)
