import StringIO
from nose.tools import assert_equal, raises
from fakeserver import FakeServer
from utils import assert_isinstance
from socialtext import Workspace

st = FakeServer()

def test_list_workspaces():
	wl = st.workspaces.list()
	st.assert_called('GET', '/data/workspaces')
	[assert_isinstance(w, Workspace) for w in wl]

def test_get_workspaces():
	ws = st.workspaces.get(123)
	st.assert_called('GET', '/data/workspaces/123')

	ws = st.workspaces.get('marketing')
	st.assert_called('GET', '/data/workspaces/marketing')

	assert_isinstance(ws, Workspace)
	assert_equal(123, ws.id)
	assert_equal('marketing', ws.name)

	ws.get()
	st.assert_called('GET', '/data/workspaces/marketing')

@raises(NotImplementedError)
def test_create_workspaces():
	st.workspaces.create()

def test_delete_workspaces():
	ws = st.workspaces.get(123)
	ws.delete()
	st.assert_called('DELETE', '/data/workspaces/marketing')

	st.workspaces.delete(ws)
	st.assert_called('DELETE', '/data/workspaces/marketing')

	st.workspaces.delete(123)
	st.assert_called('DELETE', '/data/workspaces/123')