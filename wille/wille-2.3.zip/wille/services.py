"""Wille Services Module

Mostly used internally by Wille. However, a developer using
Wille may need to understand how Wille Service Definitions work.

Examples:

>>> import services 

Currently two types of services are supported:
	- Local services: executed locally, as specified in service adapter (see readme.txt)
	- HTTP services: executed over an HTTP API
	
Let's first see how local services work.

Initiating an instance of a local service:
>>> service = services.LocalService('../tests', 'upload_test', 'examples/libs')

Some metadata for services are available, such as parameter list:
>>> service.required_params
['raw_data', 'checksum']

Once instantiated, services can be executed with specified parameters:
>>> result = service.execute({'raw_data':'<h1>Hello World!</h1>', 'checksum': '1682'})

Result is return in ServiceData format. As an example, let's count length of returned data:
print(result.data)

"""

# Standard Python modules
import datetime
import os
import re
import sys
import httplib
import urllib
import urllib2
import email
import mimetypes
import imp
import time
import zipfile
import thread # Note: thread has been renamed to _thread in python 3
import pickle
import string
from urlparse import urlparse
import shutil
import traceback
from urllib import urlencode

# Load libraries that are not supported by IronPython
if sys.platform == 'cli':
	import ironsubprocess as subprocess
else:
	import subprocess

# Additional Python libs
import httplib2

import feedparser
try:
	import json
except:
	import simplejson as json
from pyjavaproperties import Properties

# Wille modules
from zipblob import Zipblob
import utils

ANY = None
DEFAULT_PROPERTIES_FILENAME = 'willeservice.properties'
SERVICE_STATUS_INITIALIZING = 'init'
SERVICE_STATUS_OK = 'ok'
SERVICE_STATUS_ERROR = 'error'

class InvalidArgumentException(Exception): pass

class ServiceData:
	"""ServiceData - either input or output"""
	def __init__(self, data, metadata):
		self.data = data
		self.metadata = metadata
		pass
	
	def get(self, key=None):
		if key is not None:
			return data[key]
		return data

	def success(self):
		"""Returns True/False based on whether this
		   instance contains a successful service result.
		   
		   If undetermined (such as for service input data),
		   returns None"""
		   		   
		# Undetermined -> None
		if not self.metadata.has_key('success'):			
			return None
		
		# Success
		if self.metadata['success']:
			return True
		
		# Otherwise False
		return False

class Service:
	"""Base class for all Wille services"""
	def __init__(self):
		self.properties = Properties()
		
	def __str__(self):
		return self.uri
	
	def __copy__(self):
		raise Exception("Abstract base class - __copy__ not implemented")

	def execute(self, params, servicepool=None, keyring=None):
		raise Exception("Abstract base class - execute not implemented")

class LocalService(Service):
	""" Local service """
	
	def __init__(self, parent_dir, subdir, libs_dir):
		# Debugging
		self.debug = False
		self.error_log = ''
		
		# Vars common to all services
		self.name = subdir.replace('/', '').replace('\\', '')
		self.pooltype = 'local'
		self.type = ''
		self.uri = None
		self.all_params = None
		self.required_params = None
		self.description = ''
		self.published = datetime.datetime.now()
		self.status = SERVICE_STATUS_INITIALIZING
		self.profiles = None
		
		# Define dirs
		self.parent_dir = parent_dir
		self.subdir = subdir
		self.relative_dir = os.path.join(parent_dir, subdir)
		self.absolute_dir = os.path.realpath(os.path.join(os.getcwd(), self.relative_dir))
		self.properties_filename = \
			os.path.realpath(\
				os.path.join(self.relative_dir, DEFAULT_PROPERTIES_FILENAME))
		self.libs_dir = libs_dir
		self.libs_dir_absolute = os.path.realpath(os.path.join(os.getcwd(), libs_dir))
		
		# Execution count
		self.exec_count = 0
		
		# Define uri
		self.uri = 'file://%s' % (self.absolute_dir)
		
		# Read and parse services.properties file
		self.reload()
		
	def status_ok(self):
		"""Is service status ok?""" 
		if self.status == SERVICE_STATUS_OK:
			return True
		return False
		
	def __copy__(self):
		"""Create a copy of this service instance (for rudimentary parallelism support)"""
		return LocalService(self.parent_dir, self.subdir, self.libs_dir)
	
	def reload(self):
		"""Reload service"""
		try:
			self.__load_properties()
		except Exception, e:
			self.status = SERVICE_STATUS_ERROR
			self.error_log = "%s\n" % e

	def __load_properties(self):
		self.properties = Properties()
		self.properties.load(open(self.properties_filename))
				
		# Extract the most frequently used properties
		self.type = self.properties['type']
		self.description = self.properties['description']
		
		# Profile
		if len(self.properties['profile']):
			self.profiles = self.properties['profile'].split(',')
		else:
			self.profiles = None
			
		# Parameters
		if self.properties['parameters']:
			all_params_raw = self.properties['parameters'].split(',')
			self.all_params = list()
			self.required_params = list()
			for param in all_params_raw:
				param_decoded = param.strip()
				if len(param_decoded) > 2:
					if param_decoded[0] == '(' and param_decoded[ - 1] == ')':
						# Not a required param
						param_decoded = param_decoded[1: - 1]
					else:
						self.required_params.append(param_decoded)
				else:
					self.required_params.append(param_decoded)
				self.all_params.append(param_decoded)
		self.status = SERVICE_STATUS_OK

	def __repr__(self):
		return "LocalWilleService(%s)" % self.name
		#return self.uri

	def __execute_http_get(self, parsedCommand, params, servicepool):		
		req = urllib2.Request(parsedCommand)
		response = urllib2.urlopen(req)
		data = response.read()
		metadata = dict()
		metadata['http'] = response		# TODO: http -> http_headers?
		metadata['code'] = response.code
		metadata['success'] = False
		if response.code == 200:
			metadata['success'] = True		
		return ServiceData(data, metadata)

	def __execute_commandline(self, parsedCommand, workdir, params, servicepool):
		if self.debug: sys.stderr.write("DEBUG: starting %s (@%s)\n" % (parsedCommand, workdir))
		
		output_stdout = ''
		output_stderr = ''
		try:
			p = subprocess.Popen(parsedCommand, shell=True, \
								 stdin=subprocess.PIPE, stdout=subprocess.PIPE, \
						 	 	 stderr=subprocess.STDOUT, cwd=workdir,
						 	 	 universal_newlines=False)
			(output_stdout, output_stderr) = p.communicate()
			retval = p.returncode
		except OSError, e:
			retval = - 1 # OS errors are considered as errors too
			if self.debug: sys.stderr.write("DEBUG: Got OSError -> setting retval to 1\n")
		if self.debug: sys.stderr.write("DEBUG: Exit code: %s\n" % retval)
		
		# Prepare outputs
		data = None
		metadata = dict()
		metadata['success'] = False
		
		# Was there an error?
		if retval != 0:
			if (self.properties['adapter.errors'] != 'ignore'):
				# Yes, please return an error
				if output_stderr is None: output_stderr = ''
				data = \
					"Command-line execution failed (return value=%s)\n%s%s" % \
					(retval, output_stderr, output_stdout)
				metadata['code'] = 500
				if self.debug: print(data)
				return ServiceData(data=data, metadata=metadata)
			else:
				# No, we are ignoring errors at the moment
				if self.debug: sys.stderr.write("DEBUG: Skipping error - adapter.errors was set to 'ignore'\n")
			
		# Init output code, type and format
		metadata['code'] = 200
		output_type = self.properties['adapter.output.type']
		metadata['format'] = 'text/plain'
		
		# Determine output encoding
		metadata['encoding'] = self.properties['adapter.output.encoding']
		if not metadata['encoding']:
			metadata['encoding'] = 'utf-8'
		
		# Determine output type and format based on it
		metadata['output_type'] = output_type 
		if output_type == 'stdout':
			data = output_stdout
		if output_type == 'stderr':
			data = output_stderr
		if output_type == 'file':
			outfile_name = os.path.join(workdir, self.properties['adapter.output'])
			try:
				outfile = open(outfile_name, 'rb')			
				data = outfile.read()
				outfile.close()
				del outfile
			except Exception, e:
				data = ''
				if output_stdout:
					data += output_stdout
				if output_stderr:
					data += output_stderr
				if self.debug: print("File not found: %s" % (outfile_name))
				metadata['code'] = 500
		if output_type == 'directory' or output_type == 'dir':
			output = self.properties['adapter.output']			
			if len(output) < 1:
				raise Exception("adapter.output not specified")
			output_dir = os.path.join(workdir, output)
			data = Zipblob()
			data.add_dir(output_dir)
			metadata['format'] = 'application/zip'
			
		# No output-type --> use stdout
		if data is None:
			data = output_stdout
		
		# A specific output format was enforced?
		metadata['format'] = self.properties['adapter.output.format']
		
		# Was execution success?
		if metadata['code'] == 200:
			metadata['success'] = True
	
		return ServiceData(data=data, metadata=metadata)

	def __execute_python(self, parsedCommand, workdir, params, servicepool, keyring):
		# Format in parsedCommand: "module.ServiceClassName"
		try:
			servicemodule_id, service_classname = parsedCommand.split('.')
		except ValueError, e:
			raise Exception("Invalid adapter command parameter: %s" % parsedCommand)
		
		# Register service dir as python module
		# TODO: Considering doing this only once per module (not once per execution)
		utils.register_python_module(self.parent_dir, self.subdir)
		
		# Find module
		try:
			f, filename, description = imp.find_module(servicemodule_id)
		except Exception, e:
			raise Exception("Execute python: could not load module %s" % servicemodule_id)
			
		# Load module
		try:
			servicemodule = imp.load_module(servicemodule_id, f, filename, description)
		except Exception, e:
			raise e
			#raise Exception("Execute python: could not load module %s" % servicemodule_id)
					
		# Instantiate service class (dynamic load)
		# Static equivalent for service_classname=MyService
		# would be: "srv = servicemodule.MyService()"
		srv = getattr(servicemodule, service_classname)()
		
		# Call service
		srv.debug = self.debug
		response = srv.execute(params, servicepool=servicepool, keyring=keyring, workdir=workdir)
		
		# Parse response based on response type
		result = ServiceData('', dict())
		
		# String response
		if type(response) == str:
			result.data = response
			result.metadata['code'] = 200
			result.metadata['format'] = 'text/html'
		
		# Tuple response
		if type(response) == tuple:
			# Data
			result.data = response[0]
			
			# Additional (HTTP) headers
			result.metadata['http_headers'] = response[1]
			
			# (HTTP) response code
			result.metadata['code'] = 200
			if len(response) > 2:
				result.metadata['code'] = response[2]

		return result
	
	def match_profile(self, match_profiles):
		# Any profile will do -> True
		if match_profiles == ANY or match_profiles == '' or match_profiles == 0:
			return True
		
		# Has no profile specified -> True
		if self.profiles == ANY:
			return True

		# Match n to n profiles
		for self_profile in self.profiles:			
			for match_profile in match_profiles:
				if self_profile == match_profile:
					return True
		return False
	
	def execute(self, params, servicepool=None, keyring=None):
		# Reload properties
		self.__load_properties()
		
		# Append Wille params to params:
		# _libs		- Wille libs absolute directory
		internal_params = list()
		internal_params.append('_libs')
		params['_libs'] = self.libs_dir_absolute
		
		# Add execution count statistic
		self.exec_count += 1
		
		adapter = self.properties['adapter']
		deprecated__adapter_class = self.properties['adapter.class']
		
		# Execute command-line adapter
		command = self.properties['adapter.command']

		# Set working directory
		workdir = self.absolute_dir # Own directory by default 

		# Adapter: Isolated command-line -- move all files to temporary location
		temp = None
		if adapter == 'IsolatedCommandLine':
			temp = utils.TempCopyFolder(self.absolute_dir)
			workdir = temp.dir
			
		# Parse command
		parsedCommand = command
		if self.all_params: # Parameters are parsed only of they are required
			for param in (self.all_params + internal_params):
				# ${} params = Pass content of parameter as string
				paramEncoding = '${%s}' % param
				if params is not None and params.has_key(param):
					if parsedCommand.find(paramEncoding) >= 0:
						parsedCommand = parsedCommand.replace(paramEncoding, params[param])
				else:
					# Parameter missing
					if self.required_params is not None:
						try:
							self.required_params.index(param)
							raise InvalidArgumentException("Missing parameter: %s" % param)
						except ValueError:
							# Replace with nothing if parameter is optional
							parsedCommand = parsedCommand.replace(paramEncoding, '')
					
				# @{} params = Write content of parameter to a file
				paramEncoding = '@{%s}' % param
				if params and params.has_key(param):
					#print("find: %s/%s -> %s" % (parsedCommand,paramEncoding,parsedCommand.find(paramEncoding)))
					if parsedCommand.find(paramEncoding) >= 0:
						# Replace encoding with parameter name
						parsedCommand = parsedCommand.replace(paramEncoding, param)
						pfile = open(os.path.join(workdir, param), 'wb')
						pfile.write(params[param]) #uploaded_filedata
						pfile.close()
						del pfile 
				else:
					# Parameter missing
					if self.required_params is not None:
						try:
							self.required_params.index(param)
							raise InvalidArgumentException("Missing parameter: %s" % param)
						except ValueError:
							# Replace with nothing if parameter is optional
							parsedCommand = parsedCommand.replace(paramEncoding, '')

		# Debugging help:
		if self.debug: print("DEBUG: Executing command:%s" % parsedCommand)
		
		# Adapter: HTTP/GET
		if adapter == 'HTTPGet':
			return self.__execute_http_get(parsedCommand, params, servicepool)
		
		# Adapter: Python Service
		if adapter == 'PythonService':
			return self.__execute_python(parsedCommand, workdir, params, servicepool, keyring)
		
		# Adapter: command-line
		if adapter == 'CommandLine':
			return self.__execute_commandline(parsedCommand, workdir, params, servicepool)
		
		# Adapter: isolated command-line
		if adapter == 'IsolatedCommandLine':
			try:			
				result = self.__execute_commandline(parsedCommand, workdir, params, servicepool)
			except:
				# Whatever happened, let's delete temp files and reraise exception
				if temp: del temp
				raise
			return result
			
		raise Exception("Unsupported adapter: %s (%s)" % (adapter, repr(adapter)))

class HTTPService(Service):
	""" HTTP Service """
	
	def __init__(self, url, name='', type=None, description='', all_params=None, required_params=None):
		self.uri = url
		self.name = name
		self.type = type
		self.all_params = all_params
		self.required_params = required_params
		self.description = description
		self.published = None
		self.exec_count = 0
		self.error_log = ''
		self.status = 'Unknown'
		self.pooltype = 'HTTP'
		
	def __copy__(self):
		"""Create a copy of this service instance (for rudimentary parallel exec support)"""
		return HTTPService(self.uri, self.name, self.type, self.description, self.all_params, self.required_params)
		
	def __repr__(self):
		return self.uri
	
	def reload(self):
		"""Reload service"""
		sys.stderr.write('Warning: HTTPService reloading not implemented\n')
		return True		

	def execute(self, params, servicepool=None, keyring=None):
		"""Executes an HTTP service. Will manage Zipblob results automatically."""
		
		# Create HTTP Request URL, body and headers
		
		# Capture call URL and split it
		url = self.uri
		url_parts = urlparse(url)
		url_protocol = url_parts[0]
		url_domain = url_parts[1]
		
		# List of output files
		filelist = []
		zipblob = Zipblob()
		
		# Determine whether to use GET or POST
		postRequired = False
		paramTotalLen = 0
		if params:
			for param in params:
				paramTotalLen += len(str(params[param]))
			
		if len(url) + paramTotalLen >= 1024: # Even larger value might be ok, but lets be fail-safe
			postRequired = True
			
		# Initiate new HTTP client and pass valid credentials to it
		http = httplib2.Http()		
		if keyring:
			# Username tokens
			for key in keyring.keys(type='UsernameToken', domain=url_domain):
				http.add_credentials(key.username, key.password)
				
		try:
			if postRequired:			
				body, headers = _encode_multipart_data(params, dict())
				response, content = http.request(url, "POST", headers=headers, body=body)					
			else:
				headers = {'Content-type': 'application/x-www-form-urlencoded'}
				body = ''
				if params:
					url = '%s?%s' % (url, urlencode(params))
				response, content = http.request(url, "GET", headers=headers, body=body)				
		except Exception, e:
			return ServiceData("HTTP service execution failed: %s" % e, {'success':False})
			
		# Prepare output data+metadata
		output = ServiceData(None, {})
		
		# Auto-detect content-type if not set
		if not response.has_key('content-type'):
			response['content-type'] = 'text/plain'
			
		# JSON support
		if response['content-type'][:len('application/json')] == 'application/json' or \
		   response['content-type'][:len('text/javascript')] == 'text/javascript':
			output.data = json.loads(content)
			
		# ZipBlob support
		if response['content-type'] == 'application/zip' or \
		   response['content-type'] == 'application/octet-stream':
			# Handling the multipart response
			msg = email.message_from_string(content)
			
			# Do we always have just one zip-based result? If not, adapt the following
			for part in msg.walk():			
				# multipart/* are just containers
				if part.get_content_maintype() == 'multipart':
					continue
				zipblob.write(part.get_payload(decode=True))
			output.data = zipblob
		
		# Support for all the rest
		if output.data is None:
			if response.get('content-length') or len(content):
				output.data = content
			else:
				output.data = ''
			
		# Attach HTTP-specific metadata
		output.metadata['http_response'] = response
		if response.status == 200:
			output.metadata['success'] = True
		else:
			output.metadata['success'] = False
		
		return output

# See recipe: http://stackoverflow.com/questions/68477/send-file-using-post-from-a-python-script
def _encode_multipart_data(data, files):
	boundary = utils.random_string(30)
	
   	def get_content_type (filename):
   		return mimetypes.guess_type (filename)[0] or 'application/octet-stream'
       
	def encode_field (field_name):
		return ('--' + boundary, \
           	    'Content-Disposition: form-data; name="%s"' % field_name, \
                   '', str (data [field_name]))
	def encode_file (field_name):
		filename = files [field_name]
        	return ('--' + boundary,
           	    'Content-Disposition: form-data; name="%s"; filename="%s"' % (field_name, filename),
                   'Content-Type: %s' % get_content_type(filename),
                   '', open (filename, 'rb').read ())
	lines = []
   	for name in data:
   		lines.extend (encode_field (name))
   	for name in files:
   		lines.extend (encode_file (name))
	lines.extend (('--%s--' % boundary, ''))
	body = '\r\n'.join (lines)
	headers = {'content-type': 'multipart/form-data; boundary=' + boundary, \
			   'content-length': str (len (body))}
	return body, headers

class ServicePool:
	""" Pool for services """
	def __init__(self):
		self.servicelist = {}
		self.type = None

	def services(self, name=ANY, type=ANY, uri=ANY, profile=ANY):
		"""Returns services in pool matching specified criteria.
		   At least one parameter must be specified
		   
			Parameters:
				name - Match service any (Default=ANY)
				type - Service type (Default=ANY)
				uri - Service URI (Default=ANY)
		"""
		raise Exception("Abstract Base Class")	

class LocalServicePool(ServicePool):
	""" Pool for local services """
	def __init__(self, services_dir, libs_dir):
		# Call super
		ServicePool.__init__(self)
		
		self.type = 'local'
		self.root_folder = services_dir
		self.error_log = ''

		folders = os.listdir(services_dir)
		for service_dir in folders:
			# Make full path
			service_fullpath = os.path.join( services_dir, service_dir )
			
			# Only add folders
			if os.path.isdir(service_fullpath):
				# Ignore folders starting with a dot (.)
				if service_dir[0] != '.':
					self.servicelist[service_dir] = LocalService(services_dir, service_dir, libs_dir)

	def services(self, name=ANY, type=ANY, uri=ANY, profile=ANY):
		results = list()
		for localname in self.servicelist:
			service = self.servicelist[localname]
			if type == ANY or service.type == type: 
				if uri == ANY or service.uri == uri:
					if name == ANY or service.name == name:
						if service.match_profile(profile):
							results.append(service)
		return results

class HTTPServicePool(ServicePool):
	""" Pool for HTTP Services """
	def __init__(self, server_url=None):
		# Call super
		ServicePool.__init__(self)
		self.type = 'http'
		self.feeds = dict()
		
		# Initial server connection
		if len(server_url) > 0:
			self.connect_to(server_url)
		else:
			server_url = None

	def __str__(self):
		return "HTTPPool(%s)" % self.server_url

	def connect_to(self, server_url):
		"""Connect/update connection to a server"""
		
		# Create services feed URL
		services_url = "%sservices/" % server_url
		if server_url[ - 1] == '/':
			server_url = server_url[0: - 1] 
		
		# Add to feeds
		d = feedparser.parse(services_url)
		try:
			link = d['feed']['link']
			self.feeds[link] = d
		except Exception, e:
			raise Exception("Not found: %s (%s)" % (services_url, e))			
		return True
	
	def __refresh_neighbors(self):
		# Refresh service data from neighbors
		for server_name in self.feeds:
			self.connect_to(server_name)
	
	def __match_feed_item(self, item, name=ANY, type=ANY, uri=ANY):
		if name is ANY or name == item['title']:
			if type is ANY or type == item['dc_type']:
				if uri is ANY or uri == item['link']:
					return True
	
	def services(self, name=ANY, type=ANY, uri=ANY, profile=ANY):
		"""Find services
		Arguments:
			type -- Match by type (Default=ANY)
		"""
		if profile != ANY:
			# @TODO: RSS profiles support
			print("Error: search by profiles not supported in HTTP services") 
		
		self.__refresh_neighbors() # Always start by reloading feeds
		results = list()		
		for feed_name in self.feeds:
			if len(self.feeds[feed_name]['entries']) > 0:
				for entry in self.feeds[feed_name]['entries']:
					if self.__match_feed_item(entry, name, type, uri):
						# Create HTTPService instance
						desc = ''
						if entry.has_key('dc_description'):
							desc = entry['dc_description']
						
						service = \
							HTTPService(\
								url=entry['link'],
								name=entry['title'],
								type=entry['dc_type'],
								description=desc,
								all_params='Unknown',
								required_params='Unknown')						
						results.append(service)
		return results

class GlobalServicePool(ServicePool):
	""" A collection of service pools """
	def __init__(self):
		# Call super
		ServicePool.__init__(self)
		self.type = 'global'
		self.servicepools = list()
		self.debug = False

	def __add_service_pool(self, servicepool):
		self.servicepools.append(servicepool)
		return True

	def load_dir(self, services_dir='services', libs_dir='libs'):
		pool = LocalServicePool(services_dir, libs_dir)
		self.__add_service_pool(pool)
	
	def load_url(self, server_url):
		pool = HTTPServicePool(server_url)
		return self.__add_service_pool(pool)

	def pools(self, pooltype=ANY):
		""" List pools """
		results = list()
		for pool in self.servicepools:
			if pooltype == ANY or pool.type == pooltype:
				results.append(pool)
		return results

	def execute_service(self, name=ANY, type=ANY, uri=ANY, params=None, \
					          keyring=None, profile=ANY, prefer_index=0):
		""" Run a service matching specified criteria
			Parameters:
				name - Service name (default=ANY)
				type - Service type (default=ANY)
				uri - Service uri (default=ANY)
				params - Service parameters as required by it (default=None)
				keyring - Keyring (default=None)
				prefer_index - In case several service match request, prefer this (nth) service (default=0)
				"""						
		pooltype = ANY

		if name == ANY and type == ANY and uri == ANY:
			raise Exception("You need to specify at least one criteria")
		
		# Direct HTTP execute
		if pooltype == ANY or pooltype == 'http':
			if uri is not ANY and (uri[0:7] == 'http://' or uri[0:8] == 'https://'):
				tmpHttpService = HTTPService(uri)
				tmpHttpService.debug = self.debug
				return tmpHttpService.execute(params, servicepool=self, keyring=keyring)
		
		# Pool search
		found_services = self.services(name=name, type=type, uri=uri, pooltype=pooltype, profile=profile)
		if not found_services:
			raise Exception("Service not found: name=%s,type=%s,uri=%s,pooltype=%s,profile=%s" % \
						    (name, type, uri, pooltype, profile))

		# Try to execute first found
		if self.debug:
			print("DEBUG: Number of redundant services: %s" % len(found_services))
		prefer_index = prefer_index % len(found_services) # Make sure prefer_index is always < len(found_services)
		first_service = found_services[prefer_index].__copy__() # Copy for parallel exec support
		first_service.debug = self.debug
		
		retries_left = 3
		retry_delay = 0.5
		while retries_left:
			first_service.debug = self.debug
			result = first_service.execute(params, servicepool=self, keyring=keyring)
			
			# Determine if this was success
			if result.metadata.has_key('success'):
				if result.metadata['success'] is True:
					break

			if result.metadata.has_key('code'):
				if str(result.metadata['code']) == '200':
					break

			# Sleep if using HTTP
			if first_service.pooltype == 'http':
				if self.debug:
					print("DEBUG: Service execution failed --> wait and retry (retries left: %s)" % (retries_left))
				time.sleep(retry_delay)
				
			retries_left -= 1
			retry_delay += 3
			
		return result

	def services(self, name=ANY, type=ANY, uri=ANY, pooltype=ANY, profile=ANY):
		""" Find services by specified criteria:"""
		results = list()
		for pool in self.servicepools:
			if pooltype == ANY or pool.type == pooltype:
				results_inner = pool.services(name=name, type=type, uri=uri, profile=profile)
				if results_inner:
					for result in results_inner:
						results.append(result)
		return sorted(results) # Return alphabetically sorted results

	def execute_services(self, service_descriptions, keyring=None):
		""" Executes a group of services. Parameters:
				service_descriptions - List of services to be executed. Each service is dict() with keys:
							name - Name of service to execute (None/ANY=not specified)
							type - Service type (None/ANY=not specified)
							uri - Service URI
							profile - Service profile
							params - Service parameters
				keyring - Keyring (optional)
					
				Note: minimum execution type 10 ms due use of polling
							
			Returns:
				List of service results on matching order  
		"""
		
		# Sequential execution
		results = list()
		for service_description in service_descriptions:
			service_description['keyring'] = keyring
			results.append(self.execute_service(**service_description))

		return results
		
		# Threaded implementation that doesn't work very well when used with commandline adapter:
		"""
		import thread
		self.results = dict()
		self.counter = 0
		self.counter_lock = thread.allocate_lock()		
		self.next_thread_id = 0
		for desc in service_descriptions:
			# Note: using next thread id as prefer_index (first service=index 0, etc.)
			self.counter_lock.acquire() # Add number of running threads
			self.counter += 1
			self.counter_lock.release()
			thread.start_new_thread( \
				self.__execute_service_parallel,\
				(desc, self.next_thread_id, self.next_thread_id) )
			self.next_thread_id += 1
			
		while self.counter > 0:
			time.sleep(0.01) # 0.01=10 ms = minimum execution time of this function 
		
		return self.results
		"""

	def __execute_service_parallel(self, args, thread_id, prefer_index):
		""" Protected method for executing a single service in a threaded """
		if not args.has_key('name'): args['name'] = ANY
		if not args.has_key('type'): args['type'] = ANY
		if not args.has_key('uri'): args['uri'] = ANY
		if not args.has_key('params'): args['params'] = dict()
		if not args.has_key('keyring'): args['keyring'] = None
		
		result = self.execute_service(name=args['name'], type=args['type'], uri=args['uri'], \
									  params=args['params'], keyring=args['keyring'], \
									  prefer_index=prefer_index)
		
		self.counter_lock.acquire() # Diminish number of running threads and insert results
		self.counter -= 1
		self.results[thread_id] = result
		self.counter_lock.release()		

# Run tests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
