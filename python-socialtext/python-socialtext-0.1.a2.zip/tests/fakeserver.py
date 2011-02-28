"""
A fake server that "responds" to API methods with pre-canned responses.
"""

import httplib2
import urlparse
import urllib
from nose.tools import assert_equal
from socialtext import Socialtext
from socialtext.client import SocialtextClient
from utils import fail, assert_in, assert_not_in, assert_has_keys


def resp(status, body, headers={}):
    resp_dict = { "status" : status }
    if headers:
        resp_dict.update(headers)
    return httplib2.Response(resp_dict), body

class FakeServer(Socialtext):
    def __init__(self, url=None, user=None, password=None):
        super(FakeServer, self).__init__('http://st.example.com', 'username', 'password')
        self.client = FakeClient()

    def assert_called(self, method, url, body=None, query={}):
        """
        Assert that an API method was just called
        """
        expected = (method, url)
        called = self.client.callstack[-1][0:2]

        assert self.client.callstack, "Expected %s %s but no calles were made." % expected

        assert expected == called, "Expected %s %s, got %s %s" % (expected + called)

        if body is not None:
            assert_equal(self.client.callstack[-1][2], body)
            
        if query:
            assert_equal(self.client.callstack[-1][3], query)

        self.client.callstack = []
    
class FakeClient(SocialtextClient):
    def __init__(self):
        self.url = 'http://st.example.com'
        self.user = 'user'
        self.password = 'password'
        self.callstack = []

    def get(self, url, **kwargs):
        return self._st_request(url, "GET", **kwargs)
    
    def _st_request(self, url, method, **kwargs):
        # Check that certain things are called correctly
        if method in ['GET', 'DELETE']:
            assert_not_in('body', kwargs)
        elif method in ['PUT', 'POST']:
            assert_in('body', kwargs)
            
        parsed_url = urlparse.urlparse(url)
        
        munged_url = parsed_url.path.strip('/').replace('/', '_').replace('.', '_').replace('%20', '_')
        query = urlparse.parse_qs(parsed_url.query)
        
        query = dict( ( k, v if len(v) > 1 else v[0] )
                        for k, v in query.iteritems() )
                        
        kwargs['query'] = query
        
        callback = "%s_%s" % (method.lower(), munged_url)
        if not hasattr(self, callback):
            fail("Called unknown API method: %s %s" % (method, url))

        # Note the call
        self.callstack.append((method, parsed_url.path, kwargs.get('body', None), query))

        return getattr(self, callback)(**kwargs)
    
    ##########
    # Config #
    ##########
    
    def get_data_config(self, **kw):
        return resp(200, {
            "allow_network_invitation": 0,
            "api_version": 31,
            "data_push_available": 1,
            "desktop_update_url": "https://st.example.com/st/desktop/update",
            "server_version": "4.5.3.15",
            "signals_size_limit": "1000",
        })

    ##############
    # Exceptions #
    ##############

    def get_raise_400(self, **kw):
        return resp(400, None)

    def get_raise_401(self, **kw):
        return resp(401, None)
    
    def get_raise_403(self, **kw):
        return resp(403, None)

    def get_raise_404(self, **kw):
        return resp(404, None)
        
    def get_raise_409(self, **kw):
        return resp(409, None)

    def get_raise_413(self, **kw):
        return resp(413, None)

    ###########
    # SIGNALS #
    ###########

    def get_data_signals(self, **kw):
        query = kw.get('query', {})
        assert_has_keys(query,
            optional=[
                "accounts",
                "after",
                "before",
                "direct",
                "direction",
                "following",
                "groups",
                "hidden",
                "limit",
                "offset",
                "order",
                "sender",
            ]
        )
        return resp(200, [
            {
                "mentioned_users": [],
                "attachments": [],
                "in_reply_to": { },
                "group_ids": [],
                "num_replies": "0",
                "account_ids": ["1"],
                "tags": ["foo", "bar"],
                "annotations": [],
                "uri": "/st/signals/45ddcc89023426bf",
                "body": 'Hello world!',
                "hash": "103dcc89023428d82",
                "best_full_name": "John Smith",
                "at":"2009-01-06 20:19:24.501494Z",
                "user_id":"3038",
                "signal_id": "123",
            },
            {
                "mentioned_users": [{"best_full_name" : "Smart Bob", "id" : 34343}],
                "attachments": [],
                "in_reply_to": { "user_id" : "34343", "signal_id" : "402", "uri" : "/st/signal/d28dcc89023428f3?r=4fgdcc89023429d5" },
                "group_ids": [],
                "num_replies": "0",
                "account_ids": ["1", "2", "3"],
                "tags": ["see it", "on now"],
                "annotations": [{"my_movies": {"title":"Bullit"}}],
                "uri": "/st/signals/45ddcc89023426bf",
                "body": 'I got my mustang back from the shop that <a href="/?profile/3063">Smart Bob</a> owns',
                "hash": "103dcc89023428d82",
                "best_full_name": "Steve McQueen",
                "at":"2009-01-06 20:19:24.501494Z",
                "user_id":"3037",
                "signal_id": "987",
            }
        ])

    def get_data_signals_123(self, **kw):
        signal = self.get_data_signals()[1][0]
        return resp(200, signal)

    def delete_data_signals_123(self, **kw):
        return resp(202, None)

    def put_data_signals_123_hidden(self, **kw):
        return resp(202, None)
    
    def post_data_signals(self, body, **kw):
        assert_has_keys(body,
            required=['signal'],
            optional=[
                "account_ids",
                'annotations',
                'in_reply_to',
                'group_ids',
                "recipient"
            ]
        )
        assert_has_keys(body.get('in_reply_to', {}),
            optional=[
                "signal_id",
                "search"
            ]
        )
        return resp(204, None, headers={ 
            'x-location': "/st/signals/45ddcc89023426bf",
            'x-signal-id': 123,
            'x-signal-hash':"103dcc89023428d82", 
        })

    #########
    # USERS #
    #########

    def get_data_users(self, **kw):
        query = kw.get('query', {})
        
        assert_has_keys(query,
            optional=["count", "filter", "offset", "order", "want_private_fields"])
        return resp(200, [
            {
                "email_address": "john@example.com",
                "best_full_name": "John Smith",
                "user_id": 123,
                "username": "JAS123",
                "last_name": "Smith",
                "first_name": "John",
            },
            {
                "email_address": "bob@example.com",
                "best_full_name": "Bob MacDonald",
                "user_id": 987,
                "username": "BAM987",
                "last_name": "MacDonald",
                "first_name": "Bob",
            }
        ])

    def get_data_users_123(self, **kw):
        query = kw.get('query', {})
        
        assert_has_keys(query,
            optional=["all", "want_private_fields"])
        user = self.get_data_users()[1][0]
        return resp(200, user)
    
    ############
    # WEBHOOKS #
    ############
    
    def get_data_webhooks(self, **kw):
        return resp(200, [
            {
                "workspace_id" : None,
                "group_id" : None,
                "url" : "https://example.com",
                "class" : "signal.create",
                "id" : 123,
                "details" : { "to_user" : 123, "tag" : "abc123" },
                "account_id" : 1,
                "creator_id" : 110
            },
            {
                "workspace_id" : 123,
                "group_id" : None,
                "url" : "https://example.com",
                "class" : "page.create",
                "id" : 987,
                "details" : { 'page_id' : 'example_page' },
                "account_id" : None,
                "creator_id" : 110
            },
        ])

    def get_data_webhooks_123(self, **kw):
        hook = self.get_data_webhooks()[1][0]
        return resp(200, hook)

    def get_data_webhooks_987(self, **kw):
        hook = self.get_data_webhooks()[1][1]
        return resp(200, hook)

    def delete_data_webhooks_123(self, **kw):
        return resp(202, None)

    def post_data_webhooks(self, body, **kw):
        assert_has_keys(body,
            required=['class', 'url'],
            optional=['workspace_id', 'account_id', 'group_id', 'details'])

        hook_id = 123 if body['class'] == "signal.create" else 987
        # POST to /data/webhooks returns an empty body
        # with a Location header pointing to the resource.
        return resp(204, None, headers={
            'location': '/data/webhooks/%d' % hook_id
        })

    ##############
    # WORKSPACES #
    ##############

    def get_data_workspaces(self, **kw):
        return resp(200, [
            {
                "workspace_id": "123",
                "is_all_users_workspace": 0,
                "permission_set": "members_only",
                "group_count": "3",
                "name": "marketing",
                "default": 0,
                "modified_time": "2007-05-21 10:55:46.630421-07",
                "account_id": "2",
                "uri": "/data/workspaces/marketing",
                "id": 123,
                "title" : "Marketing",
                "user_count" : 2
            },
            {
                "workspace_id": "987",
                "is_all_users_workspace": 0,
                "permission_set": "members_only",
                "group_count": "1",
                "name": "sales",
                "default": 0,
                "modified_time": "2007-05-21 10:55:46.630421-07",
                "account_id": "1",
                "uri": "/data/workspaces/sales",
                "id": 987,
                "title" : "Sales",
                "user_count" : 2
            }
        ])

    def get_data_workspaces_123(self, **kw):
        hook = self.get_data_workspaces()[1][0]
        return resp(200, hook)

    def get_data_workspaces_marketing(self, **kw):
        hook = self.get_data_workspaces()[1][0]
        return resp(200, hook)

    def delete_data_workspaces_123(self, **kw):
        return resp(202, None)

    def delete_data_workspaces_marketing(self, **kw):
        return self.delete_data_workspaces_123()

    
    def get_data_workspaces_987(self, **kw):
        hook = self.get_data_workspaces()[1][1]
        return resp(200, hook)

    def get_data_workspaces_sales(self, **kw):
        hook = self.get_data_workspaces()[1][1]
        return resp(200, hook)

    #########
    # PAGES #
    #########

    def get_data_workspaces_marketing_pages(self, **kw):
        return resp(200, [
            {
                "page_uri" : "http://example.com/marketing/index.cgi?test_1",
                "modified_time" : 1169971407,
                "name" : "Test 1",
                "uri" : "test_1",
                "revision_id" : 1234567890,
                "page_id" : "test_1",
                "tags" : ["Foo", "Bar"],
                "last_edit_time" : "2007-01-28 08:03:27 GMT",
                "revision_count" : 1,
                "last_editor" : "bob@example.com",
                "workspace_name" : "marketing",
                "type" : "wiki"
            },
            {
                "page_uri" : "http://example.com/marketing/index.cgi?test_2",
                "modified_time" : 1169971407,
                "name" : "Test 2",
                "uri" : "test_1",
                "revision_id" : 1234567890,
                "page_id" : "test_2",
                "tags" : ["Hello", "World"],
                "last_edit_time" : "2007-01-28 08:03:27 GMT",
                "revision_count" : 1,
                "last_editor" : "joe@example.com",
                "workspace_name" : "marketing",
                "type" : "wiki"
            }
        ])

    def get_data_workspaces_marketing_pages_test_1(self, **kw):
        kw.setdefault('headers', {})
        kw['headers'].setdefault('Accept', 'application/json')
        accept = kw['headers']['Accept']
        if accept == 'application/json':
            page = self.get_data_workspaces_marketing_pages()[1][0]
            return resp(200, page)
        elif accept == 'text/x.socialtext-wiki':
            return resp(200,
            """
            [Hello world] This is a wiki!
            """, headers={ "content-type" : "text/x.socialtext-wiki" })
        else:
            return resp(200,
            """
            <div class="wiki">
                <a href="#">Hello world</a><p>This is a wiki!</p>
            </div>
            """, headers={ "content-type" : "text/html"})

    def put_data_workspaces_marketing_pages_Test_1(self, body, **kw):
        assert_has_keys(body,
            required=['content'],
            optional=['tags', 'edit_summary', 'signal_edit_summary'])
        return resp(204, None)

    def delete_data_workspaces_marketing_pages_test_1(self, **kw):
        return resp(202, None)  