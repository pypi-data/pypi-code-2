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
from zope.interface import implements
from Products.CMFCore.interfaces import IContentish
from Products.CMFPlone.interfaces.Translatable import ITranslatable

class DummyResult:
    implements(IContentish)
    _View_Permission = None
        
    def __init__(self, id):
        self._id = id
        
    def getId(self):
        return self._id
        
    def Title(self):
        return 'Title of %s' % self._id
    
    def Description(self):
        return 'Description of %s' % self._id
    
    def absolute_url(self):
        return 'Path of %s' % self._id
    
class TranslatableDummyResult(DummyResult):
    __implements__ = (ITranslatable,)
    
    def getTranslation(self, language=None):
        if self._id == 'no-translation':
            return None
        if self._id == 'language-neutral':
            if language is None:
                return None
            return DummyResult(self._id + ' language neutral')
        return DummyResult(self._id + ' translation')
    
class DummyPortal:
    def __init__(self, paths=None):
        self._paths = paths
        
    def getPortalObject(self):
        return self
    
    def unrestrictedTraverse(self, path, default):
        id = self._paths.get(path)
        if id is not None:
            if path.endswith('/translation'):
                return TranslatableDummyResult(id)
            res = DummyResult(id)
            if path.endswith('/protected'):
                res._View_Permission = ()
            return res
        return default

class TakeActionToolListActionsTests(unittest.TestCase):
    def setUp(self):
        from Products.takeaction.takeaction import TakeActionTool
        self.tool = TakeActionTool()
        self.tool.portal_url = DummyPortal({
            '/foo/bar': 'baz',
            '/foo/spam/bar': 'baz',
            '/foo/eggs/bar': 'baz',
            '/spam/eggs': 'monty',
            '/foo/translation': 'python',
            '/foo/protected': 'perl',
            '/bar/translation': 'no-translation',
            '/baz/translation': 'language-neutral'
        })
        
    def testEmpty(self):
        """No paths in the tool means no actions"""
        self.assertEqual(self.tool.listActions(), [])
        
    def testNonExistent(self):
        """Non-existing paths result in no actions"""
        self.tool.addAction('/no/such/path')
        self.assertEqual(self.tool.listActions(), [])
        
    def testNoAccess(self):
        """No view access means no actions"""
        self.tool.addAction('/foo/protected')
        self.assertEqual(self.tool.listActions(), [])
        
    def testCategory(self):
        """Setting the action category results in actions with that category"""
        self.tool.addAction('/foo/bar', 'foobar')
        result = self.tool.listActions()
        self.assertEqual(result[0].getCategory(), 'foobar')
        
    def testNonTranslatable(self):
        """Normal CMF content paths results"""
        self.tool.addAction('/foo/bar')
        self.tool.addAction('/spam/eggs')
        result = self.tool.listActions()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].getId(), 'takeaction-baz')
        self.assertEqual(result[0].Title(), 'Title of baz')
        self.assertEqual(result[0].Description(), 'Description of baz')
        self.assertEqual(result[0].getActionExpression(), 'string:Path of baz')
        self.assertEqual(result[1].getId(), 'takeaction-monty')
        self.assertEqual(result[1].Title(), 'Title of monty')
        
    def testDuplicateIds(self):
        """Unique action ids even when there are duplicate object ids"""
        self.tool.addAction('/foo/bar')
        self.tool.addAction('/foo/spam/bar')
        self.tool.addAction('/foo/eggs/bar')
        result = self.tool.listActions()
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].getId(), 'takeaction-baz')
        self.assertEqual(result[1].getId(), 'takeaction-baz-2')
        self.assertEqual(result[2].getId(), 'takeaction-baz-3')
        
    def testTranslatable(self):
        """Translatable content results in actions for tranlations"""
        self.tool.addAction('/foo/translation')
        result = self.tool.listActions()
        self.assertEqual(result[0].getId(), 'takeaction-python')
        self.assertEqual(result[0].Title(), 'Title of python translation')
        
    def testTranslatableNoTranslation(self):
        """Translatable without an appropriate translation means no action"""
        self.tool.addAction('/bar/translation')
        self.assertEqual(self.tool.listActions(), [])
        
    def testTranslatableLanguageNeutral(self):
        """Translatable, no translation, but with language neutral version"""
        self.tool.addAction('/baz/translation')
        result = self.tool.listActions()
        self.assertEqual(result[0].getId(), 'takeaction-language-neutral')
        self.assertEqual(result[0].Title(),
                         'Title of language-neutral language neutral')
        

class TakeActionToolEditActionsTests(unittest.TestCase):
    def setUp(self):
        from Products.takeaction.takeaction import TakeActionTool
        self.tool = TakeActionTool()
        
    def testAddAction(self):
        from Products.takeaction.takeaction import TakeActionItem
        self.tool.addAction('/foo/bar')
        self.assertEqual(self.tool._items, (TakeActionItem('/foo/bar'),))
        
        self.assertRaises(ValueError, self.tool.addAction, '/foo/bar')
        
        self.tool.addAction('/foo/bar', 'baz')
        self.assertEqual(self.tool._items, (TakeActionItem('/foo/bar'),
                                            TakeActionItem('/foo/bar', 'baz')))
        
        self.assertRaises(ValueError, self.tool.addAction, '/foo/bar', 'baz')
        
    def testDeleteAction(self):
        from Products.takeaction.takeaction import TakeActionItem
        self.tool.addAction('/foo/bar')
        self.tool.addAction('/foo/bar', 'baz')
        
        self.tool.deleteAction('/foo/bar')
        self.assertEqual(self.tool._items, (TakeActionItem('/foo/bar', 'baz'),))
        
        self.tool.addAction('/foo/bar')
        self.tool.deleteAction('/foo/bar', 'baz')
        self.assertEqual(self.tool._items, (TakeActionItem('/foo/bar'),))
        
        self.tool.deleteAction('nonesuch')
        self.assertEqual(self.tool._items, (TakeActionItem('/foo/bar'),))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests((
        unittest.makeSuite(TakeActionToolListActionsTests),
        unittest.makeSuite(TakeActionToolEditActionsTests),
    ))
    return suite

if __name__ == '__main__':
    unittest.main()
