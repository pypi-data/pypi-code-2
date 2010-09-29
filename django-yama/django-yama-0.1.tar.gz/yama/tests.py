import django.test as unittest
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import admin, auth
from django.contrib.contenttypes.models import ContentType
from django.test.client import Client
from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError

from yama.admin import MenuAdmin
from yama.models import Menu, MenuItem
from yama.settings import MODELS

MENU_LANG = settings.LANGUAGES[0][0]
ADMIN_BASE = reverse('admin:app_list', args=['yama'])

class MenuTests(unittest.TestCase):
    fixtures = ['menus_test']
    
    def setUp(self):
        self.client = Client()
        assert self.client.login(username='user', password='pass')

    def testUniqueVisible(self):
        """ Make sure that no two visible menus with the same language can exist in the same position """
        m1 = Menu.objects.create(name='right menu 1', type='R', language=MENU_LANG, visible=True)
        # this should be ok, it's not visible
        m2 = Menu.objects.create(name='right menu 2', type='R', language=MENU_LANG, visible=False)
        # this should be ok as well, different type of menu
        m3 = Menu.objects.create(name='top menu 1', type='U', language=MENU_LANG, visible=False)
        self.assertRaises(IntegrityError, Menu.objects.create, name='right menu 3', type='R', language=MENU_LANG, visible=True)

    def testBasicAdminUrlsReturn200(self):
        urls = ['menu/', 'menu/add/', 'menu/1/', 'menu/1/delete/', 'menu/1/item/1/', 
                'menu/1/item/add/', 'menu/1/item/add/as/first-child/of/1/']
        for url in urls:
            response = self.client.get(ADMIN_BASE + url)
            got = '%s: %s' % (url, response.status_code)
            expected = '%s: %d' % (url, 200)
            self.assertEquals(got, expected)
    
    def testMovingItemsWorks(self):
        # originally, the first element has an id of 1
        self.assertEquals(MenuItem.objects.all()[0].id, 1)
        url = ADMIN_BASE + 'menu/1/item/3/move/'
        response = self.client.post(url, {'position' : 'left', 'target_id' : 1})
        self.assertEquals('%s: %s' % (url, response.status_code), '%s: %d' % (url, 200))
        self.assertEquals(MenuItem.objects.all()[0].id, 3)

    def testValidTargets(self):
        item = MenuItem.objects.get(pk=3)
        url = ADMIN_BASE + 'menu/1/item/3/valid-targets/'
        response = self.client.get(url)
        self.assertEquals('%s: %s' % (url, response.status_code), '%s: %s' % (url, 200))

        returned_ids = [int(s) for s in response.content.split(',')]
        invalid_ids = [desc.id for desc in item.get_descendants()]
        invalid_ids.append(item.id)
        valid_ids = [itm.id for itm in MenuItem.objects.exclude(id__in=invalid_ids)]

        self.assertEquals(len(valid_ids), len(returned_ids))
        for valid_id in valid_ids:
            self.assert_(valid_id in returned_ids, '%d not in %s' % (valid_id, returned_ids))

    def testContentObjects(self):
        MODELS[('auth', 'User')] = Q(is_active=True)
        model = auth.models.User
        content_type = ContentType.objects.get_for_model(model)
        url = ADMIN_BASE + 'menu/contenttype/%d/' % content_type.id
        response = self.client.get(url)
        obj_repr = unicode(model.objects.filter(is_active=True)[0])
        self.assertContains(response, obj_repr, status_code=200)

    def testMenuItemsCanHaveOnlyOneLink(self):
        menu = Menu.objects.get()
        ct = ContentType.objects.all()[0]
        same_args = {'menu' : menu, 'caption' : 'test', 'visible' : False, 'open_in_new_window' : False}
        more_args = [
            {'link_view' : 'test.views.main_view', 'link_url': 'http://www.google.com', 'content_type' : ct, 'object_id' : ct.id }
        ]
        for args in more_args:
            item = MenuItem()
            args.update(same_args)
            for arg in args:
                setattr(item, arg, args[arg])
            self.assertRaises(ValidationError, MenuItem.objects.insert_node, node=item, target=None, commit=True)
