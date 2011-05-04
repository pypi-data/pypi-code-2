import cherrypy
import simplejson

from turbogears import controllers, expose
from turbogears.testutil import create_request


class ExposeRoot(controllers.RootController):

    [expose("turbogears.tests.simple")]
    [expose("json")]
    def with_json(self):
        return dict(title="Foobar", mybool=False, someval="foo")

    [expose("turbogears.tests.simple")]
    [expose("json", accept_format = "application/json", as_format="json")]
    [expose('cheetah:turbogears.tests.textfmt', accept_format="text/plain")]
    def with_json_via_accept(self):
        return dict(title="Foobar", mybool=False, someval="foo")


def test_gettinghtml():
    cherrypy.root = ExposeRoot()
    create_request("/with_json")
    body = cherrypy.response.body[0]
    assert "Paging all foo" in body

def test_gettingjson():
    cherrypy.root = ExposeRoot()
    create_request("/with_json?tg_format=json")
    body = cherrypy.response.body[0]
    assert '"title": "Foobar"' in body

def test_gettingjsonviaaccept():
    cherrypy.root = ExposeRoot()
    create_request("/with_json_via_accept",
            headers=dict(Accept="application/json"))
    body = cherrypy.response.body[0]
    assert '"title": "Foobar"' in body

def test_getting_json_with_accept_but_using_tg_format():
    cherrypy.root = ExposeRoot()
    create_request("/with_json_via_accept?tg_format=json")
    body = cherrypy.response.body[0]
    assert '"title": "Foobar"' in body

def test_getting_plaintext():
    cherrypy.root = ExposeRoot()
    create_request("/with_json_via_accept",
        headers=dict(Accept="text/plain"))
    print cherrypy.response.body[0]
    assert cherrypy.response.body[0] == "This is a plain text for foo."

def test_allow_json():

    class NewRoot(controllers.RootController):
        [expose(template="turbogears.tests.doesnotexist", allow_json=True)]
        def test(self):
            return dict(title="Foobar", mybool=False, someval="niggles")

    cherrypy.root = NewRoot()
    create_request("/test", headers= dict(accept="application/json"))
    body = cherrypy.response.body[0]
    values = simplejson.loads(body)
    assert values == dict(title="Foobar", mybool=False, someval="niggles",
        tg_flash=None)
    assert cherrypy.response.headers["Content-Type"] == "application/json"
    create_request("/test?tg_format=json")
    body = cherrypy.response.body[0]
    values = simplejson.loads(body)
    assert values == dict(title="Foobar", mybool=False, someval="niggles",
        tg_flash=None)
    assert cherrypy.response.headers["Content-Type"] == "application/json"
