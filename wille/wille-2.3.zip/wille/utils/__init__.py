"""utils - Utility methods

Deprecation warning: these utility methods and modules are provided only for
convience of Wille development. 

For copyright information and licensing, see LICENSE.txt
"""

import datetime
import decimal
import os, sys, mimetypes
import urllib
import random, string
import tempfile
import shutil
import time
from os.path import join, splitext, split, exists
import simplejson

ENCODING_FALLBACK_CHARSET = 'utf-8'

def fileshare_make_response(shared_path, filename):
	# Headers
	headers = {}
		
	# Headers: content-length
	statinfo = os.stat(os.path.join(shared_path, filename))
	headers['Content-Length'] = statinfo.st_size
		
	# Headers: content-type
	mimetype = mimetypes.guess_type(filename)[0]
	headers['Content-type'] = mimetype
		
	# Data
	data = fileshare_read_file_safe(shared_path, filename)
	
	# Full response
	return (data, headers, 200)

def fileshare_read_file_safe(shared_path, filename):
	"""Safe way for reading and returning given file
	   Parameters:
	   shared_dir - Directory from which file is served
	   filename - Filename under the given directory		
	"""
				
	# Normalise path
	filepath = os.path.join(shared_path, filename)
	realpath = os.path.realpath(filepath)
	realroot = os.path.realpath(shared_path)
		
	# Safety check: filepath must be under shared_dir
	if realpath[:len(realroot)] != realroot:
		raise ValueError("Trying to access file outside shared path")
		
	f = open(filepath, 'rb')
	data = f.read()
	f.close()
	return data

def random_string(length):
	"""Generate random string (from letters) of given length""" 
	return ''.join([random.choice(string.letters) for i in range (length + 1)])

def __copytree_with_ignores__(source, target):
	if not os.path.exists(target):
		os.mkdir(target)
	for root, dirs, files in os.walk(source):
		if '.svn' in dirs: dirs.remove('.svn')  # don't visit .svn directories           
		for file in files:
			#if splitext(file)[-1] in ('.pyc', '.pyo', '.fs'): continue
			from_ = join(root, file)           
			to_ = from_.replace(source, target, 1)
			to_directory = split(to_)[0]
			if not exists(to_directory):
				os.makedirs(to_directory)
            
			shutil.copy(from_, to_)			

class TempCopyFolder:
	"""Creates a temporary copy from specified folder that is
	   deleted automatically on garbage-collection"""
	def __init__(self, source, debug=False):
		self.dir = tempfile.mkdtemp(prefix='wille_')
		self.debug = debug
		try:
			__copytree_with_ignores__(source, self.dir)
		except Exception, e:
			if self.debug:
				 print("Copytree failed. Exception: %s" % e) 
			self.__del__()
			raise e
			
		# Note: In Python 2.6 we could use shutil.copytree with ignores:
		# 	shutil.copytree(self.absolute_dir,tempdir_service,symlinks=False)
		if self.debug:
			print("Created tempFolder %s" % self.dir) 		
		
	def __del__(self):
		if self.debug:
			print("DEBUG: Removing tempFolder %s" % self.dir)
		try:
			shutil.rmtree(self.dir) # Remove entire temp dir
			if self.debug:
				print("------ Done removing")
		except:
			if self.debug:
				print("------ Failed removing %s (file blocked by a process?)" % self.dir)
			pass

class Reloader:
	"""Checks to see if any loaded modules have changed on disk and, 
	if so, reloads them.
	    
	Function has been taken from web.py <http://webpy.org> version 0.33
	by Anand Chitipothu, made available under Public domain. Modifications have
	been made for Wille.       
	"""
	def __init__(self):
		self.mtimes = {}

	def call(self):
		for mod in sys.modules.values():
			self.check(mod)
            
	def check(self, mod):		
		try: 
			mtime = os.stat(mod.__file__).st_mtime
		except (AttributeError, OSError, IOError):
			return
		if mod.__file__.endswith('.pyc') and os.path.exists(mod.__file__[:-1]):
			mtime = max(os.stat(mod.__file__[:-1]).st_mtime, mtime)

		if mod not in self.mtimes:
			self.mtimes[mod] = mtime
		elif self.mtimes[mod] < mtime:
			try:
				reload(mod)
				self.mtimes[mod] = mtime
			except ImportError: 
				pass

def register_python_module(root_dir, module_dir):
	"""Utility function for registering given location as a python module.
	
	   Returns: True if new module was added
	            False if module was already registered and
	                  doesn't need to be readded"""
		
	# Construct full path
	full_path = os.path.join(root_dir, module_dir)

	# Check for duplicates
	for location in sys.path:
		if location is full_path:
			return False

	# Not found -> append to path
	sys.path.append(full_path)
		
	return True

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

class DjangoJSONEncoder(simplejson.JSONEncoder):
    """                                                                             
                                                                          
    JSONEncoder subclass that knows how to encode date/time and decimal types.      
                                                                          
    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        elif isinstance(o, datetime.date):
            return o.strftime(self.DATE_FORMAT)
        elif isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        elif isinstance(o, decimal.Decimal):
            return str(o)
        else:
            return super(DjangoJSONEncoder, self).default(o)

def jsonEncode( obj ):
    return simplejson.dumps( obj, indent=4, default=DjangoJSONEncoder().default )

def jsonDecode( text ):
    try:
        obj = simplejson.loads( text, parse_float=decimal.Decimal )
    except:
        print("Failed to decode text as JSON: '%s'" % text)
        return None
    else:
        return obj

# Run tests
if __name__ == "__main__":
    import doctest
    doctest.testmod()

def metadata_to_http_headers(metadata):
	"""Send headers based on given metadata"""
		
	# Default headers
	headers = {}
		
	# Parse content-type from format + encoding
	try:
		format = metadata['format']
	except KeyError:
		# Use text/plain as a fallback
		# TODO: Make this fallback mimetype configurable
		format = 'text/plain'
	try:
		encoding = metadata['encoding']
	except KeyError:
		# Use specified fallback for encoding
		encoding = ENCODING_FALLBACK_CHARSET
	headers['Content-type'] = '%s; charset=%s' % (format, encoding)
		
	# Retrieve extra headers from http_headers
	if metadata.has_key('http_headers'):
		for header in metadata['http_headers']:
			headers[header] = metadata['http_headers'][header]
			
	# TODO: Note that find is not fool proof
	if headers['Content-type'].find('charset=') == -1:
		headers['Content-type'] += '; charset=%s' % (encoding)
				
	return headers
