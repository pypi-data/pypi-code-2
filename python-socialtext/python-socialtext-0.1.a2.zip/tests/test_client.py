import base64
import mock
import httplib2
from socialtext.client import SocialtextClient
from nose.tools import assert_equal

fake_response = httplib2.Response({"status": 200})
fake_body = '{"hi": "there"}'
mock_request = mock.Mock(return_value=(fake_response, fake_body))

def client(impersonate=False):
    cl = SocialtextClient("http://example.com", "username", "apikey")
    if impersonate:
        cl.impersonate("joe@example.com")
    return cl

def test_impersonate():
    cl = client(impersonate=True)
    assert_equal("joe@example.com", cl.on_behalf_of)

def test_get():
    cl = client(impersonate=True)
    
    @mock.patch.object(httplib2.Http, "request", mock_request)
    @mock.patch('time.time', mock.Mock(return_value=1234))
    def test_get_call():
        resp, body = cl.get("/hi")
        mock_request.assert_called_with("http://example.com/hi", "GET", 
            headers={
                "Accept": "application/json",
                "authorization" : cl.authorization(),
                "User-Agent": cl.USER_AGENT,
                "X-On-Behalf-Of": cl.on_behalf_of
            }
        )
        # Automatic JSON parsing
        assert_equal(body, {"hi":"there"})

    test_get_call()

def test_post():
    cl = client(impersonate=True)
    
    @mock.patch.object(httplib2.Http, "request", mock_request)
    def test_post_call():
        cl.post("/hi", body=[1, 2, 3])
        mock_request.assert_called_with("http://example.com/hi", "POST", 
            headers = {
                "Accept": "application/json",
                "authorization" : cl.authorization(),
                "Content-Type": "application/json",
                "User-Agent": cl.USER_AGENT,
                "X-On-Behalf-Of": cl.on_behalf_of
            },
            body = '[1, 2, 3]'
        )
    
    test_post_call()