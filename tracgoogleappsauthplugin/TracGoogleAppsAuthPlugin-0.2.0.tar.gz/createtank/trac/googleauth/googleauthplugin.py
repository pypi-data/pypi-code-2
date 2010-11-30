"""
Google Apps authentication plugin for Trac
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
	"""TracAccountManager Password Store which authenticates against a Google Apps domain"""
	
	implements(IPasswordStore, IPermissionGroupProvider)
	
	# Plugin Options
	opt_key = 'google_apps'
	gapps_domain = Option(opt_key, 'domain', '', """Domain name of the Google Apps domain""")
	gapps_admin_username = Option(opt_key, 'admin_username', '', """Username or email with Google Apps admin access""")
	gapps_admin_secret = Option(opt_key, 'admin_secret', '', """Password for Google Apps admin account""")
	gapps_group_access = Option(opt_key, 'group_access', '', """Optional Google Apps Group which is exclusively granted access to this Trac site""")
	
	def __init__(self):
		self.env.log.debug('GoogleAppsPasswordStore.__init__()')
		self.env.log.debug('domain: %s\tadmin_username: %s\tadmin_secret: %s\tgroup_access: %s' % (self.gapps_domain, self.gapps_admin_username, len(self.gapps_admin_secret)*'*', self.gapps_group_access))
		#db = self.env.get_db_cnx()

		self.group_cache = {'anonymous':[],}
	
	def _validate(self):
		"""Validate that the plugin is configured correctly"""
		return self.gapps_domain and self.gapps_admin_username and self.gapps_admin_secret
	
	def _get_user_email(self, username):
		if username.find('@') > -1:
			email = username
		else:
			email = '%s@%s' % (username, self.gapps_domain)
		return email

	def _get_admin_email(self):
		return self._get_user_email(self.gapps_admin_username)
	
	def _get_apps_service(self):
		"""Build instance of gdata AppsService ready for ProgrammaticLogin()"""
		email = self._get_admin_email()
		return gdata.apps.service.AppsService(email=email, domain=self.gapps_domain, password=self.gapps_admin_secret)
	
	def _get_groups_service(self):
		"""Build instance of gdata GroupsService ready for ProgrammaticLogin()"""
		email = self._get_admin_email()
		return gdata.apps.groups.service.GroupsService(email=email, domain=self.gapps_domain, password=self.gapps_admin_secret)
	
	def _get_all_users(self):
		service = self._get_apps_service()
		service.ProgrammaticLogin()
		gapps_users_feed = service.RetrieveAllUsers()
		users = map(lambda x: x.login.user_name, gapps_users_feed.entry)
		return users
	
	def _get_all_users_in_group(self, group, suspended_users=True):
		service = self._get_groups_service()
		service.ProgrammaticLogin()
		gapps_users_feed = service.RetrieveAllMembers(group, suspended_users)
		self.log.debug(gapps_users_feed)  # DEBUG
		emails = map(lambda x: x['memberId'], gapps_users_feed)  # yuck, Groups service gives us email addresses instead of usernames
		emails = filter(lambda x: x.endswith(self.gapps_domain), emails)  # toss out members outside our domain
		users = map(lambda x: x.split('@')[0], emails)
		return users
	
	
	# IPasswordStore API
	
	def get_users(self):
		"""Returns an iterable of the known usernames."""
		self.log.debug('get_users')
		if not self._validate():
			self.log.debug('Plugin validation failed (check config!), falling through.')
			return []
		
		if self.gapps_group_access:
			self.log.debug('Restricting user list to members of group "%s".' % (self.gapps_group_access))
			return self._get_all_users_in_group(self.gapps_group_access)
		else:
			return self._get_all_users()

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
		if not self._validate():
			self.log.debug('Plugin validation failed (check config!), falling through.')
			return None
		
		# This should allow the use of multiple PasswordStore implementations at the expense of making the login process slower...
		#if user not in self.get_users():
		#	self.log.debug('User "%s" is not one of our users, Google Apps plugin falling through.' % (user))
		#	return None
		
		email = self._get_user_email(user)		
		service = self._get_apps_service()
		try:
			service.ClientLogin(email, password, account_type='HOSTED', source='createtank-tracgoogleappsauthplugin-0.2')
			if self.group_cache.has_key(user):
				self.log.debug('Flushing group cache for user "%s".' % (user))
				del self.group_cache[user]
			return True
		except BadAuthentication, e:
			self.log.debug(e)
			return False
		except CaptchaRequired, e:
			self.log.debug(e) # yikes?!
			return False
		
		return None # ?

	def delete_user(self, user):
		"""Deletes the user account.
		Returns True if the account existed and was deleted, False otherwise.
		"""
		self.log.debug('delete_user(%s): NOT IMPLEMENTED' % (user))
		return False

	def config_key(self):
		"""'''Deprecated'''
		Returns a string used to identify this implementation in the config.
		This password storage implementation will be used if the value of
		the config property "account-manager.password_format" matches.
		This implementation uses the key 'googleappsauthplugin'.
		"""
		return 'googleappsauthplugin'


	# IPermissionGroupProvider API

	def get_permission_groups(self, username):
		"""Return a list of names of the groups that the user with the specified name is a member of."""
		self.log.debug('get_permission_groups(%s)' % (username))
		
		if username == 'anonymous':
			self.log.debug('This plugin does not authenticate anonymous user.')
			return []
		
		if not self._validate():
			self.log.debug('Plugin validation failed (check config!), falling through.')
			return []

		
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
			except AppsForYourDomainException, e:
				self.log.debug(e)
				groups = []
			
		self.log.debug(groups)
		return groups
		