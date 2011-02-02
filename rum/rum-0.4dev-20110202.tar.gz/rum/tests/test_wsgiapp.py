from pkg_resources import resource_filename
from unittest import TestCase
import rum
from rum import exceptions as exc
from rum.testutil import RumTestApp
from paste.deploy import loadapp

class TestRumApp(TestCase):
    def test_load_paste_app_factory(self):
        app = loadapp('config:'+resource_filename('rum.tests', 'test.ini'))

    def test_load_no_config(self):
        app = rum.RumApp()

    def test_load_with_config_from_file(self):
        app = rum.RumApp(resource_filename('rum.tests', 'test.cfg'))

    def test_load_no_full_stack(self):
        app = rum.RumApp(full_stack=False)

    def test_load_debug_true(self):
        app = rum.RumApp(debug=True)

    def test_set_names(self):
        app = rum.RumApp(resource_filename('rum.tests', 'test.cfg'))
        from rum.tests.model import Person
        names=("psn","psns")
        names_canonical=app.names_for_resource(Person)
        app.set_names(Person,*names)
        self.failUnlessEqual(app.names_for_resource(Person), names)
        app.set_names(Person, *names_canonical)
        self.failUnlessEqual(app.names_for_resource(Person), names_canonical)
    def test_url_for_called_outside_rum_context(self):
        app = rum.RumApp(resource_filename('rum.tests', 'test.cfg'))
        from rum.tests.model import Person

        # Emulate what 'with' does so test can work in py2.4
        ctx = app.mounted_at('/admin')
        ctx.__enter__()
        try:
            url = app.url_for(Person, action='new')
            self.failUnlessEqual(url, '/admin/persons/new')
        
            person_obj = Person(id='alberto')
            url = app.url_for(obj=person_obj, action='edit')
            self.failUnlessEqual(url, '/admin/persons/alberto/edit')
        finally:
            ctx.__exit__()


class TestRootController(TestCase):
    def setUp(self):
        app = rum.RumApp(resource_filename('rum.tests', 'test.cfg'))
        self.app = RumTestApp(app)

    def test_root(self):
        self.app.get('/')
