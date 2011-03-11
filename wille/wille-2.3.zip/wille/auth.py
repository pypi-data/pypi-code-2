"""Authentication Keyring Module

Provides facilities for managing different user credentials
(Username and API keys, etc.) and can be used as such for automatic user
authentication and authorisation. Auth can be extended to support arbitrary
token types.

Using auth:

Firstly, import auth package:

>>> import auth 

Initialize new keyring by invoking:

>>> my_keys = auth.Keyring()

Different types of authentication "keys" can be added. Scope of the keys
may be also defined by setting a domain in which the key is valid.

An example of adding a username token e.g. for HTTPBasic authentication

>>> my_keys.add_token_username('johndoe', 'mypassword', domain='www.example.com')

An example of adding a generic API key:

>>> my_keys.add_token_apikey('A1B2C3D4E5', domain='api.example.com')

Keys with specified criteria can be retrieved by invoking keys() method:

>>> a_key = my_keys.keys()[0]

>>> a_key.username
'johndoe'

>>> a_key.password
'mypassword'

>>> a_key.match_domain('www.example.com')
True

>>> a_key.match_domain('www.example.org')
False

"""

import pickle
from urlparse import urlparse
from itertools import repeat

# Default filename for keyring
KEYRING_DEFAULT_FILENAME = 'default.keyring'

# Domain wildcard match
DOMAIN_ANY=None

class Token:
	""" Token """
	def __init__(self, domain=DOMAIN_ANY):
		self.domain = domain

	def match_domain(self, domain):
		"""Does this token match a given domain?
		
			Test cases:
			
			Import Token model:
			
			>>> from auth import Token
			
			Create test token:
			
			>>> t = Token(domain='example.com')
			
			Direct match:
			
			>>> t.match_domain('example.com')
			True
		
			Doesn't match:
			
			>>> t.match_domain('example.org')
			False
			
			Matches a subdomain:
			
			>>> t.match_domain('api.example.com')
			True
			
			Subdomain matches, but domain doesn't:
			
			>>> t.match_domain('api.example.org')
			False

			Spoof #1: Domain name in pathname
			
			>>> t.match_domain('api.example.org/example.com')
			False

			Spoof #2: Domain name as a urlencoded argument
			
			>>> t.match_domain('api.example.org/?url=example.com')
			False

			Spoof #3: Domain name in subdomain
			
			>>> t.match_domain('example.com.spoof')
			False
			
			Token is valid for several domains:
			
			>>> t2 = Token(domain=['example.com', 'example.org'])
			
			Try first:
			
			>>> t2.match_domain('example.com')
			True

			Try second:
			
			>>> t2.match_domain('example.org')
			True
			
			Try something that should not work
			
			>>> t2.match_domain('example.biz')
			False

			Create token for a specific location within a domain
			
			>>> t3 = Token(domain='example.com/api')
			
			Try matching location:
			
			>>> t3.match_domain('example.com/api/callback')
			True

			Try invalid location:
			
			>>> t3.match_domain('example.org/api')
			False
			
			Create token valid only for a specific port:
			
			>>> t4 = Token('example.com:1234')

			>>> t4.match_domain('example.com')
			False
			
			>>> t4.match_domain('example.com:1234')
			True
			
			
			"""
				
		# If any match is valid then return already
		if domain is DOMAIN_ANY or self.domain is DOMAIN_ANY:
			return True
		
		# They are equals
		if self.domain == domain:
			return True
		
		# Parse hostname
		domain_parsed = urlparse(domain)
		hostname_parsed = domain_parsed[1]
		
		# Limit hostname to minimum required match
		if len(domain_parsed[1])==0 and len(domain_parsed[2])>1:
			hostname_parsed = domain_parsed[2].split('/')[0]
			
		# Match string
		if type(self.domain)==str:
			find_expected = len(hostname_parsed)-len(self.domain)
			if hostname_parsed.find(self.domain) == find_expected:
				return True
			else:
				# If lenght is same or not subdir is contained, it is not a match 
				if self.domain.find('/') < 0 or len(self.domain)==len(domain):
					return False
				
				# Required match could still be shorter and hence, match
				if domain[0:len(self.domain)]==self.domain:
					return True
				 
				return False
		
		# Match list of strings
		for domain_item in self.domain:
			if hostname_parsed.find(domain_item) >= 0:
				return True 				
				
		return False

class UsernameToken(Token):
	"""Ordinary username + password token
		Parameters:
			username
			password (optional)
			domain (optional) 
			"""
	def __init__(self, username, password=None, domain=DOMAIN_ANY):
		self.username = username
		self.password = password		
		self.domain = domain
		
	def __str__(self):
		return "<UsernameToken(%s/%s) for %s>" % (self.username, self.password, self.domain)
		
class APIKeyToken(Token):
	"""Generic API key token
		Parameters:
			api_key
			secret (optional)
			domain (optional) 
			"""
	def __init__(self, api_key, secret=None, domain=DOMAIN_ANY):
		self.api_key = api_key
		self.secret = secret
		self.domain = domain
		
	def __str__(self):
		return "<APIKeyToken(%s/%s) for %s>" % (self.api_key, self.secret, self.domain)

class Keyring:
	"""Keyring is used to manage a set of tokens
	"""
	def __init__(self, filename=None):
		"""Initialize a keyring, and optionally load it from a file"""
		self.__keys = list()
		
		self.filename = filename
		if filename:
			self.load(filename)
	
	def load(self, filename):
		"""Merge tokens from file to the keyring"""
		# Unpickle
		try:
			file = open(filename, 'rb')
		except:
			return False
		keyring = pickle.load(file)
		
		# Merge to keyring		
		for key in keyring.__keys:
			self.add_token(key)
			
		return True

	def save(self, filename):
		"""Save keyring to a file"""
		
		f = open(filename, 'wb')
		f.write(pickle.dumps(self))
		f.close()
				
	def add_token(self, token):
		"""Generic method for adding new token to the keyring
		
			Parameters:
				token - Token to add
		"""
		# Check for duplicates
		for key in self.__keys:
			if str(key) == str(token):
				return 
			
		# If none, append
		self.__keys.append(token)
		
	def add_token_username(self, name, password=None, domain=DOMAIN_ANY):
		"""Convenience method for adding username token to the keyring
		
			Parameters:
				name - Name/username
				password - Password (optional)
				domain - Domain for which the username token is valid (e.g. api.example.com)				
		"""
		
		return self.add_token( UsernameToken(name, password, domain) )

	def add_token_apikey(self, api_key, secret='', domain=DOMAIN_ANY):
		"""Convenience method for adding API key token to the keyring
		
			Parameters:
				api_key - Actual API key, preferrably as a string
				secret - Secret value (optional)
				domain - Domain for which API key is valid (e.g. api.example.com)				
				"""
		return self.add_token( APIKeyToken(api_key, secret, domain) )

	def keys(self, type=None, domain=DOMAIN_ANY):
		"""Find keys by specified criteria. Finds all by defaul
		
			Parameters:
				type - Returns only keys of a given type
					   Specified as string of the key class name
					   (examples: 'UsernameToken', 'APIKeyToken'
				domain - Return only keys that match the given domain
				       """
		results = []
		for key in self.__keys:
			# Filter by type
			class_suffix = str(key.__class__).split('.')[-1]
			if type is None or type==class_suffix:
				if key.match_domain(domain):
					results.append(key)
		return results

# Run tests
if __name__ == "__main__":
    import doctest
    doctest.testmod()
