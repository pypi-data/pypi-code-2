# takeaction: content as actions
# Copyright (C) 2007 Jarn AS
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
import unittest

from Products.Five import zcml

from Products.GenericSetup.testing import BodyAdapterTestCase

_BODY = """\
<?xml version="1.0"?>
<object name="portal_takeaction"
   meta_type="TakeAction content-as-actions tool">
 <item category="spam" path="foo/bar"/>
 <item category="eggs" path="monty/python"/>
</object>
"""

class ImportExportTests(BodyAdapterTestCase):
    def setUp(self):
        import Products.GenericSetup
        import Products.Five
        import Products.takeaction
        from Products.takeaction.takeaction import TakeActionTool
        
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('meta.zcml', Products.GenericSetup)
        zcml.load_config('configure.zcml', Products.GenericSetup)
        zcml.load_config('configure.zcml', Products.takeaction)
        
        self._obj = TakeActionTool()
        self._BODY = _BODY

    def _getTargetClass(self):
        from Products.takeaction.exportimport import TakeActionToolXMLAdapter
        return TakeActionToolXMLAdapter

    def _populate(self, obj):
        obj.addAction('foo/bar', 'spam')
        obj.addAction('monty/python', 'eggs')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests((
        unittest.makeSuite(ImportExportTests),
    ))
    return suite

if __name__ == '__main__':
    unittest.main()
