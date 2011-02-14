import StringIO
from nose.tools import assert_equal, raises
from fakeserver import FakeServer
from utils import assert_isinstance
from socialtext import Signal

st = FakeServer()

def test_list_signals():
	sl = st.signals.list()

	st.assert_called('GET', '/data/signals')
	[assert_isinstance(s, Signal) for s in sl]

def test_get_signals():
	signal = st.signals.get(123)

	st.assert_called('GET', '/data/signals/123')
	assert_isinstance(signal, Signal)

	signal.get()
	st.assert_called('GET', '/data/signals/123')

def test_create_signal():
	body = "This is a signal!"
	in_reply_to = 121
	group_ids = [1, 2, 3]

	signal = st.signals.create(body, in_reply_to=in_reply_to, group_ids=group_ids)

	# The Socialtext API just returns headers
	# We force a GET call to retrieve the Signal
	st.assert_called('GET', '/data/signals/123')
	assert_isinstance(signal, Signal)

def test_delete_signals():
	signal = st.signals.get(123)

	signal.delete()
	st.assert_called('DELETE', '/data/signals/123')

	st.signals.delete(123)
	st.assert_called('DELETE', '/data/signals/123')

	st.signals.delete(signal)
	st.assert_called('DELETE', '/data/signals/123')

def test_get_mentioned_user_ids():
	# test signal mention
	body = "Hello {user: 123}!"
	signal = st.signals.load({"body": body})
	assert_equal(['123'], signal.get_mentioned_user_ids())

	# test multiple mentions
	body = "Hello {user: 123}, {user: 567}, and {user: 8910}!"
	signal.body = body
	expected = ['123', '567', '8910']
	assert_equal(expected, signal.get_mentioned_user_ids())


def test_is_user_mentioned():
	# User 123 is mentioned in this signal
	body = "Hello {user: 123}!"
	signal = st.signals.load({"body": body})
	assert_equal(True, signal.is_user_mentioned(123))

	# User 123 isn't mentioned in this signal
	signal.body = "Hello {user: 987}"
	assert_equal(False, signal.is_user_mentioned(123))