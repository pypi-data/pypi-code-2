import time

from cStringIO import StringIO
from urllib import urlencode
from unittest import TestCase

import cherrypy

from turbogears import config, controllers, expose, startup, testutil, visit


def cookie_header(morsel):
    """Returns a dict containing cookie information to pass to a server."""
    return {'Cookie': morsel.output(header="")[1:]}


class VisitRoot(controllers.RootController):

    [expose()]
    def index(self):
        cur_visit = visit.current()
        return cur_visit.key


class TestVisit(TestCase):

    def setUp(self):
        self._visit_on = config.get('visit.on', False)
        self._visit_source = config.get('visit.source', 'cookie')
        config.update({'visit.on': True})
        self._visit_timeout = config.get('visit.timeout', 20)
        config.update({'visit.timeout': 50})
        self.cookie_name = config.get("visit.cookie.name", 'tg-visit')
        self._visit_key_param = config.get("visit.form.name", 'tg_visit')
        cherrypy.root = VisitRoot()

    def tearDown(self):
        startup.stopTurboGears()
        config.update({'visit.timeout': self._visit_timeout})
        config.update({'visit.on': self._visit_on})

    def test_visit_response(self):
        """Test if the visit cookie is set in cherrypy.response."""
        testutil.create_request("/")
        assert cherrypy.response.simple_cookie.has_key(self.cookie_name)

    def test_new_visit(self):
        """Test that we can see a new visit on the server."""
        testutil.create_request("/")
        assert visit.current().is_new

    def test_old_visit(self):
        """Test if we can track a visitor over time."""
        testutil.create_request("/")
        # first visit's cookie
        morsel = cherrypy.response.simple_cookie[self.cookie_name]
        testutil.create_request("/", headers=cookie_header(morsel))
        assert not visit.current().is_new

    def test_visit_from_form(self):
        """Test if the visit key is retrieved from the request params."""
        try:
            config.update({'visit.source': 'cookie,form'})
            # first visit's cookie
            testutil.create_request("/")
            first_key = cherrypy.response.body[0].strip()
            # second request with no cookies
            post_data = StringIO(urlencode({self._visit_key_param: first_key}))
            testutil.create_request("/", method='POST', rfile=post_data)
            second_key = cherrypy.response.body[0].strip()
        finally:
            config.update({'visit.source': self._visit_source})
        assert first_key == second_key

    def test_visit_from_form_with_cookie_fallback(self):
        """Test if visit key is retrieved from cookie if not found in params."""
        try:
            config.update({'visit.source': 'form,cookie'})
            # first visit's cookie
            testutil.create_request("/")
            first_key = cherrypy.response.body[0].strip()
            # second request with no cookies
            morsel = cherrypy.response.simple_cookie[self.cookie_name]
            testutil.create_request("/", headers=cookie_header(morsel))
            second_key = cherrypy.response.body[0].strip()
        finally:
            config.update({'visit.source': self._visit_source})
        assert first_key == second_key

    def test_cookie_expires(self):
        """Test if the visit timeout mechanism works."""
        timeout = config.get('visit.timeout', 50)
        try:
            # set expiration to one second for this test only
            config.update({'visit.timeout': 1.0/60})
            testutil.create_request("/")
            morsel = cherrypy.response.simple_cookie[self.cookie_name]
            time.sleep(2) # 2 seconds
            testutil.create_request("/", headers=cookie_header(morsel))
        finally:
            config.update({'visit.timeout': timeout})
        assert cherrypy.response.simple_cookie[
                self.cookie_name].value != morsel.value, \
            'cookie values should not match'
        assert visit.current().is_new, \
            'this should be a new visit, as the cookie has expired'

    def test_cookie_not_permanent(self):
        """Check that by default the visit cookie is not permanent."""
        testutil.create_request('/')
        morsel = cherrypy.response.simple_cookie[self.cookie_name]
        assert not morsel['expires'] and not morsel['max-age']

    def test_cookie_permanent(self):
        """Check that the visit cookie can be made permanent."""
        permanent = config.get('visit.cookie.permanent', False)
        try:
            # set cookie permanent for this test only (needs restart)
            startup.stopTurboGears()
            config.update({'visit.cookie.permanent': True})
            startup.startTurboGears()
            testutil.create_request('/')
            morsel = cherrypy.response.simple_cookie[self.cookie_name]
        finally:
            config.update({'visit.cookie.permanent': permanent})
        assert morsel['max-age'] == 3000
        expires = time.mktime(time.strptime(morsel['expires'],
            '%a, %d-%b-%Y %H:%M:%S GMT')[:8] + (0,))
        should_expire = time.mktime(time.gmtime()) + morsel['max-age']
        assert abs(should_expire - expires) < 3
