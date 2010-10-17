# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2010 Joshua D Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

from trosnoth.network.authserver import AuthenticatedUser
from trosnoth.network import authserver

ACH_ID = 'test'
PATH = '/tmp'

fakeAchievement = ...
STUBS = [
    (authserver, 'achievementDict', {ACH_ID: fakeAchievement})
]

_inPlaceStubs = {}

def setStubs():
    for obj, attr, value in STUBS:
        assert not _inPlaceStubs.has_key((obj, attr))
        _inPlaceStubs[(obj, attr)] = getattr(obj, attr)
        setattr(obj, attr, value)

def unsetStubs():
    for (obj, attr), value in _inPlaceStubs:
        setattr(obj, attr, value)
    _inPlaceStubs.clear()

def mockAuthUser():
    result = object.__new__(AuthenticatedUser)
    result._path = PATH
    return result

def test_load_achievements():
    user = mockAuthUser()

    user._loadAchievements()
    assert len(user.achievements) == 1

    achData = user.achievements[ACH_ID]
    assert achData['unlocked'] == False
    assert achData['progress'] == 0

