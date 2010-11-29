"""
Google Apps authentication plugin for Trac
@author: David A. Riggs <david.riggs@createtank.com>
"""

from trac.core import *
from trac.config import Option

from acct_mgr.api import IPasswordStore
from trac.perm import IPermissionGroupProvider

import gdata.apps.service
import gdata.apps.groups.service
from gdata.service import BadAuthentication, CaptchaRequired
from gdata.apps.service import AppsForYourDomainException


class GoogleAppsPasswordStore(Component):
	
	implements(IPasswordStore, IPermissionGroupProvider)
	
	# Plugin Options
	opt_key = 'google_apps'
	gapps_domain = Option(opt_key, 'domain', None, """Domain name of the Google Apps domain""")
	gapps_admin_username = Option(opt_key, 'admin_username', None, """Username or email with Google Apps admin access""")
	gapps_admin_secret = Option(opt_key, 'admin_secret', None, """Password for Google Apps admin account""")
	
	def __init__(self):
		self.env.log.debug('GoogleAppsPasswordStore.__init__()')
		self.env.log.debug('domain: %s\tadmin_username: %s\tadmin_secret: %s' % (self.gapps_domain, self.gapps_admin_username, len(self.gapps_admin_secret)*'*'))
		db = self.env.get_db_cnx()

		self.group_cache = {'anonymous':[],}
	
	def _get_admin_email(self):
		if self.gapps_admin_username.find('@') > -1:
			email = self.gapps_admin_username
		else:
			email = '%s@%s' % (self.gapps_admin_username, self.gapps_domain)
		return email
	
	def _get_apps_service(self):
		"""Build instance of gdata AppsService ready for ProgrammaticLogin()"""
		email = self._get_admin_email()
		return gdata.apps.service.AppsService(email=email, domain=self.gapps_domain, password=self.gapps_admin_secret)
	
	def _get_groups_service(self):
		"""Build instance of gdata GroupsService ready for ProgrammaticLogin()"""
		email = self._get_admin_email()
		return gdata.apps.groups.service.GroupsService(email=email, domain=self.gapps_domain, password=self.gapps_admin_secret)
		
	# IPasswordStore API
	
	def get_users(self):
		"""Returns an iterable of the known usernames."""
		self.log.debug('get_users')
		service = self._get_apps_service()
		service.ProgrammaticLogin()
		gapps_user_feed = service.RetrieveAllUsers()
		users = map(lambda x: x.login.user_name, gapps_user_feed.entry)
		return users

	def has_user(self, user):
		"""Returns whether the user account exists."""
		self.log.debug('has_user(%s)' % (user))
		return user in self.get_users()

	def has_email(self, address):
		"""Returns whether a user account with that email address exists."""
		self.log.debug('has_email(%s)' % (address))
		user = address.split('@')[0]
		return user in self.get_users() 

	def set_password(self, user, password, old_password=None):
		"""Sets the password for the user.  This should create the user account
		if it doesn't already exist.
		Returns True if a new account was created, False if an existing account
		was updated.
		"""
		self.log.debug('set_password(%s): NOT IMPLEMENTED' % (user))
		return None # TODO

	def check_password(self, user, password):
		"""Checks if the password is valid for the user.
	
		Returns True if the correct user and password are specfied.  Returns
		False if the incorrect password was specified.  Returns None if the
		user doesn't exist in this password store.

		Note: Returing `False` is an active rejection of the login attempt.
		Return None to let the auth fall through to the next store in the
		chain.
		"""
		self.log.debug('check_password(%s, %s)' % (user, len(password)*'*'))
		
		if user.find('@') > -1:
			email = user
		else:
			email = '%s@%s' % (user, self.gapps_domain)
		
		service = self._get_apps_service()
		try:
			service.ClientLogin(email, password, account_type='HOSTED', source='createtank-googleauthtracplugin-1.0') # email?
			return True
		except BadAuthentication as e:
			self.log.debug(e)
			return False
		except CaptchaRequired as e:
			self.log.debug(e) # yikes?!
			return False
		
		return None # ?

	def delete_user(self, user):
		"""Deletes the user account.
		Returns True if the account existed and was deleted, False otherwise.
		"""
		self.log.debug('delete_user(%s): NOT IMPLEMENTED' % (user))
		return False

	# IPermissionGroupProvider API

	def get_permission_groups(self, username):
		"""Return a list of names of the groups that the user with the specified name is a member of."""
		self.log.debug('get_permission_groups(%s)' % (username))
		
		groups = []
		if self.group_cache.has_key(username):
			self.log.debug('returning cached groups for user: '+username)
			groups = self.group_cache[username]
		else:
			self.log.debug('groups not cached, requesting from Google Apps for user: '+username)
			service = self._get_groups_service()
			try:
				service.ProgrammaticLogin()
				groups_feed = service.RetrieveGroups(username, False)
				groups = map(lambda x: x['groupName'], groups_feed)
		
				self.group_cache[username] = groups
			except AppsForYourDomainException as e:
				self.log.debug(e)
				groups = []
			
		self.log.debug(groups)
		return groups
		