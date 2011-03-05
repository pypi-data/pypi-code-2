import pytest
import mypkg3
from webob import Request
from zope.component import getMultiAdapter
from zope.publisher.browser import TestRequest
from zope.pytest import configure, create_app
from mypkg3.app import SampleApp


def pytest_funcarg__apps(request):
    app = SampleApp()
    return app, create_app(request, app)

def pytest_funcarg__config(request):
    return configure(request, mypkg3, 'ftesting.zcml')

def test_view_sampleapp(config, apps):
    zope_app, wsgi_app = apps
    view = getMultiAdapter(
        (zope_app, TestRequest()), name="index.html")
    rendered_view = view()
    assert view() == u'Hello from SampleAppView!'

def test_browser(config, apps):
    zope_app, wsgi_app = apps
    http_request = Request.blank('http://localhost/test/index.html')
    response = http_request.get_response(wsgi_app)
    assert response.body == 'Hello from SampleAppView!'
    assert response.status == "200 Ok"

@pytest.mark.xfail("sys.version_info < (2,6)")
def test_infrae_browser(config, apps):
    # Late import. This import will fail with Python < 2.6
    from infrae.testbrowser.browser import Browser
    zope_app, wsgi_app = apps
    browser = Browser(wsgi_app)
    browser.open('http://localhost/test/index.html')
    assert browser.contents == 'Hello from SampleAppView!'
    assert browser.status == '200 Ok'
