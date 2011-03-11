import sys; sys.path.append('..')

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import thread, sys

# Config and constants
debug = False
VALID_RESPONSE = 'GET+HTTP Basic OK'

# Test calling services over HTTP
from wille.client import Client
cl = Client()

# Set up a test server
class TestServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path=='/':
			self.send_response(200)
			self.end_headers()
			self.wfile.write('GET OK')
			return
		
		if self.path=='/httpbasic':
			# Calculate valid username/password base64
			import base64
			base64_valid = base64.encodestring('%s:%s' % ('validusername', 'validpassword'))[:-1]
			
			# Parse given Authorization
			try:				
				base64_user_raw = self.headers.getfirstmatchingheader('authorization').pop().strip()
				base64_user = base64_user_raw.split('Basic ')[1]
			except:
				base64_user = ''
				
			if base64_user!=base64_valid:
				self.send_response(401)
				self.wfile.write('WWW-Authenticate: Basic realm="localhost"\n')
				self.end_headers()				
				return
			
			self.send_response(200)
			self.end_headers()
			self.wfile.write( VALID_RESPONSE )
			return
		
		self.send_response(500)
		return
	
	def do_POST(self):
		self.send_response(200)
		self.end_headers()
		self.wfile.write('POST OK')
		return
	
	def log_message(self, format, *args):
		pass

# Start server (and run on background)
if debug: print("Starting server")
httpd = HTTPServer(('', 8080), TestServerHandler)
server_thread = thread.start_new_thread(httpd.serve_forever,())

# Simple HTTP GET from localhost
if debug: print("HTTP GET")
resp = cl.execute_service(uri='http://localhost:8080/')
assert( resp.data == 'GET OK' )

# HTTP GET with HTTP Basic Authentication
if debug: print("HTTP GET + Basic Auth")
cl.keyring.add_token_username('validusername', 'validpassword', 'localhost:8080')
resp = cl.execute_service(uri='http://localhost:8080/httpbasic')
assert( resp.data == VALID_RESPONSE )

# HTTP GET with HTTP Basic Authentication and 2 invalid usernames/passwords (1 of each)
if debug: print("HTTP GET + multichoice Basic Auth")
cl2 = Client()
cl2.keyring.add_token_username('invalidusername', 'validpassword', 'localhost:8080/httpbasic')
cl2.keyring.add_token_username('validusername', 'invalidpassword', 'localhost:8080/httpbasic')
cl2.keyring.add_token_username('validusername', 'validpassword', 'localhost:8080')
assert( cl2.execute_service(uri='http://localhost:8080/httpbasic').data == VALID_RESPONSE )

# Batch service execution with HTTP GET + Basic
if debug: print("Batch HTTP GET + multichoice Basic Auth")
descriptions = ( \
	{'uri': 'http://localhost:8080/httpbasic'}, \
	{'uri': 'http://localhost:8080/httpbasic'}, \
	{'uri': 'http://localhost:8080/httpbasic'}, \
)
results = cl2.execute_services(descriptions)
assert( results[0].data == VALID_RESPONSE )
assert( results[1].data == VALID_RESPONSE )
assert( results[2].data == VALID_RESPONSE )

# Cleanup
if debug: print("All done - cleanup...")
sys.exit(0)
