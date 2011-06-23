# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""
from nose.tools import assert_true

from pyf.services.tests import TestController


class TestRootController(TestController):
    def test_index(self):
        response = self.app.get('/')

        assert_true('DashBoard' in response)
        assert_true('PyF' in response)
        assert_true('Login' in response)

