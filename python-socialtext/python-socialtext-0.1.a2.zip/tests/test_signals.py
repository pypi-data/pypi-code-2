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
    
    query = {
        "accounts": [1,2,3],
        "groups": [1,2,3],
        "order": st.signals.ORDER_DATE,
        "direction": st.signals.DIRECTION_DESC,
        "following" : '1',
        "limit": '25', # urllib.urlencode turns numbers into strings
    }
    
    sl = st.signals.list(**query)
    # we don't compare query equality in this case
    # the data_get_signals method on the TestServer
    # will check for required & optional query keys
    st.assert_called('GET', '/data/signals')

@raises(ValueError) 
def test_list_signals_invalid_direction():
    st.signals.list(direction="foo")
    
@raises(ValueError)
def test_list_signals_invalid_direct():
    st.signals.list(direct="foo")
    
@raises(ValueError)
def test_list_signals_invalid_order():
    st.signals.list(direct="foo")

def test_get_signals():
    signal = st.signals.get(123)

    st.assert_called('GET', '/data/signals/123')
    assert_isinstance(signal, Signal)

    signal.get()
    st.assert_called('GET', '/data/signals/123')

def test_create_signal():
    body = "This is a signal!"
    in_reply_to = 121
    recipient = 1
    accounts = [1, 2, 3]
    group_ids = [1, 2, 3]
    annotations = [
        {
            "type1": { "attr1": "value1", "attr2": "value2"},
        },
        {
            "type2": { "attr1": "value1", "attr2": "value2"},
        }
    ]

    signal = st.signals.create(body, accounts=accounts, annotations=annotations,
        in_reply_to=in_reply_to, groups=group_ids, recipient=1)

    
    in_reply_to = "annotations:foo|bar|123"

    signal = st.signals.create(body, accounts=accounts, annotations=annotations,
        in_reply_to=in_reply_to, groups=group_ids, recipient=1)

    # The Socialtext API just returns headers
    # We force a GET call to retrieve the Signal
    st.assert_called('GET', '/data/signals/123')
    assert_isinstance(signal, Signal)
    
@raises(ValueError)
def test_create_signal_with_annotations_with_multiple_outer_keys():
    body = "This is a bad signal"
    
    # annotations with the outer dictionaries having more than one key.
    annotations = [
        {
            "type1": { "attr1": "value1" }, 
            "type2": { "attr1": "value1" },
            
        }
    ]
    
    st.signals.create(body, annotations=annotations)
    
@raises(ValueError)
def test_create_signal_with_annotation_attributes_not_dict():
    body = "This is a bad signal!"
    
    # annotations where the attributes value is not of type dict
    annotations = [
        { "type1": [] }
    ]
    
    st.signals.create(body, annotations=annotations)

@raises(ValueError)
def test_create_signal_with_invalid_recipient():
    recipient = "joe@example.com"
    signal = st.signals.create("This should fail", recipient=recipient)

def test_delete_signals():
    signal = st.signals.get(123)

    signal.delete()
    st.assert_called('DELETE', '/data/signals/123')

    st.signals.delete(123)
    st.assert_called('DELETE', '/data/signals/123')

    st.signals.delete(signal)
    st.assert_called('DELETE', '/data/signals/123')

def test_hide_signals():
    signal = st.signals.get(123)

    signal.hide()
    st.assert_called('PUT', '/data/signals/123/hidden')

    st.signals.hide(123)
    st.assert_called('PUT', '/data/signals/123/hidden')

    st.signals.hide(signal)
    st.assert_called('PUT', '/data/signals/123/hidden')

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