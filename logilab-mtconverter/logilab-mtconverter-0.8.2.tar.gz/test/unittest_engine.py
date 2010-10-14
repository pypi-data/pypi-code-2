# copyright 2006-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of logilab-mtconverter.
#
# logilab-mtconverter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 2.1 of the License, or (at your
# option) any later version.
#
# logilab-mtconverter is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with logilab-mtconverter. If not, see <http://www.gnu.org/licenses/>.
from logilab.common.testlib import TestCase, unittest_main
import urllib
import re

from logilab.mtconverter import TransformData, TransformError
from logilab.mtconverter.transforms import text_to_text
from logilab.mtconverter.transform import Transform, TransformsChain
from logilab.mtconverter.engine import TransformEngine


class HtmlToText(Transform):
    inputs = ('text/html',)
    output = 'text/plain'

    def __call__(self, orig):
        orig = re.sub('<[^>]*>(?i)(?m)', '', orig)
        return urllib.unquote(re.sub('\n+', '\n', orig)).strip()

    def _convert(self, data):
        return self.__call__(data.data)

class HtmlToTextWithEncoding(HtmlToText):
    output_encoding = 'utf8'

class FooToBar(Transform):
    inputs = ('text/*',)
    output = 'text/bar'

    def __call__(self, orig):
        orig = re.sub('foo', 'bar', orig)
        return urllib.unquote(re.sub('\n+', '\n', orig)).strip()

    def _convert(self, data):
        return self.__call__(data.data)

class HtmlIdTransform(Transform):
    inputs = ('text/html',)
    output = 'text/html'

    def _convert(self, data):
        return data.data + ' transformed'

class TransformNoIO(Transform):
    pass

class BadTransformNoInput(Transform):
    inputs = ()
    output = 'text/plain'

class BadTransformBadInput1(Transform):
    inputs = ('text/bla/bla',)
    output = 'text/plain'

class BadTransformBadInput2(Transform):
    inputs = ('text/',)
    output = 'text/plain'

class BadTransformBadOutput1(Transform):
    inputs = ('text/plain',)
    output = 'text/bla/bla'

class BadTransformBadOutput2(Transform):
    inputs = ('text/plain',)
    output = 'text/'

class BadTransformWildcardOutput(Transform):
    inputs = ('text/plain',)
    output = 'text/*'


def html_data():
    return TransformData('<b>foo</b>', 'text/html', 'ascii')

class EngineTC(TestCase):
    def setUp(self):
        self.engine = TransformEngine()
        
    def register(self):
        #A default set of transforms to prove the interfaces work
        self.engine.add_transform(HtmlToText())
        self.engine.add_transform(FooToBar())

    def test_register_fail(self):
        register = self.engine.add_transform
        self.assertRaises(TransformError, register, TransformNoIO())
        self.assertRaises(TransformError, register, BadTransformNoInput())
        self.assertRaises(TransformError, register, BadTransformBadInput1())
        self.assertRaises(TransformError, register, BadTransformBadInput2())
        self.assertRaises(TransformError, register, BadTransformWildcardOutput())
        self.assertRaises(TransformError, register, BadTransformBadOutput1())
        self.assertRaises(TransformError, register, BadTransformBadOutput2())

    def test_has_input(self):
        self.register()
        self.failUnless(self.engine.has_input('text/html'))
        self.failUnless(self.engine.has_input('text/plain'))
        self.failUnless(self.engine.has_input('text/whatever'))
        self.failIf(self.engine.has_input('application/octet-stream'))
                        
    def test_convert(self):
        self.register()
        self.engine.add_transform(text_to_text())
        
        data = TransformData("This is a test", 'text/x-diff', 'ascii')
        out = self.engine.convert(data, 'text/plain')
        self.failUnlessEqual(out.data, "This is a test")
        self.failUnlessEqual(out.mimetype, 'text/plain')
        self.failUnlessEqual(out.encoding, 'ascii')

        # html_to_text transform should take priority over text_to_text
        data = self.engine.convert(html_data(), "text/plain")
        self.failUnlessEqual(data.data, "foo")
        self.failUnlessEqual(data.mimetype, 'text/plain')
        self.failUnlessEqual(data.encoding, 'ascii')
        
        self.engine.remove_transform('HtmlToText')
        self.engine.remove_transform('FooToBar')
        self.engine.add_transform(HtmlToTextWithEncoding())
        data = self.engine.convert(html_data(), "text/plain")
        self.failUnlessEqual(data.mimetype, 'text/plain')
        self.failUnlessEqual(data.encoding, 'utf8')

        self.engine.add_transform(FooToBar())
        data = self.engine.convert(html_data(), 'text/bar')
        self.failUnlessEqual(data.data, "<b>bar</b>")

    def test_chain(self):
        #self.register()
        hb = TransformsChain('hbar')
        hb.append(HtmlToText())
        hb.append(FooToBar())
        self.engine.add_transform(hb)
        cache = self.engine.convert(html_data(), 'text/bar')
        self.failUnlessEqual(cache.data, "bar")

    def test_same(self):
        data = TransformData("This is a test", 'text/plain', 'ascii')
        out = self.engine.convert(data, 'text/plain')
        self.failUnlessEqual(out.data, "This is a test")
        self.failUnlessEqual(out.mimetype, 'text/plain')
        self.failUnlessEqual(out.encoding, 'ascii')
        
        self.engine.add_transform(HtmlIdTransform())
        out = self.engine.convert(html_data(), 'text/html')
        self.failUnlessEqual(out.data, "<b>foo</b> transformed")
        self.failUnlessEqual(out.mimetype, 'text/html')
        self.failUnlessEqual(out.encoding, 'ascii')

                                
    def test_convert_compressed(self):
        self.register()
        data = TransformData(open('data.txt.gz', 'rb').read(), 'text/plain', 'gzip')
        self.assertRaises(TransformError, self.engine.convert, data, 'text/plain')
        self.engine.add_transform(text_to_text())
        self.assertRaises(TransformError, self.engine.convert, data, 'text/plain')


if __name__ == '__main__':
    unittest_main()
