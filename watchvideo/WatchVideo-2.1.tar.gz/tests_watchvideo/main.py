# -*- coding: utf-8 -*-
# Copyright (C) 2011  Michał Masłowski  <mtjm@mtjm.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Tests for `watchvideo.main`."""


import unittest


__all__ = ("GetDefaultPlayerTestCase",)


class GetDefaultPlayerTestCase(unittest.TestCase):

    """Tests for `watchvideo.main.get_default_player`."""

    def test_is_command(self):
        """Test that the default player is a command"""
        from watchvideo.main import get_default_player
        from watchvideo.utils import is_command
        self.assert_(is_command(get_default_player()))

    def test_not_changed(self):
        """Test that the default player doesn't change"""
        from watchvideo.main import get_default_player
        player_1 = get_default_player()
        player_2 = get_default_player()
        self.assertEquals(player_1, player_2)
