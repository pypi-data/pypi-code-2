# -*- coding: utf-8 -*-
'''
Created on 03.06.2009

@author: cykooz
'''

import os
import tempfile
import unittest
import doctest
import shutil
from cStringIO import StringIO

import webob
from webob.exc import HTTPNotFound
from paste.fileapp import FileApp 
import zope.datetime
import Image

from cykooz.thumbs.middleware import Thumbs, make_thumbs

this_path = os.path.dirname(os.path.abspath(__file__))

def test_app(environ, start_response):
	request = webob.Request(environ)
	app = None
	if 'not_found' in request.GET:
		app = HTTPNotFound()
	elif request.path_info == '/html/index.html':
		app = FileApp(os.path.join(this_path, 'index.html'))
	elif request.path_info == '/image/image.jpg':
		app = FileApp(os.path.join(this_path, 'image.jpg'))
	elif request.path_info == '/image/image.png':
		app = FileApp(os.path.join(this_path, 'image.png'))
	else: app = HTTPNotFound()
	return app(environ, start_response)


class ThumbsTestCase(unittest.TestCase):
	
	def setUp(self):
		self.cache_dir = tempfile.mkdtemp()
		self.app = Thumbs(test_app, self.cache_dir,
						{
							'small_crop': {'size': (100, 100), 'scale_method': 'crop', 'quality': 'png'},
							'large_crop': {'size': (300, 100), 'scale_method': 'crop'},
							'small_stretch': {'size': (100, 100), 'scale_method': 'stretch', 'quality': 80},
							'large_stretch': {'size': (500, 500), 'scale_method': 'stretch', 'quality': 80},
							'small_squash': {'size': (200, 500), 'scale_method': 'squash'},
							'large_squash': {'size': (500, 500), 'scale_method': 'squash'},
							'small_fit_stretch': {'size': (100, 100)},
							'large_fit_stretch': {'size': (500, 500)},
							'small_fit_squash': {'size': (200, 500), 'scale_method': 'fit_squash'},
							'large_fit_squash': {'size': (500, 500), 'scale_method': 'fit_squash'},
						})

	def tearDown(self):
		shutil.rmtree(self.cache_dir)

	def test_not_found(self):
		request = webob.Request.blank('/html/not_found.html')
		response = request.get_response(self.app)
		self.assertEqual(response.status, '404 Not Found')

	def test_not_image(self):
		request = webob.Request.blank('/html/index.html')
		response = request.get_response(self.app)
		self.assertTrue('Content-Type' in response.headers)
		self.assertEqual(response.headers['Content-Type'], 'text/html')

	def get_image(self, url, mime_type='image/jpeg'):
		request = webob.Request.blank(url)
		response = request.get_response(self.app)
		self.assertTrue('Content-Type' in response.headers)
		self.assertEqual(response.headers['Content-Type'], mime_type)
		data = response.app_iter
		if not hasattr(data, 'read'):
			data = StringIO(''.join(data))		
		return Image.open(data)

	def test_image(self):
		image = self.get_image('/image/image.jpg')
		self.assertEqual(image.size, (234, 327))
		
	def test_crop_image(self):
		image = self.get_image('/image/image.jpg?view=small_crop', 'image/png')
		self.assertEqual(image.size, (100, 100))
		image = self.get_image('/image/image.jpg?view=large_crop')
		self.assertEqual(image.size, (300, 100))

	def test_stretch_image(self):
		image = self.get_image('/image/image.jpg?view=small_stretch')
		self.assertEqual(image.size, (100, 100))
		image = self.get_image('/image/image.jpg?view=large_stretch')
		self.assertEqual(image.size, (500, 500))

	def test_squash_image(self):
		image = self.get_image('/image/image.jpg?view=small_squash')
		self.assertEqual(image.size, (200, 500))
		image = self.get_image('/image/image.jpg?view=large_squash')
		self.assertEqual(image.size, (234, 327))

	def test_fit_stretch_image(self):
		image = self.get_image('/image/image.jpg?view=small_fit_stretch')
		self.assertEqual(image.size, (71, 100))
		image = self.get_image('/image/image.jpg?view=large_fit_stretch')
		self.assertEqual(image.size, (357, 500))

	def test_fit_squash_image(self):
		image = self.get_image('/image/image.jpg?view=small_fit_squash')
		self.assertEqual(image.size, (200, 279))
		image = self.get_image('/image/image.jpg?view=large_fit_squash')
		self.assertEqual(image.size, (234, 327))

	def test_resize_image_bad_view(self):
		image = self.get_image('/image/image.jpg?view=bad')
		self.assertEqual(image.size, (234, 327))

	def test_cache(self):
		# Проверяем реакцию кэша на удаление оригинальной картинки
		self.test_fit_stretch_image()
		path = os.path.join(self.cache_dir, 'small_fit_stretch', 'image/image.jpg.jpg')
		self.assertTrue(os.path.isfile(path), u'Image not found in cache')
		request = webob.Request.blank('/image/image.jpg?view=small_fit_stretch&not_found=1')
		mtime = zope.datetime.rfc1123_date(long(os.stat(path).st_mtime))
		request.headers['If-Modified-Since'] = mtime
		response = request.get_response(self.app)
		self.assertEqual(response.status, '404 Not Found')
		self.assertFalse(os.path.isfile(path), u'Image found in cache. It`s not correct')


class MakeThumbsTestCase(unittest.TestCase):
	
	def setUp(self):
		self.cache_dir = tempfile.mkdtemp()
		sizes = '''
				small = 150x100
				small_str = 150x100,stretch,q80
				small_crop = 150x100,crop,qpng'''
		self.app = make_thumbs(test_app, None, cache_dir=self.cache_dir, sizes=sizes)

	def tearDown(self):
		shutil.rmtree(self.cache_dir)

	def test_make_thumbs(self):
		self.assertTrue('small' in self.app.sizes)
		self.assertTrue('small_str' in self.app.sizes)
		self.assertTrue('small_crop' in self.app.sizes)
		self.assertEqual(self.app.sizes['small'],
						{'size': (150, 100), 'scale_method': 'fit_stretch', 'quality': 75})
		self.assertEqual(self.app.sizes['small_str'],
						{'size': (150, 100), 'scale_method': 'stretch', 'quality': 80})
		self.assertEqual(self.app.sizes['small_crop'],
						{'size': (150, 100), 'scale_method': 'crop', 'quality': 'png'})


def test_suite():
	suite = unittest.TestSuite()
	suite.addTest(doctest.DocTestSuite('cykooz.thumbs.middleware',
                                    	optionflags=doctest.ELLIPSIS+
                                     	doctest.NORMALIZE_WHITESPACE))
	suite.addTest(unittest.makeSuite(ThumbsTestCase))
	suite.addTest(unittest.makeSuite(MakeThumbsTestCase))
	return suite


if __name__ == '__main__':
	test_suite()
	