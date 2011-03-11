"""Wille Server Module

Using Wille Server.

Let's start by importing Wille server:

>>> import server

Instantiate a server with some customisations:

>>> server = server.Server(services_dir='examples/services', apps_dir=None, server_port=80, quiet=True)

Once services are loaded and everything is otherwise ok, let's run the server

>>> server.run(background=True)

Now, take a look at your HTTP server, at http://localhost:port/

When finished, press Ctrl+C to kill the server

"""
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import cgi
import re
import os
import sys
import threading
import thread
import urlparse
import string
import socket
import traceback
import time
import utils
from exceptions import KeyboardInterrupt

# Wille
import app
import services
import client
import memorystore
from utils import Reloader
import utils.template as template
from views import Frontpage, AppList, ServiceList, ServiceExecute, Management, SharedFilesView
from app import App

#
# Settings
#

# Fallback charset (used when charset cannot be detected)
ENCODING_FALLBACK_CHARSET = 'utf-8'

# Slow response threshold (in seconds)
SLOW_RESPONSE_THRESHOLD		=	10

class WilleHTTPRequestHandler(BaseHTTPRequestHandler):
	"""Map requests according to specified URL patterns"""

	def datastore(self, key=None):
		"""Acquire access to memory datastore
		   If key is specified, retrieves content from that key"""
		store = memorystore.get_handler(self.server.server_port)		
		if key is None:
			return store
		return store.get(key)
		
	def wille_client(self):
		"""Get an instance of local wille client"""
		
		if hasattr(self, 'wille_client_instance')==False:
			o = self.datastore('client')              # ... here
			self.wille_client_instance = client.Client(o.servicepool, o.keyring, o.debug, profiles=o.profiles, userdata_dir=o.userdata_dir)
		return self.wille_client_instance
	
	def input(self, varname=None, default=None):
		"""Parse input data. Parameters:
			varname - Get only selected variable (None=get all variables in a dict)
			default - Default value (returned if variable not found)			
		"""

		# Parse input
		self.__parse_input()
			
		# Handle this function
		if varname:
			if self.__vars.has_key(varname):
				return self.__vars[varname]
			else:
				return default
		return self.__vars
	
	def __parse_input(self):
		# Try if input has been parsed already
		try:
			self.__vars
			return
		except:
			# Not parsed -> parse
			self.__vars = dict()
			
			# Parse query string
			request_url = self.requestline.split(' ')[1]
			pattern = r'^[^\?]+\?([^#]*)'
			qs_match = re.match(pattern,request_url)
			if qs_match:
				qs=qs_match.group(1)
				parsed_qs = cgi.parse_qs(qs)
				for key in parsed_qs:
					self.__vars[key] = parsed_qs[key][0] # Put GET data to vars
			else:
				parsed_qs = dict()
			
			# Parse POST data
			if self.headers.dict.has_key('content-length') and \
		   	   string.lower(self.headers.dict['content-type']).startswith('application/x-www-form-urlencoded'):
				content_length = string.atoi(self.headers.dict['content-length'])
				self.__vars = cgi.parse_qs(self.rfile.read(content_length)) # Put POST data to vars
			else:
				if self.headers.dict.has_key('content-length'):
					ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
					if ctype == 'multipart/form-data':
						post_data=cgi.parse_multipart(self.rfile, pdict) # Put POST data to vars
						for key in post_data:
							self.__vars[key] = post_data[key][0]
		return
		
	def __process_request(self, command):
		"""Processes a request"""

		# Hard-code urls
		urls = self.datastore('urls')
		
		# Deny request by default
		permitted = False
		
		# Determine if access is permitted to the client
		server_visibility = self.datastore('server_visibility')
		
		# Enabled profiles
		profiles = self.datastore('profiles')
		
		# Match public
		if server_visibility[0] == 'public':
			permitted = True
		
		# Match localhost
		if self.client_address[0]=='127.0.0.1' or \
		   self.client_address[0]==self.datastore('hostname'):
			permitted = True # Access is permitted always for localhost/public
			
		# Match by list (IP + public)
		if type(server_visibility)=="list":
			for ip in ip_list:
				if len(ip)>0:
					if ip == self.client_address[0]:
						permitted = True
			
		# If permitted, map to given request
		if permitted:		
			return self.__map_request(command,urls)
		
		# Access is denied
		self.send_error(401)
		return
	
	def match_path(self, path, urls):
		"""Match path against given set of URL+handler tuples"""
		for rule in urls:
			str_pattern = '^'+rule[0]+'(\?.*)?$'
			match = re.match(str_pattern,path)
			if match:
				return rule, match
		return None, None

	def __map_request(self, command, urls):
		"""Send request to matching handler"""
		
		# Retrieve apps from datastore
		apps = self.datastore('apps')
		
		# Call reloader (if enabled)
		if self.datastore('reloader'):
			# Reload changed code
			self.datastore('reloader_instance').call()			

			# Reload all apps			
			for appname in apps:
				apps[appname].reload()
		
		# Match request against given URL patterns
		rule, match = self.match_path(self.path, urls)
		if match:
			# Prepare arguments
			args = [self,]
			for arg in match.groups()[:-1]:
				args.append(arg)
				
			# Set matched rule
			self.rule = rule
				
			# Set working directory
			if len(rule)>=3:
				self.workdir = rule[2]
			else:
				self.workdir = '.' # Unknown workdir
				
			time_start = time.time()
			try:
				# If we called an app, make it available to the request handler
				self.app = None
				for app in apps:
					app_pattern = '^/apps/%s/(.*)$' % app
					#print "DEBUG -- re.match(%s,%s)" % (app_pattern, self.path)
					if re.match(app_pattern, self.path):
						#print "MATCH: %s against %s" % (self.path, app_pattern) 
						self.app = apps[app]
						break
				
				# Get method attribute (GET,POST,HEAD,etc.) from handler and execute it
				message = getattr( rule[1](), command )(*args)
				
				# Extract headers from tuple, if present
				headers = {}
				if type(message)==tuple:
					# Send response
					response_code = 200
					if len(message)>2:
						response_code = message[2]
					self.send_response(response_code)
					
					# Send headers
					if len(message)>1:
						headers = message[1]
						for header in headers:
							self.send_header(header, headers[header])
							
					self.end_headers()
					
					# Extract data to message
					data = message[0]
				else:
					data = message
					
				# Unicode to string (use encoding specified in headers
				if type(data)==unicode:
					encoding = ENCODING_FALLBACK_CHARSET
					if headers.has_key('Content-type'):
						items = headers['Content-type'].split(';')
						for item in items:
							parts = item.split('=')
							if len(parts)>1:
								key = parts[0].strip()
								value = parts[1].strip()
								if key == 'charset':						
									encoding = value
										
					if self.datastore('debug'):
						print("Encoding %s bytes with %s" % (len(data), encoding))
					data = data.encode(encoding)
				
				# Write out string response
				if type(data)==str:
					self.wfile.write( str(data) )
				else:
					self.wfile.write("Unknown data type (%s) -- expecting unicode/str" % type(data))
					
			except Exception, e:					
				try:
					# Try sending an error
					self.send_error(500, str(e))
				finally:
					# Print stack trace if error was sent successfully (in debug mode)
					if self.datastore('debug'):	
						print ("Error: %s" % e)						
						traceback.print_exc(file=sys.stderr)
				return
				
			time_end = time.time()
			time_delta = time_end-time_start
			if time_delta > SLOW_RESPONSE_THRESHOLD:
				if not self.datastore('quiet'):
					sys.stderr.write("Warning: slow response (%s s) to %s\n" % (int(time_delta), self.path))

		# Not found error
		#self.send_error(404)
		return
	
	def log_message(self, format, *args):
		if self.datastore('quiet'): return
		BaseHTTPRequestHandler.log_message(self, format, *args)
	
	def do_OPTIONS(self): return self.__process_request('OPTIONS')
	def do_GET(self): return self.__process_request('GET')
	def do_HEAD(self): return self.__process_request('HEAD')	
	def do_POST(self): return self.__process_request('POST')
	def do_PUT(self): return self.__process_request('PUT')
	def do_DELETE(self): return self.__process_request('DELETE')
	def do_TRACE(self): return self.__process_request('TRACE')
	def do_CONNECT(self): return self.__process_request('CONNECT')

class StoppableHTTPServer(HTTPServer):
	""" A stoppable HTTP server """
	request_queue_size=100
	quiet=False
		
	def server_bind(self):
		HTTPServer.server_bind(self)
		self.socket.settimeout(1)
		self.run = True

	def get_request(self):
		while self.run:
			try:
				sock, addr = self.socket.accept()
				sock.settimeout(None)
				return (sock, addr)
			except socket.timeout:				
				time.sleep(0.1) # Sleep for some time in case of a socket timeout

	def stop(self):
		self.run = False

	def serve(self):
		while self.run:
			self.handle_request()

class ThreadedStoppableHTTPServer(ThreadingMixIn, StoppableHTTPServer):
	"""Handle requests in a separate thread."""		  
	# Dev note:
	#	Using ForkingMixIn instead of ThreadingMixIn would use
	#   processes instead of threads (if that was desirable)

server_default_urls = [
	("/management/", Management),
	("/services/(.*)/", ServiceExecute),
	("/services/", ServiceList),
	("/apps/", AppList),
	("/shared/(.*)", SharedFilesView),
	("/", Frontpage),
]

class Server:
	""" Wille Server """
	def __init__(self, server_port=8080, server_visibility='localhost',\
					   services_dir='services', apps_dir='apps', wille_root_dir='.',
					   userdata_dir='data', profiles='', neighbour_urls=list(), quiet=False, debug=False,
					   reloader=False):
		"""Initiate new server instance.
				Parameters:
		   			server_port - Port in which servers will be ran
		   			server_visibility - Server visibility (default=localhost)
		   			services_dir - Directory from which services are automatically loaded.
		   						   Convenience argument for loading a directory of services  
		   			apps_dir - Directory from which all apps are automatically loaded.
		   					   Convenience argument for register_apps_dir
					wille_root_dir - Wille root directory (=project root dir)
					profiles - Profiles
					neighbour_urls - List of neighbouring Wille nodes
					quiet - Quiet operation
					debug - Debug mode
		   			"""
		self.services_dir = services_dir
		self.server_port = int(server_port)
		self.server_visibility = server_visibility
		self.background_thread = None
		self.httpd = None
		self.running = False
		self.quiet = quiet
		self.debug = debug
		self.reloader = reloader
		self.userdata_dir = userdata_dir
		
		# Wille root dir
		if not wille_root_dir or len(wille_root_dir) == 0:
			wille_root_dir = os.path.realpath('.')
		if not self.quiet: print ('Wille root dir: %s' % wille_root_dir)		
		
		# Initiate memory store
		self.store = memorystore.get_handler(server_port)
		
		# Profiles
		self.profiles = None
		if len(profiles)>0:
			self.profiles = profiles.split(',')
		if not self.quiet: print ('Profiles enabled: %s' % (self.profiles))
		
		# Data directory
		if not self.quiet: print ('Using data directory: %s' % self.userdata_dir)
		
		# Initiate client
		self.wille_client = client.Client(debug=self.debug, profiles=self.profiles, userdata_dir=self.userdata_dir)
		
		# There may be multiple service dirs
		services_dir_list = services_dir.split(';')
		if not self.quiet: print ('Loading services from %s' % (services_dir_list))
		for dir in services_dir_list:
			try:
				self.wille_client.load_dir(dir) # Load services
			except Exception, e:
				if not self.quiet: print (e)
				
			if type(neighbour_urls)==str:
				neighbour_urls = list(neighbour_urls,)
			for neighbour_url in neighbour_urls:
				if len(neighbour_url)>0:
					self.wille_client.load_url(neighbour_url)
													
		# Update memorystore
		self.store.update('client', self.wille_client)
		self.store.update('hostname', self.resolve_ip())
		self.store.update('port', server_port)
		self.store.update('server_visibility', self.server_visibility)
		self.store.update('profiles', self.profiles)
		self.store.update('wille_root_dir', wille_root_dir)
		self.store.update('apps', dict())
		self.store.update('apps_dir', apps_dir)
		self.store.update('urls', server_default_urls) # Assign default URLs
		self.store.update('quiet', self.quiet)
		self.store.update('debug', self.debug)
		self.store.update('reloader', self.reloader)

		# Load apps (to self.store)
		if not self.quiet: print ('Loading apps from "%s"' % (apps_dir))
		if apps_dir:
			self.register_apps_dir(apps_dir)

	def resolve_url(self):
		"""Resolves server's URL"""
		return "http://%s:%s/" % (self.resolve_ip(), self.server_port)
	
	def resolve_app_url(self, appname):
		"""Resolves apps URL"""
		return "%sapps/%s/" % (self.resolve_url(), appname)
		
	def resolve_ip(self, interface_hostname = None):
		"""Resolves server's public IP"""
		# give the hostname of the interface you want the ipaddr of
		hostname = interface_hostname or socket.gethostname()
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind((hostname, 0))
		ipaddr, port = s.getsockname()
		s.close()
		return ipaddr  # returns 'nnn.nnn.nnn.nnn' (StringType)
	
	def register_app(self, apps_dir, appname):
		"""Register specified app to server
				Parameters:
					path - path to app 
					appname - a name for serving the app
					urls - List of URLs with corresponding callback classes"""						   
		if self.running:
			raise Exception("Couldn't register new app; server is already running")
		
		self.apps = self.store.get('apps')
		
		# Create new App
		try:
			thisapp = app.App(name=appname, path=apps_dir)
			self.apps[appname] = thisapp
		except Exception, e:
			if self.debug:
				print ("Failed registering App %s: %s\n----" % (appname, e))
				traceback.print_exc(file=sys.stderr)
				print ("")
			return False
		
		# Register app to sever
		self.store.update('apps',self.apps)
		
		# Register new urls to server (begin/commit for thread-safety)
		try:
			self.store.begin()
			server_url = self.store.get('urls')
			try:
				for url in thisapp.urls:
					# Make urls relative to appname and append to server_urls
					parsed_url = ( ('/apps/%s%s' % (appname, url[0])), url[1], (apps_dir+'/'+appname) ) + url[2:]
					server_url.append(parsed_url)
			except Exception, e:
				if not self.quiet:
					print ("Warning: failed loading app %s: %s" % e)
		finally:	
			# Rollback is not supported so now we just basically commit every time
			self.store.commit()
		
		return True
	
	def register_apps_dir(self, apps_dir):
		"""Register all apps from specified directory"""
		
		try:
			app_folders = os.listdir(apps_dir)
			for appname in app_folders:
				try:
					self.register_app(apps_dir, appname)
				except Exception, e:
					if not self.quiet: print(e)
		except Exception, e:
			if not self.quiet: print (e)
			return False
						
		return True
				
	def run(self, background=True, multi_thread=True):
		"""Start the server
				Parameters:
					background - Run in background? (default=True)
					multi_thread - Use multithreaded server to serve
								   multiple concurrent requests (default=True)
					quiet - Quiet operation - avoids printing to console (default=True)
		"""
		if not self.quiet:
			print( 'Starting server to port %s, URL %s' % \
				    (self.server_port, self.resolve_url()) )
			print( 'Server visibility: %s' % (self.server_visibility) )

		# Generate hostname from IP
		self.hostname = self.resolve_ip()
		
		# Server address
		self.server_address = ''

		# Workaround for IronPython exception:
		# (ValueError: IPv4 address 0.0.0.0 and IPv6 address
		#  ::0 are unspecified addresses that cannot be used as a target address.)
		if sys.platform == 'cli':
			#self.server_address = 'localhost'
			self.server_address = '%s' % self.hostname

		# Start server (single/multi-thread)
		if multi_thread:
			self.httpd = ThreadedStoppableHTTPServer((self.server_address, self.server_port), WilleHTTPRequestHandler)
		else:
			self.httpd = StoppableHTTPServer((self.server_address, self.server_port), WilleHTTPRequestHandler)
			
		# Convey server's global settings
		self.httpd.quiet = self.quiet
		self.httpd.debug = self.debug
		
		# Hook reloader
		self.store.update('reloader_instance', utils.Reloader())

		if background:
			self.background_thread = thread.start_new_thread(self.httpd.serve_forever,())
			self.running = True
		else:		
			try:
				self.httpd.serve_forever()
			except KeyboardInterrupt:
				pass
			self.httpd.server_close()
			if not self.quiet:
				print('Stopping server')
