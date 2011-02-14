import StringIO
from nose.tools import assert_equal, raises
from fakeserver import FakeServer
from utils import assert_isinstance
from socialtext import User

st = FakeServer()

def test_list_users():
	ul = st.users.list()

	st.assert_called('GET', '/data/users')
	[assert_isinstance(u, User) for u in ul]

def test_get_users():
	user = st.users.get(123)
	st.assert_called('GET', '/data/users/123')
	assert_isinstance(user, User)

	user.get()
	st.assert_called('GET', '/data/users/123')

	user = st.users.get(user)
	st.assert_called('GET', '/data/users/123')

def test_is_member_of_account():
	accounts = [{ "account_id": "123"}, {"account_id": "987"}]
	user = st.users.load({"accounts": accounts})
	assert_equal(True, user.is_member_of_account("123"))
	assert_equal(True, user.is_member_of_account("987"))
	assert_equal(False, user.is_member_of_account("1000"))

def test_is_member_of_group():
	groups = [{ "group_id": "123"}, {"group_id": "987"}]
	user = st.users.load({"groups": groups})
	assert_equal(True, user.is_member_of_group("123"))
	assert_equal(True, user.is_member_of_group("987"))
	assert_equal(False, user.is_member_of_group("1000"))

@raises(NotImplementedError)
def test_create_user():
	st.users.create()

@raises(NotImplementedError)
def test_delete_users():
	st.users.delete(123)