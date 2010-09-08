import os
from webtest import TestApp
import tg
import ew
from tg.util import DottedFileNameFinder
from tg.configuration import AppConfig

class TestConfig(AppConfig):

    def __init__(self, folder, values=None):
        if values is None: 
            values = {}
        AppConfig.__init__(self)
        #First we setup some base values that we know will work
        self.renderers = ['genshi', 'mako', 'jinja','json']
        self.render_functions = tg.util.Bunch()
        self.package = ew.tests
        self.default_renderer = 'genshi'
        self.globals = self
        self.helpers = {}
        self.auth_backend = None
        self.auto_reload_templates = False
        self.use_legacy_renderer = False
        self.use_dotted_templatenames = False
        self.serve_static = False



        root = "."
        test_base_path = os.path.join(root,'ew/tests',)
        if folder:
            test_config_path = os.path.join(test_base_path, folder)
        else:
            test_config_path = test_base_path
        self.paths=tg.util.Bunch(
                    root=test_base_path,
                    controllers=os.path.join(test_config_path, 'controllers'),
                    static_files=os.path.join(test_config_path, 'public'),
                    templates=[os.path.join(test_config_path, 'templates')],
                    i18n=os.path.join(test_config_path, 'i18n')
                    )

        #Then we overide those values with what was passed in
        for key, value in values.items():
            setattr(self, key, value)

    def setup_helpers_and_globals(self):
        tg.config['pylons.app_globals'] = self.globals
        tg.config['pylons.h'] = self.helpers
        g = tg.config['pylons.app_globals']
        g.dotted_filename_finder = DottedFileNameFinder()

def app_from_config(base_config, deployment_config=None):
    if not deployment_config:
        deployment_config = {'debug': 'true',
                             'error_email_from': 'paste@localhost',
                             'smtp_server': 'localhost'}

    env_loader = base_config.make_load_environment()
    app_maker = base_config.setup_tg_wsgi_app(env_loader)
    app = TestApp(app_maker(deployment_config, full_stack=True))
    return app



