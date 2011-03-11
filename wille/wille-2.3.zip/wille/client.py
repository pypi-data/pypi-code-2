"""Wille Client Module

Using Wille Client.

Firstly, import it:

>>> import client

Instantiate a client:

>>> client = client.Client()

If we want to use local services, we need to tell client where they are:

>>> client.load_dir('../tests')

See what services we found from local folder:

>>> client.services()
[LocalWilleService(timeout_test), LocalWilleService(data), LocalWilleService(stub), LocalWilleService(upload_test)]

Services can be searched by their name:

>>> client.services(name='stub')
[LocalWilleService(stub)]

Services can be also search by their type:

>>> client.services(type='test')
[LocalWilleService(timeout_test), LocalWilleService(upload_test)]

Similarly, services can be executed (note that we need to prepare parameters):

>>> params = {'raw_data': file('../tests/data/data.txt','rb').read(), 'checksum': '525'}

>>> result = client.execute_service(name='upload_test',params=params)

You can also run a group of services. First we need to prepare
a service description for every unique service/data combination:

>>> desc1 = {'name': 'upload_test', 'params': params}

Pass a list of these descriptions to grouped service execution

>>> results = client.execute_services([desc1,desc1,])

Results are available in a dictionary, indexed in the order they were given as arguments:

>>> results[0].data
'OK - checksum match (525)\\r\\n'

>>> results[1].data
'OK - checksum match (525)\\r\\n'

Hint: You can turn on debugging mode in Wille client by setting debug:

>>> client.debug = True

"""

import os
import auth
import services
import time

from services import GlobalServicePool

ANY = None

class Client:
	""" Wille Client
	
		Parameters (all optional):
		
				servicepool - Servicepool (default=None, recommended)
				
				keyring - Init with given keyring
				
				debug - Enable debug mode
				
				profiles - Enable only given profiles (default=all enabled)
				
				userdata_dir = Directory to store user/session data
	"""
	
	def __init__(self, servicepool=None, keyring=None, debug=False, profiles=None, \
				       userdata_dir=None):
		
		# Servicepool
		if servicepool:
			self.servicepool = servicepool
		else:
			self.servicepool = GlobalServicePool()
			
		self.debug = debug
		self.servicepool.debug = self.debug
		self.profiles = profiles
		
		# Userdata dir
		self.userdata_dir = None		
		self.__open_userdata_dir(userdata_dir)
		
		# Keyring
		if keyring:
			self.keyring = keyring
		else:
			# No keyring given -> load default
			self.keyring = auth.Keyring()
			self.load_keyring()
		self.keyring.debug = self.debug
		
	def __open_userdata_dir(self, userdata_dir):
		self.userdata_dir = userdata_dir
		if userdata_dir is None or len(userdata_dir)<1:
			self.userdata_dir = None
			return False
		 
		if not os.path.exists(userdata_dir):
			os.mkdir(userdata_dir)
			if self.debug:
				print("Created new userdata directory: %s" % userdata_dir)
		 
		if self.debug:
			print("Wille.client.Client: using data directory: %s" % self.userdata_dir)
		return True
		
	def load_dir(self, services_dir='../services', libs_dir=None):
		""" Load services from given directory (with given libs directory) """
		
		if libs_dir is None:
			libs_dir = os.path.realpath( os.path.join(services_dir, '../libs') )
		return self.servicepool.load_dir(services_dir, libs_dir)
	
	def load_url(self, server_url):
		return self.servicepool.load_url(server_url)
	
	def load_keyring(self, filename=None):
		""" Load keyring (optionally from given file)"""
		if self.userdata_dir is None:
			if self.debug:
				print("Wille.Client: Could not load keyring: userdata_dir was not specified!")
			return False			 
		if filename is None:
			filename = os.path.join(self.userdata_dir, auth.KEYRING_DEFAULT_FILENAME)			
		self.keyring_filename = filename
		return self.keyring.load(self.keyring_filename)
	
	def save_keyring(self):
		""" Save keyring """
		
		if self.keyring_filename:
			self.keyring.save(filename=self.keyring_filename)
		else:
			raise Exception('Keyring filename not specified')
			 
	def services(self, name=ANY, type=ANY, uri=ANY, pooltype=ANY):
		""" Find services """
		return self.servicepool.services(name, type, uri, pooltype, profile=self.profiles)

	def execute_service(self, name=ANY, type=ANY, uri=ANY, params=None, prefer_index=0):
		""" Execute a service by given description """
		return self.servicepool.execute_service(name, type, uri, params, self.keyring, self.profiles, prefer_index)

	def execute_services(self, service_descriptions):
		""" Execute multiple services by given descriptions """
		return self.servicepool.execute_services(service_descriptions, self.keyring)

	def launch_viewer(self, type='webbrowser', location=''):
		"""Launch viewer. Parameters:
			type - Type of the viewer:
						webbrowser - Launch system's web browser
			location - Location/arguments to pass to the viewer """
			
		# Try to launch webbrowser
		if type=='webbrowser':
			try:
				import webbrowser
				webbrowser.open(location,new=0)
			except:
				# Not supported (especially in Jython) - provide manual instructions instead
				print("Your python's runtime environment doesn't support web browser launching")
				print("To launch the browser manually, please enter the following URL to a browser manually:")
				print("")
				print(location)
				print("")
		else:
			raise Exception("Unsupported viewer type")
			
		return

# Run tests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
