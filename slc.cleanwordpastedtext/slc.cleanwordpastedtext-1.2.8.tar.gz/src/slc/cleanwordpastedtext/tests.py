from zope import event
from Products.Archetypes.event import ObjectInitializedEvent
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
import slc.cleanwordpastedtext

ptc.setupPloneSite()

# Set up the Plone site used for the test fixture. The PRODUCTS are the products
# to install in the Plone site (as opposed to the products defined above, which
# are all products available to Zope in the test fixture)
PRODUCTS = ['slc.cleanwordpastedtext']
ptc.setupPloneSite(products=PRODUCTS)

class TestCase(ptc.PloneTestCase):
    """Base class for integration tests. This may
    provide specific set-up and tear-down operations, or provide convenience
    methods.
    """
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             slc.cleanwordpastedtext)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

old_text = """<p>\n<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n<meta name="ProgId" content="Word.Document" />\n<meta name="Generator" content="Microsoft Word 12" />\n<meta name="Originator" content="Microsoft Word 12" />\n\n\n\n\n\n\n\n\n</p>\n<p class="MsoNormal"><b style=""><i style=""><u><span style="color: rgb(192, 0, 0);">Donec sagittis quam vel urna viverra fringilla. Nam sollicitudin lectus diam, eget placerat sapien. Vivamus faucibus dui eget lectus bibendum rhoncus. In rutrum dapibus lorem a tincidunt. Morbi est nisi, venenatis at venenatis vitae, porttitor facilisis metus. Duis dapibus molestie accumsan. Morbi porta ornare mollis. Vestibulum eu viverra felis. Aliquam erat volutpat. Quisque nisl est, imperdiet ut malesuada nec; gravida a urna!</span></u></i></b></p>\n"""

new_text = """<p class="MsoNormal">Donec sagittis quam vel urna viverra fringilla. Nam sollicitudin lectus diam, eget placerat sapien. Vivamus faucibus dui eget lectus bibendum rhoncus. In rutrum dapibus lorem a tincidunt. Morbi est nisi, venenatis at venenatis vitae, porttitor facilisis metus. Duis dapibus molestie accumsan. Morbi porta ornare mollis. Vestibulum eu viverra felis. Aliquam erat volutpat. Quisque nisl est, imperdiet ut malesuada nec; gravida a urna!</p>\n"""


class TestCleanWordPastedText(TestCase):

    def afterSetUp(self):
        self.loginAsPortalOwner()

    def test_clean_word_pasted_text(self):
        self.portal.invokeFactory('Document', 'word_pasted_doc')
        doc = self.portal._getOb('word_pasted_doc')
        doc.setTitle('Word Pasted Doc')
        field = doc.Schema().get('text')
        field.getMutator(doc)(old_text)

        doc.Schema().get('cleanWordPastedText').set(doc, False)
        event.notify(ObjectInitializedEvent(doc))
        self.assertEquals(doc.getText(), old_text)

        doc.Schema().get('cleanWordPastedText').set(doc, True)
        event.notify(ObjectInitializedEvent(doc))
        self.assertEquals(doc.getText(), new_text)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestCleanWordPastedText))
    return suite

