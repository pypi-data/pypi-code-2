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

from cykooz.thumbs.middleware import Thumbs

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
							'small': {'size': (100, 100), 'params': [], 'quality': 75},
							'small_str': {'size': (100, 100), 'params': ['scale_stretch'], 'quality': 75},
							'small_crop': {'size': (100, 100), 'params': ['crop'], 'quality': 'png'},
							'large': {'size': (500, 500), 'params': [], 'quality': 75}
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
		
	def test_resize_image_small(self):
		image = self.get_image('/image/image.jpg?view=small')
		self.assertEqual(image.size, (71, 100))

	def test_resize_image_stretch(self):
		image = self.get_image('/image/image.jpg?view=small_str')
		self.assertEqual(image.size, (100, 100))

	def test_resize_image_crop(self):
		image = self.get_image('/image/image.jpg?view=small_crop', 'image/png')
		self.assertEqual(image.size, (100, 100))

	def test_resize_image_large(self):
		image = self.get_image('/image/image.jpg?view=large')
		self.assertEqual(image.size, (357, 500))

	def test_resize_image_bad_view(self):
		image = self.get_image('/image/image.jpg?view=bad')
		self.assertEqual(image.size, (234, 327))

	def test_cache(self):
		# Проверяем реакцию кэша на удаление оригинальной картинки
		self.test_resize_image_small()
		path = os.path.join(self.cache_dir, 'small', 'image/image.jpg.jpg')
		self.assertTrue(os.path.isfile(path), u'Image not found in cache')
		request = webob.Request.blank('/image/image.jpg?view=small&not_found=1')
		mtime = zope.datetime.rfc1123_date(long(os.stat(path).st_mtime))
		request.headers['If-Modified-Since'] = mtime
		response = request.get_response(self.app)
		self.assertEqual(response.status, '404 Not Found')
		self.assertFalse(os.path.isfile(path), u'Image found in cache. It`s not correct')

def test_suite():
	suite = unittest.TestSuite()
	suite.addTest(doctest.DocTestSuite('cykooz.thumbs.middleware',
                                    	optionflags=doctest.ELLIPSIS+
                                     	doctest.NORMALIZE_WHITESPACE))
	suite.addTest(unittest.makeSuite(ThumbsTestCase))
	return suite


if __name__ == '__main__':
	test_suite()
	