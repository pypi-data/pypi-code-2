from socialtext.resources.base import Resource, Manager, get_id
from socialtext.urls import make_data_url

class User(Resource):
	def __repr__(self):
		return "<User: %s>" % self.get_id()

	def delete(self):
		raise NotImplementedError
	
	def get_id(self):
		"""
		Get the ID of this User.

		:rtype: str
		"""
		if hasattr(self, "user_id"):
			return self.user_id
		elif hasattr(self, "username"):
			return self.username
		return ""

	def is_member_of_account(self, account):
		"""
		Returns True if the user is a member of the provided account.

		:param account: The :class:`Account` (or ID of the Account) to check

		:rtype: bool
		"""
		account_id = get_id(account)
		for acct in self.accounts:
			if acct['account_id'] == account_id:
				return True
		return False

	def is_member_of_group(self, group):
		"""
		Returns True if the user is a member of the provided group.

		:param group: The :class:`Group` (or ID of the Group) to check

		:rtype: bool
		"""
		group_id = get_id(group)
		for group in self.groups:
			if group['group_id'] == group_id:
				return True
		return False

	
class UserManager(Manager):
	"""
	Manage :class:`User` resources.
	"""
	resource_class = User

	def list(self):
		"""
		Get a list of all users

		:rtype: list of :class:`User`.
		"""
		url = make_data_url('users')
		return self._list(url)

	def get(self, user):
		"""
		Get a specific user

		:param user: The :class:`User` (or ID of the User) to get.
		:rtype: :class:`User`
		"""
		url = make_data_url('user', arguments_dict={ 'user' : get_id(user) })
		return self._get(url)

	def create(self, *args, **kwargs):
		raise NotImplementedError

	def delete(self, user):
		raise NotImplementedError
