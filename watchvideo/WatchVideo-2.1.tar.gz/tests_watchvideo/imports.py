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


"""Test importing WatchVideo modules.

This should detect syntax compatibility with old Python versions and
the code coverage will show unused modules.
"""


import unittest


__all__ = ("ImportsTestCase",)


class ImportsTestCase(unittest.TestCase):

    """Tests for importing WatchVideo modules."""

    def test_cli(self):
        """Test importing watchvideo script module"""
        import watchvideo.watchvideo_cli

    def test_qt(self):
        """Test importing qtwatchvideo script module"""
        import watchvideo.watchvideo_gui

    def test_add_videos(self):
        """Test importing add videos dialog"""
        from watchvideo.add_videos import AddVideosDialog
        self.assert_(AddVideosDialog)

    def test_about(self):
        """Test importing about dialog"""
        from watchvideo.about import AboutDialog
        self.assert_(AboutDialog)
