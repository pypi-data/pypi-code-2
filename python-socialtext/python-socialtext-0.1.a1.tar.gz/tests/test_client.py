import base64
import mock
import httplib2
from socialtext.client import SocialtextClient
from nose.tools import assert_equal

fake_response = httplib2.Response({"status": 200})
fake_body = '{"hi": "there"}'
mock_request = mock.Mock(return_value=(fake_response, fake_body))

def client():
    cl = SocialtextClient("http://example.com", "username", "apikey")
    return cl

def test_get():
    cl = client()
    
    @mock.patch.object(httplib2.Http, "request", mock_request)
    @mock.patch('time.time', mock.Mock(return_value=1234))
    def test_get_call():
        resp, body = cl.get("/hi")
        mock_request.assert_called_with("http://example.com/hi", "GET", 
            headers={
                "Accept": "application/json",
                "authorization" : cl.authorization(),
                "User-Agent": cl.USER_AGENT
            }
        )
        # Automatic JSON parsing
        assert_equal(body, {"hi":"there"})

    test_get_call()

def test_post():
    cl = client()
    
    @mock.patch.object(httplib2.Http, "request", mock_request)
    def test_post_call():
        cl.post("/hi", body=[1, 2, 3])
        mock_request.assert_called_with("http://example.com/hi", "POST", 
            headers = {
                "Accept": "application/json",
                "authorization" : cl.authorization(),
                "Content-Type": "application/json",
                "User-Agent": cl.USER_AGENT
            },
            body = '[1, 2, 3]'
        )
    
    test_post_call()