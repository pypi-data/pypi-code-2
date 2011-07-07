##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
import unittest


class CompositeTests(unittest.TestCase):

    def setUp(self):
        from zope.testing.cleanup import cleanUp
        from AccessControl.SecurityManagement import noSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy
        from Products.CompositePage.tests.test_tool \
            import PermissiveSecurityPolicy
        cleanUp()
        self.old_policy = setSecurityPolicy(PermissiveSecurityPolicy())
        noSecurityManager()

    def tearDown(self):
        from zope.testing.cleanup import cleanUp
        from AccessControl.SecurityManagement import noSecurityManager
        from AccessControl.SecurityManager import setSecurityPolicy
        setSecurityPolicy(self.old_policy)
        noSecurityManager()
        cleanUp()

    def _make_composite(self):
        from OFS.Folder import Folder
        from ZPublisher.HTTPRequest import HTTPRequest
        from ZPublisher.HTTPRequest import HTTPResponse
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        from Products.CompositePage.composite import Composite
        from Products.CompositePage.element import CompositeElement
        from Products.CompositePage.slot import Slot

        TEMPLATE_TEXT = '\n'.join((
            '<html>',
            '<body>',
            """<div tal:replace="structure slot: slot_a (top) """
                """'Top News Stories'">slot_a</div>""",
            """<span tal:replace="structure slot: slot_b """
                """'Other News'">slot_b</span>""",
            '<div tal:replace="structure context/slots/slot_c">slot_c</div>',
            '</body>',
            '</html>',
        ))
        f = Folder()
        f.getPhysicalPath = lambda: ()
        f.getPhysicalRoot = lambda f=f: f
        req = f.REQUEST = HTTPRequest('', dict(HTTP_HOST='localhost:8080'), {})
        req.response = HTTPResponse()
        f.composite = Composite()
        f.composite._setId("composite")
        t = ZopePageTemplate(
            id="template", text=TEMPLATE_TEXT, content_type="text/html")
        f.composite.template = t
        f.composite.filled_slots.slot_a = slot_a = Slot("slot_a")
        t = f.composite.template
        if t.pt_errors():
            raise SyntaxError(t.pt_errors())
        a1 = ZopePageTemplate(id="a1", text="<b>Slot A</b>")
        f._setObject(a1.id, a1)
        e1 = CompositeElement('e1', f.a1)
        slot_a._setObject(e1.id, e1)
        return f.composite

    def _registerTraversable(self):
        from zope.component import getGlobalSiteManager
        from zope.interface import Interface
        from zope.traversing.interfaces import ITraversable
        from zope.traversing.adapters import DefaultTraversable
        getGlobalSiteManager().registerAdapter(
            DefaultTraversable, [Interface], ITraversable)

    def assertTextEqual(self, a, b):
        a = a.strip().replace("\n", "")
        b = b.strip().replace("\n", "")
        self.assertEqual(a, b)

    def test_render(self):
        self._registerTraversable()
        rendered = self._make_composite()()
        expected = ('<html><body>'
                    '<div class="slot_header"></div><div><b>Slot A</b></div>'
                    '<div class="slot_header"></div>'
                    '<div class="slot_header"></div>'
                    '</body></html>')
        self.assertTextEqual(rendered, expected)

    def test_getManifest(self):
        self._registerTraversable()
        manifest = self._make_composite().getManifest()
        self.assertEqual(len(manifest), 3)
        self.assertEqual(manifest[0]['name'], 'slot_a')
        self.assertEqual(manifest[0]['title'], 'Top News Stories')
        self.assertEqual(manifest[0]['class_name'], 'top')
        self.assertEqual(
            manifest[0]['target_path'], 'composite/filled_slots/slot_a')
        self.assertEqual(len(manifest[0]['elements']), 1)

        self.assertEqual(manifest[1]['name'], 'slot_b')
        self.assertEqual(manifest[1]['title'], 'Other News')
        self.assertEqual(manifest[1]['class_name'], None)
        self.assertEqual(
            manifest[1]['target_path'], 'composite/filled_slots/slot_b')
        self.assertEqual(len(manifest[1]['elements']), 0)

        self.assertEqual(manifest[2]['name'], 'slot_c')
        self.assertEqual(manifest[2]['title'], 'slot_c')
        self.assertEqual(manifest[2]['class_name'], None)
        self.assertEqual(
            manifest[2]['target_path'], 'composite/filled_slots/slot_c')
        self.assertEqual(len(manifest[2]['elements']), 0)

    def test_slot_expr_compiler_error(self):
        # Bad slot expressions should produce a reasonable error.
        from Products.PageTemplates.ZopePageTemplate import ZopePageTemplate
        from zope.tal.taldefs import TALError
        text = '<div tal:content="structure slot: a b" />'
        try:
            t = ZopePageTemplate(
                id="template", text=text, content_type="text/html")
        except TALError, e:
            msg = unicode(e)
        else:
            msg = ' '.join(t.pt_errors())
            if not msg:
                raise AssertionError("Expected a syntax error")
        self.assertTrue("syntax error" in msg)

    def test_getSlotClassName(self):
        self._registerTraversable()
        composite = self._make_composite()
        self.assertEqual(composite.getSlotClassName('slot_a'), 'top')
        self.assertEqual(composite.getSlotClassName('slot_b'), None)
        self.assertEqual(composite.getSlotClassName('slot_c'), None)
        self.assertRaises(KeyError,
                          composite.getSlotClassName, 'nonexistent_slot')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(CompositeTests),
    ))
