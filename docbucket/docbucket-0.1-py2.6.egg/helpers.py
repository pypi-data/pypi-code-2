#!/usr/bin/env python
#coding=utf8
#
#       Copyright 2010 Antoine Millet <antoine@inaps.org>
#
#       This file is part of DocBucket.
#       
#       Foobar is free software: you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation, either version 3 of the License, or
#       (at your option) any later version.
#       
#       Foobar is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

from models import DocumentClass
from django.conf import settings

import os
from StringIO import StringIO
from tempfile import mktemp
from subprocess import Popen
from PIL import Image

def list_document_classes():
	return tuple(((dc.slug, dc.name) for dc 
	               in DocumentClass.objects.order_by('name')))

def list_incomings():
	''' Return the all the relevant files contained in incoming 
		directory. '''
	
	indir = settings.INCOMING_DIRECTORY
	
	files = ((f, f) for f 
	         in os.listdir(settings.INCOMING_DIRECTORY)
	         if os.path.isfile(os.path.join(indir, f))
	         and os.path.splitext(f)[1] in settings.INCOMING_EXTS)

	return tuple(files)

def assemble(filenames):
	''' Assemble files. '''
	
	outputs = {}
	pdfs = []
	
	for filename in filenames:
		absfilename = os.path.join(settings.INCOMING_DIRECTORY, filename)
		
		hocr_filename = mktemp(suffix='.html')
		text_filename = mktemp(suffix='.txt')
		pdf_filename = mktemp(suffix='.pdf')
		
		# Launch hocr file creation:
		opts = {'input': absfilename, 'output': hocr_filename}
		if Popen(settings.HOCR_CMD % opts, shell=True).wait() != 0:
			raise Exception('Error while hocr')
		
		# Launch text file creation:
		opts = {'input': absfilename, 'output': text_filename}
		if Popen(settings.TEXT_CMD % opts, shell=True).wait() != 0:
			raise Exception('Error while text')
		
		# Launch pdf creation:
		opts = {'input_img': absfilename, 'output': pdf_filename,
		        'input_hocr': hocr_filename}
		print settings.HOCR2PDF_CMD % opts
		if Popen(settings.HOCR2PDF_CMD % opts, shell=True).wait() != 0:
			raise Exception('Error while hocr2pdf')
		
		text = open(text_filename, 'r').read().decode('utf-8', 'ignore').encode('utf-8')
		outputs[filename.replace('.', '_')] = text
		pdfs.append(pdf_filename)
	
	# Finally, assemble all pdfs:
	complete_pdf_filename = mktemp(suffix='.pdf')
	opts = {'inputs': ' '.join(pdfs), 'output': complete_pdf_filename}
	if Popen(settings.ASSEMBLE_CMD % opts, shell=True).wait() != 0:
		raise Exception('Error while assemble')

	return (complete_pdf_filename, outputs)

def make_thumbnails(filename):
	image = Image.open(filename)
	thumbnails = {}
	
	for name, size in settings.THUMBNAILS_SIZES.iteritems():
		thumb = image.copy()
		thumb.thumbnail(size, Image.ANTIALIAS)
		thumb_file = StringIO()
		thumb.save(thumb_file, format='PNG')
		thumb_file.seek(0)
		thumbnails[name] = thumb_file
	
	return thumbnails
