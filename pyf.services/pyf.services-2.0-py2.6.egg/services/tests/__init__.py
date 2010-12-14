# -*- coding: utf-8 -*-
"""Unit and functional test suite for pyf.services."""

from tg import config
from paste.deploy import appconfig, loadapp
from routes import url_for
from webtest import TestApp

from pyf.services import model
from pyf.services.websetup import setup_app

__all__ = ['setup_db', 'teardown_db', 'TestController', 'url_for']

def setup_db():
    """Method used to build a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.init_model(engine)
    model.metadata.create_all(engine)

def teardown_db():
    """Method used to destroy a database"""
    engine = config['pylons.app_globals'].sa_engine
    model.metadata.drop_all(engine)

class TestController(object):
    """
    Base functional test case for the controllers.
    
    The pyf.services application instance (``self.app``) set up in this test 
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.
    
    Check pyf.services.tests.functional.test_authentication for the repoze.who
    integration tests.
    
    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).
    
    """
    
    application_under_test = 'main_without_authn'
    
    def setUp(self):
        """Method called by nose before running each test"""
        app_conf = 'config:test.ini#%s' % self.application_under_test

        # Loading the application:
        conf_dir = config.here
        wsgiapp = loadapp(app_conf, relative_to=conf_dir)
        self.app = TestApp(wsgiapp)

        # Setting it up:
        conf = appconfig(app_conf, relative_to="./")
        setup_app("pyf.services", conf, [])
    
    def tearDown(self):
        """Method called by nose after running each test"""
        # Cleaning up the database:
        teardown_db()
