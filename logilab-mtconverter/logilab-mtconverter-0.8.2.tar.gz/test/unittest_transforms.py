# -*- coding: iso-8859-1 -*-
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

from logilab.mtconverter.engine import TransformEngine
from logilab.mtconverter import TransformData, TransformError, \
     register_base_transforms, register_pil_transforms

ENGINE = TransformEngine()
register_base_transforms(ENGINE)
register_pil_transforms(ENGINE)

import logilab.mtconverter as mtc
import os.path as osp
DATAPATH = osp.join(osp.split(mtc.__file__)[0], 'test')

class MiscTransformsTC(TestCase):
    def test_html_to_text(self):
        data = TransformData(u'<b>yo (zou éà ;)</b>', 'text/html', 'utf8')
        converted = ENGINE.convert(data, 'text/plain').decode().strip()
        self.assertEquals(converted, u'**yo (zou éà ;)**')

        # will trigger guess_encoding, check non-utf8 encoding
        data = TransformData(u'<b>yo (zou éà ;)</b>'.encode('latin1'), 'text/html')
        converted = ENGINE.convert(data, 'text/plain').decode().strip()
        self.assertEquals(converted, u'**yo (zou éà ;)**')

        data = TransformData(u'<p>yo <br/>zogzog </p>', 'text/html', 'utf8')
        converted = ENGINE.convert(data, 'text/plain').decode().strip()
        self.assertEquals(converted, u'yo\n\nzogzog')

    def test_xml_to_text(self):
        data = TransformData(u'<root><b>yo (zou éà ;)</b>a<tag/>b<root>', 'application/xml', 'utf8')
        converted = ENGINE.convert(data, 'text/plain').decode().strip()
        self.assertEquals(converted, u'yo (zou éà ;) a b')


    def test_pgpsignature_to_text(self):
        _data = u"""-----BEGIN PGP SIGNATURE-----
Version: GnuPG v1.4.9 (GNU/Linux)

iEYEARECAAYFAkxX5p8ACgkQkjcInxztrI64QQCggKA+PmbLYnGNtBB3Lb3pO3P8
r2MAoIO1DSsuM23SzgmqubGJEZuSRWhR
=GDDk
-----END PGP SIGNATURE-----
"""
        data = TransformData(_data, 'application/pgp-signature')
        converted = ENGINE.convert(data, 'text/plain').decode()
        self.assertTextEquals(converted, _data)


    def test_odt_to_text(self):
        data = TransformData(open(osp.join(DATAPATH, 'hello.odt')),
                             'application/vnd.oasis.opendocument.text', 'utf8')
        converted = ENGINE.convert(data, 'text/plain').decode().strip()
        self.assertEquals(converted, u'Hello ! OpenOffice.org/2.4$Unix OpenOffice.org_project/680m17$Build-9310 Hello quoi de neuf doc ? bonjour 2008-07-08T16:19:35 2009-01-09T14:44:54 mot-clef 1 PT37S')
        # ZipFile will complain that
        # TypeError: file() argument 1 must be (encoded string without NULL bytes), not str
        # if given a plain str ... we shielded us from that.
        data = TransformData(open(osp.join(DATAPATH, 'hello.odt')).read(),
                             'application/vnd.oasis.opendocument.text', 'utf8')
        converted = ENGINE.convert(data, 'text/plain').decode().strip()
        self.assertEquals(converted, u'Hello ! OpenOffice.org/2.4$Unix OpenOffice.org_project/680m17$Build-9310 Hello quoi de neuf doc ? bonjour 2008-07-08T16:19:35 2009-01-09T14:44:54 mot-clef 1 PT37S')

if __name__ == '__main__':
    unittest_main()


## from utils import input_file_path, output_file_path, normalize_html,\
##      load, matching_inputs

## from logilab.mtconverter import MissingBinary
## from logilab.mtconverter.transforms.piltransforms import image_to_gif
## from logilab.mtconverter.transforms.piltransforms import image_to_png
## from logilab.mtconverter.transforms.piltransforms import image_to_jpeg
## from logilab.mtconverter.transforms.piltransforms import image_to_bmp
## from logilab.mtconverter.transforms.piltransforms import image_to_tiff
## from logilab.mtconverter.transforms.piltransforms import image_to_ppm
## from logilab.mtconverter.transforms.piltransforms import image_to_pcx

## from os.path import exists
## import sys
## # we have to set locale because lynx output is locale sensitive !
## os.environ['LC_ALL'] = 'C'


## class TransformTest(TestCase):

##     def do_convert(self, filename=None):
##         if filename is None and exists(self.output + '.nofilename'):
##             output = self.output + '.nofilename'
##         else:
##             output = self.output
##         input = open(self.input)
##         orig = input.read()
##         input.close()
##         data = datastream(self.transform.name())
##         res_data = self.transform.convert(orig, data, filename=filename)
##         self.assert_(idatastream.isImplementedBy(res_data))
##         got = res_data.getData()
##         try:
##             output = open(output)
##         except IOError:
##             import sys
##             print >>sys.stderr, 'No output file found.'
##             print >>sys.stderr, 'File %s created, check it !' % self.output
##             output = open(output, 'w')
##             output.write(got)
##             output.close()
##             self.assert_(0)
##         expected = output.read()
##         if self.normalize is not None:
##             expected = self.normalize(expected)
##             got = self.normalize(got)
##         output.close()

##         self.assertEquals(got, expected,
##                           '[%s]\n\n!=\n\n[%s]\n\nIN %s(%s)' % (
##             got, expected, self.transform.name(), self.input))
##         self.assertEquals(self.subobjects, len(res_data.getSubObjects()),
##                           '%s\n\n!=\n\n%s\n\nIN %s(%s)' % (
##             self.subobjects, len(res_data.getSubObjects()), self.transform.name(), self.input))

##     def testSame(self):
##         self.do_convert(filename=self.input)

##     def testSameNoFilename(self):
##         self.do_convert()

##     def __repr__(self):
##         return self.transform.name()


## class PILTransformsTest(TestCase):
##     def afterSetUp(self):
##         ATSiteTestCase.afterSetUp(self)
##         self.pt = self.portal.portal_transforms

##     def test_image_to_bmp(self):
##         self.pt.registerTransform(image_to_bmp())
##         imgFile = open(input_file_path('logo.jpg'), 'rb')
##         data = imgFile.read()
##         self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
##         data = self.pt.convertTo(target_mimetype='image/x-ms-bmp',orig=data)
##         self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/x-ms-bmp')

##     def test_image_to_gif(self):
##         self.pt.registerTransform(image_to_gif())
##         imgFile = open(input_file_path('logo.png'), 'rb')
##         data = imgFile.read()
##         self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/png')
##         data = self.pt.convertTo(target_mimetype='image/gif',orig=data)
##         self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/gif')

##     def test_image_to_jpeg(self):
##         self.pt.registerTransform(image_to_jpeg())
##         imgFile = open(input_file_path('logo.gif'), 'rb')
##         data = imgFile.read()
##         self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/gif')
##         data = self.pt.convertTo(target_mimetype='image/jpeg',orig=data)
##         self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/jpeg')

##     def test_image_to_png(self):
##         self.pt.registerTransform(image_to_png())
##         imgFile = open(input_file_path('logo.jpg'), 'rb')
##         data = imgFile.read()
##         self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
##         data = self.pt.convertTo(target_mimetype='image/png',orig=data)
##         self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/png')

##     def test_image_to_pcx(self):
##         self.pt.registerTransform(image_to_pcx())
##         imgFile = open(input_file_path('logo.gif'), 'rb')
##         data = imgFile.read()
##         self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/gif')
##         data = self.pt.convertTo(target_mimetype='image/pcx',orig=data)
##         self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/pcx')

##     def test_image_to_ppm(self):
##         self.pt.registerTransform(image_to_ppm())
##         imgFile = open(input_file_path('logo.png'), 'rb')
##         data = imgFile.read()
##         self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/png')
##         data = self.pt.convertTo(target_mimetype='image/x-portable-pixmap',orig=data)
##         self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/x-portable-pixmap')

##     def test_image_to_tiff(self):
##         self.pt.registerTransform(image_to_tiff())
##         imgFile = open(input_file_path('logo.jpg'), 'rb')
##         data = imgFile.read()
##         self.failUnlessEqual(self.portal.mimetypes_registry.classify(data),'image/jpeg')
##         data = self.pt.convertTo(target_mimetype='image/tiff',orig=data)
##         self.failUnlessEqual(data.getMetadata()['mimetype'], 'image/tiff')


## TRANSFORMS_TESTINFO = (
##     ('Products.PortalTransforms.transforms.pdf_to_html',
##      "demo1.pdf", "demo1.html", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.word_to_html',
##      "test.doc", "test_word.html", normalize_html, 0
##      ),
##     ('Products.PortalTransforms.transforms.lynx_dump',
##      "test_lynx.html", "test_lynx.txt", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.html_to_text',
##      "test_lynx.html", "test_html_to_text.txt", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.identity',
##      "rest1.rst", "rest1.rst", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.text_to_html',
##      "rest1.rst", "rest1.html", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.safe_html',
##      "test_safehtml.html", "test_safe.html", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.image_to_bmp',
##      "logo.jpg", "logo.bmp", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.image_to_gif',
##      "logo.bmp", "logo.gif", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.image_to_jpeg',
##      "logo.gif", "logo.jpg", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.image_to_png',
##      "logo.bmp", "logo.png", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.image_to_ppm',
##      "logo.gif", "logo.ppm", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.image_to_tiff',
##      "logo.png", "logo.tiff", None, 0
##      ),
##     ('Products.PortalTransforms.transforms.image_to_pcx',
##      "logo.png", "logo.pcx", None, 0
##      ),
##     )

## def initialise(transform, normalize, pattern):
##     global TRANSFORMS_TESTINFO
##     for fname in matching_inputs(pattern):
##         outname = '%s.out' % fname.split('.')[0]
##         #print transform, fname, outname
##         TRANSFORMS_TESTINFO += ((transform, fname, outname, normalize, 0),)


## # ReST test cases
## initialise('Products.PortalTransforms.transforms.rest', normalize_html, "rest*.rst")
## # Python test cases
## initialise('Products.PortalTransforms.transforms.python', normalize_html, "*.py")

## # FIXME missing tests for image_to_html, st

## TR_NAMES = None

## # generate tests classes from test info
## for _transform, tr_input, tr_output, _normalize, _subobjects in TRANSFORMS_TESTINFO:
##     # load transform if necessary
##     if type(_transform) is type(''):
##         try:
##             _transform = load(_transform).register()
##         except MissingBinary:
##             # we are not interessted in tests with missing binaries
##             continue
##         except:
##             import traceback
##             traceback.print_exc()
##             continue

##     if TR_NAMES is not None and not _transform.name() in TR_NAMES:
##         print 'skip test for', _transform.name()
##         continue

##     class TransformTestSubclass(TransformTest):
##         input = input_file_path(tr_input)
##         output = output_file_path(tr_output)
##         transform = _transform
##         normalize = lambda x, y: _normalize(y)
##         subobjects = _subobjects

##     tests.append(TransformTestSubclass)

## tests.append(PILTransformsTest)


