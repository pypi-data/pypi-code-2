import StringIO
from nose.tools import assert_equal, raises
from fakeserver import FakeServer
from utils import assert_isinstance
from socialtext import Page, Workspace

st = FakeServer()

def test_list_pages():
	pl = st.pages.list('marketing')
	st.assert_called('GET', '/data/workspaces/marketing/pages')
	[assert_isinstance(p, Page) for p in pl]
	
	# Get pages by workspace
	ws = st.workspaces.get('marketing')
	st.pages.list(ws)
	st.assert_called('GET', '/data/workspaces/marketing/pages')
	[assert_isinstance(p, Page) for p in pl]
	
def test_get_pages():
	page = st.pages.get('test_1', ws='marketing')
	st.assert_called('GET', '/data/workspaces/marketing/pages/test_1')
	assert_isinstance(page, Page)

	page.get()
	st.assert_called('GET', '/data/workspaces/marketing/pages/test_1')

	st.pages.get(page)
	st.assert_called('GET', '/data/workspaces/marketing/pages/test_1')

def test_get_pages_html():
	page = st.pages.get('test_1', ws='marketing')

	html = page.get_html()
	st.assert_called('GET', '/data/workspaces/marketing/pages/test_1')
	assert_isinstance(html, str)
	assert '</div>' in html

def test_delete_pages():
	page = st.pages.get('test_1', ws='marketing')

	page.delete()
	st.assert_called('DELETE', '/data/workspaces/marketing/pages/test_1')

	st.pages.delete('test_1', ws='marketing')
	st.assert_called('DELETE', '/data/workspaces/marketing/pages/test_1')

	st.pages.delete(page)
	st.assert_called('DELETE', '/data/workspaces/marketing/pages/test_1')

def test_create_page():
	ws = "marketing"
	name = "Test 1"
	body = "This is a wiki"
	tags = ["foo", "bar"]
	edit_summary = "This is an edit summary!"

	page = st.pages.create(name, ws, body, tags=tags, edit_summary=edit_summary)

	# The Socialtext API doesn't return a JSON of the page.
	# We force a call to the newly created page
	st.assert_called('GET', '/data/workspaces/marketing/pages/test_1')
	assert_isinstance(page, Page)
	assert_equal(page.name, name)