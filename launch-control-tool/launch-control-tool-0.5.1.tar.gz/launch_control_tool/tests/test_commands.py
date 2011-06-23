# Copyright (C) 2010,2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of launch-control-tool.
#
# launch-control-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# launch-control-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launch-control-tool.  If not, see <http://www.gnu.org/licenses/>.

"""
Unit tests for the launch_control.commands package
"""

from unittest import TestCase

from launch_control_tool.commands import XMLRPCCommand


class XMLRPCCommandTestCase(TestCase):

    def test_construct_xml_rpc_url_preserves_path(self):
        self.assertEqual(
            XMLRPCCommand._construct_xml_rpc_url("http://domain/path"),
            "http://domain/path/xml-rpc/")
        self.assertEqual(
            XMLRPCCommand._construct_xml_rpc_url("http://domain/path/"),
            "http://domain/path/xml-rpc/")

    def test_construct_xml_rpc_url_adds_proper_suffix(self):
        self.assertEqual(
            XMLRPCCommand._construct_xml_rpc_url("http://domain/"),
            "http://domain/xml-rpc/")
        self.assertEqual(
            XMLRPCCommand._construct_xml_rpc_url("http://domain"),
            "http://domain/xml-rpc/")
