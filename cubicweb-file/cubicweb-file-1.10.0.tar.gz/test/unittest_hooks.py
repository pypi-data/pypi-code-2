# -*- coding: utf-8 -*-

import locale

from os.path import join, dirname
from PIL.Image import open as pilopen

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC


class FileTC(CubicWebTC):

    def test_set_mime_and_encoding(self):
        fobj = self.request().create_entity('File', data_name=u"foo.txt", data=Binary("xxx"))
        self.assertEqual(fobj.data_format, u'text/plain')
        self.assertEqual(fobj.data_encoding, self.request().encoding)

    def test_set_mime_and_encoding_gz_file(self):
        fobj = self.request().create_entity('File', data_name=u"foo.txt.gz", data=Binary("xxx"))
        self.assertEqual(fobj.data_format, u'text/plain')
        self.assertEqual(fobj.data_encoding, u'gzip')
        fobj = self.request().create_entity('File', data_name=u"foo.txt.gz", data=Binary("xxx"),
                               data_format='application/gzip')
        self.assertEqual(fobj.data_format, u'text/plain')
        self.assertEqual(fobj.data_encoding, u'gzip')
        fobj = self.request().create_entity('File', data_name=u"foo.gz", data=Binary("xxx"))
        self.assertEqual(fobj.data_format, u'application/gzip')
        self.assertEqual(fobj.data_encoding, None)


    def test_set_mime_and_encoding_bz2_file(self):
        fobj = self.request().create_entity('File', data_name=u"foo.txt.bz2", data=Binary("xxx"))
        self.assertEqual(fobj.data_format, u'text/plain')
        self.assertEqual(fobj.data_encoding, u'bzip2')
        fobj = self.request().create_entity('File', data_name=u"foo.txt.bz2", data=Binary("xxx"),
                               data_format='application/bzip2')
        self.assertEqual(fobj.data_format, u'text/plain')
        self.assertEqual(fobj.data_encoding, u'bzip2')
        fobj = self.request().create_entity('File', data_name=u"foo.bz2", data=Binary("xxx"))
        self.assertEqual(fobj.data_format, u'application/bzip2')
        self.assertEqual(fobj.data_encoding, None)

    def test_set_mime_and_encoding_unknwon_ext(self):
        fobj = self.request().create_entity('File', data_name=u"foo.123", data=Binary("xxx"))
        self.assertEqual(fobj.data_format, u'application/octet-stream')
        self.assertEqual(fobj.data_encoding, None)


class ImageTC(CubicWebTC):

    @property
    def data(self):
        return file(join(dirname(__file__), 'data', '20x20.gif')).read()

    def test_resize_image(self):
        # check no resize
        img = self.request().create_entity('File', data=Binary(self.data), data_name=u'20x20.gif')
        self.assertEqual(img.data_format, u'image/gif')
        self.assertEqual(img.data.getvalue(), self.data)
        # check thumb
        self.set_option('image-thumb-size', '5x5')
        pilthumb = pilopen(img.cw_adapt_to('IImage').thumbnail(shadow=False))
        self.assertEqual(pilthumb.size, (5, 5))
        # check resize 10x5
        self.set_option('image-max-size', '10x5')
        img = self.request().create_entity('File', data=Binary(self.data), data_name=u'20x20.gif')
        self.assertEqual(img.data_format, u'image/gif')
        pilimg = pilopen(img.data)
        self.assertEqual(pilimg.size, (5, 5))
        # also on update
        img.set_attributes(data=Binary(self.data))
        img.clear_all_caches()
        pilimg = pilopen(img.data)
        self.assertEqual(pilimg.size, (5, 5))
        # test image smaller than max size
        self.set_option('image-max-size', '40x40')
        img.set_attributes(data=Binary(self.data))
        pilimg = pilopen(img.data)
        self.assertEqual(pilimg.size, (20, 20))

if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
