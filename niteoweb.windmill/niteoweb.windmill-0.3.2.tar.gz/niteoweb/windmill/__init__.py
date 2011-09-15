import sys
import logging
import posixpath as url_path

import transaction

from Products.PloneTestCase.PloneTestCase import FunctionalTestCase, portal_owner, default_password
from Products.PloneTestCase.layer import PloneSite as PloneLayer

import windmill

from windmill.bin.admin_lib import configure_global_settings, setup, teardown
from windmill.authoring.unit import WindmillUnitTestCase
from windmill.authoring import WindmillTestClient

from niteoweb.windmill.zserver import ZServerLayer

log = logging.getLogger(__name__)

class WindmillLayer(ZServerLayer):
    """Layer for running windmill. This depends on the ZServer layer, which
    means that it will start up a ZServer instance on a random port.
    See zserver.py for details.
    """
    
    site = 'plone'
    
    windmill_settings = {
        'START_FIREFOX': True,
    }
    
    test_url = "http://%(host)s:%(port)s/index_html"

    @classmethod
    def setUp(cls):
        
        # Start the Zope server with one thread
        host, port = cls.host, cls.port
        cls.test_url = cls.test_url % locals()
        log.debug('Starting ZServer on: %s' % cls.test_url)

        # Configure windmill
        windmill.stdout, windmill.stdin = sys.stdout, sys.stdin
        configure_global_settings()
        windmill.settings['TEST_URL'] = cls.test_url
        windmill.settings.update(getattr(cls, "windmill_settings", {}))
        cls.windmill_shell_objects = setup()
        log.debug('Starting Windmill with settings: %r' % windmill.settings)

        # Configure client
        cls.wm = WindmillTestClient(__name__)
        def open_site(*a, **kw):
            """little hack to always open an url with name of plone site"""
            transaction.commit()
            if 'url' in kw:
                kw['url'] = url_path.join('/' + (kw.get('site', None) or cls.site), kw['url'].lstrip('/'))
            return cls.wm.open(*a, **kw)
        cls.wm.open_site = open_site

    @classmethod
    def tearDown(cls):
        teardown(cls.windmill_shell_objects)


class WindmillPloneLayer(PloneLayer, WindmillLayer):
    """Convenience layer which mixes PloneLayer from PloneTestCase in with
    WindMillLayer. Use this layer to execute a windmill test against a Plone
    site configured using the normal PloneTestCase setup.
    """


class WindmillTestCase(FunctionalTestCase):
    """Convenient test case which makes a Windmill controller availalbe on
    self.wm and adds some convenience methods.
    """
    
    layer = WindmillPloneLayer

    @property
    def wm(self):
        return self.layer.wm

    def login_user(self, username=portal_owner, password=default_password):
        self.wm.open_site(url="/login_form")
        self.wm.waits.forPageLoad(timeout=30000)
        self.wm.type(id="__ac_name", text=username)
        self.wm.type(id="__ac_password", text=password)
        self.wm.click(name="submit")
        self.wm.waits.forPageLoad(timeout=30000)
        self.wm.asserts.assertNode(xpath="//dl[@class='portalMessage info']/dd")

    def add_user(self, username, password, roles=('Manager',)):
        self.portal.acl_users.userFolderAddUser(username, password, roles, [])
        transaction.commit()
