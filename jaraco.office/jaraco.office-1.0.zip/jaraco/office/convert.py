import os
import optparse
from contextlib import contextmanager
from jaraco.util.filesystem import save_to_file, replace_extension

@contextmanager
def word_context(word, filename, close_flags):
	doc = word.Documents.Open(filename)
	try:
		yield doc
	finally:
		doc.Close(close_flags)

class Converter(object):
	"""
	An object that will convert a Word-readable file to one of the Word-
	savable formats (defaults to PDF).
	
	Requires Microsoft Word 2007 or later.
	"""
	def __init__(self):
		from win32com.client import Dispatch
		import pythoncom
		import threading
		if threading.current_thread().getName() != 'MainThread':
			pythoncom.CoInitialize()
		self.word = Dispatch('Word.Application')

	def convert(self, docfile_string, target_format=None):
		"""
		Take a string (in memory) and return it as a string of the
		target format (also as a string in memory).
		"""
		from win32com.client import constants
		target_format = target_format or getattr(constants, 'wdFormatPDF', 17)

		with save_to_file(docfile_string) as docfile:
			# if I don't put a pdf extension on it, Word will
			pdffile = replace_extension('.pdf', docfile)
			dont_save = getattr(constants, 'wdDoNotSaveChanges', 0)
			with word_context(self.word, docfile, dont_save) as doc:
				res = doc.SaveAs(pdffile, target_format)
			with open(pdffile, 'rb') as pdf:
				content = pdf.read()
			os.remove(pdffile)
		return content

	__call__ = convert

	def __del__(self):
		self.word.Quit()

form = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml"
	xmlns:py="http://genshi.edgewall.org/"
	xmlns:xi="http://www.w3.org/2001/XInclude">
<head>
</head>
<body>
	<div>
		<form method="post" action="convert" enctype="multipart/form-data">
			<input type="file" name="document"/>
			<input type="submit" />
		</form>
	</div>
</body>
</html>"""

class ConvertServer(object):
	def index(self):
		return form
	index.exposed = True
 
	def convert(self, document):
		cherrypy.response.headers['Content-Type'] = 'application/pdf'
		return Converter().convert(document.file.read())
	convert.exposed = True

	@staticmethod
	def start_server():
		global cherrypy
		import cherrypy
		_, args = optparse.OptionParser().parse_args()
		config = None
		if args: config, = args
		cherrypy.quickstart(ConvertServer(), config=config)