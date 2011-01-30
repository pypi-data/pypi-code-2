#
# Exportimport NodeAdapter tests
#

from Products.GenericSetup.testing import NodeAdapterTestCase
from Products.CMFTestCase.CMFTestCase import CMF21
from Products.CMFTestCase import layer
from Products.Five import zcml


_UNICODELEXICON_XML = """\
<object name="unicode_lexicon" meta_type="ZCTextIndex Unicode Lexicon">
 <element name="HTML aware splitter" group="Word Splitter"/>
 <element name="Case normalizer" group="Case Normalizer"/>
 <element name="Normalize accented chars (Latin &amp; Western European text)"
    group="Accent Normalizer"/>
</object>
"""


class UnicodeLexiconNodeAdapterTests(NodeAdapterTestCase):

    if CMF21:
        layer = layer.ZCML

    def _getTargetClass(self):
        from Products.UnicodeLexicon.exportimport \
                    import UnicodeLexiconNodeAdapter
        return UnicodeLexiconNodeAdapter

    def _populate(self, obj):
        from Products.UnicodeLexicon.pipeline import UnicodeHTMLWordSplitter
        from Products.UnicodeLexicon.pipeline import UnicodeCaseNormalizer
        from Products.UnicodeLexicon.pipeline import UnicodeLatinAccentNormalizer
        obj._pipeline = (UnicodeHTMLWordSplitter(),
                         UnicodeCaseNormalizer(),
                         UnicodeLatinAccentNormalizer())

    def setUp(self):
        import Products.GenericSetup
        import Products.UnicodeLexicon
        from Products.UnicodeLexicon.lexicon import UnicodeLexicon

        NodeAdapterTestCase.setUp(self)
        zcml.load_config('meta.zcml', Products.GenericSetup)
        zcml.load_config('configure.zcml', Products.UnicodeLexicon)

        self._obj = UnicodeLexicon('unicode_lexicon')
        self._XML = _UNICODELEXICON_XML

    def tearDown(self):
        # XXX: Do *not* tear down the CA here as this interacts
        # badly with other test modules, particularly testSetup.
        pass


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(UnicodeLexiconNodeAdapterTests))
    return suite

