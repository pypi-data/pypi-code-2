"""Tests for the `setup` module.
"""
import zope.pytest.tests
from zope.app.wsgi import WSGIPublisherApplication
from zope.publisher.browser import TestRequest
from zope.configuration.interfaces import IConfigurationContext
from zope.pytest.setup import (
    create_app, configure, setup_config, teardown_config,
    setup_db, teardown_db, setup_connection, teardown_connection,
    setup_root, teardown_root
    )

def pytest_funcarg__conf_request(request):
    return request

def test_configure(conf_request):
    result = configure(conf_request, zope.pytest.tests, 'minimal.zcml')
    assert IConfigurationContext.providedBy(result)

def test_create_app(conf_request):
    # We have to configure the environment to get an app.
    config = setup_config(zope.pytest.tests, 'ftesting.zcml')
    app = create_app(conf_request, None)
    teardown_config(config)
    assert isinstance(app, WSGIPublisherApplication)

