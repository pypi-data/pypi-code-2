#coding: utf-8
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django_webtest import WebTest
from vkontakte import signature
from vkontakte.api import _to_utf8
from merchant_api.models import Order
from merchant_api import conf

BASIC_REQUEST = {
    'item_currency_1': '643',
    'item_price_1': '100.00',
    'item_quantity_1': '1',
    'item_currency_str_1': 'RUB',
    'item_id_1': '1',
    'user_id': '1134587',
    'new_state': 'chargeable',
    'order_id': '21282',
    'currency': '643',
    'amount': '100.00',
    'currency_str': 'RUB',
    'order_date': '2010-09-03T04:32:08+04:00',
    'notification_type': 'order-state-change-test',
    'shipping_email': 'id1134587@vk.com',
    'merchant_id': conf.SHOP_ID,
    'user_name': u'Василий',
}


def _dict_to_utf8(d):
    return dict([(key, _to_utf8(d[key]),) for key in d])


class BaseMerchantApiTest(WebTest):

    def setUp(self):
        self.user = User.objects.create_user(BASIC_REQUEST['user_id'], '', '123')

    def notify_raw(self, data):
        return self.app.post(reverse('merchant_callback'), _dict_to_utf8(data))

    def notify(self, data, expected_state=None):
        data = data.copy()
        data['sig'] = signature(conf.SHOP_SECRET_KEY, data)
        response = self.notify_raw(data)
        if expected_state:
            assert expected_state in response, response
        return response

    def _data(self, **kwargs):
        data = BASIC_REQUEST.copy()
        data.update(kwargs)
        return data

class MerchantApiTest(BaseMerchantApiTest):
    fixtures = ['cities']

    def setUp(self):
        super(MerchantApiTest, self).setUp()
        self.forms_module = conf.forms_module
        conf.forms_module = 'merchant_api.forms'

    def tearDown(self):
        conf.forms_module = self.forms_module

    def assertOrdersCreated(self, data, num_test, num_real):
        test_count = Order.test.count()
        real_count = Order.real.count()
        response = self.notify(data)
        assert 'success' in response, response
        self.assertEqual(Order.test.count(), test_count + num_test)
        self.assertEqual(Order.real.count(), real_count + num_real)

    def test_callback_available(self):
        self.app.get(reverse('merchant_callback'))

    def test_basic_buy(self):
        self.notify(BASIC_REQUEST, 'success')

    def test_invalid_request(self):
        assert 'failure' in self.notify_raw(BASIC_REQUEST)

    def test_invalid_signature(self):
        response = self.notify_raw(self._data(sig='123'))
        assert 'failure' in response
        assert 'Invalid signature' in response

    def test_django_user(self):
        user = User.objects.create_user('123', '', None)
        self.assertEqual(user.vk_orders.count(), 0)
        self.notify(self._data(user_id = user.username), 'success')
        self.assertEqual(user.vk_orders.count(), 1)

    def test_testorder_creation(self):
        self.assertOrdersCreated(BASIC_REQUEST, +1, 0)

    def test_order_creation(self):
        data = self._data(notification_type = 'order-state-change')
        self.assertOrdersCreated(data, 0, +1)

    def test_invalid_status(self):
        response = self.notify(self._data(new_state='vasia'), 'failure')
        assert 'Invalid state: vasia' in response

    def test_invalid_user(self):
        old_apps = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = list(old_apps)[:] + ['vk_iframe']
        try:
            response = self.notify(self._data(user_id='123'), 'failure')
            assert 'User does not exist' in response
        finally:
            settings.INSTALLED_APPS = old_apps

    def test_invalid_user_no_iframe(self):
        # should not fail if vk_iframe is installed
        old_apps = settings.INSTALLED_APPS
        try:
            if 'vk_iframe' in old_apps:
                settings.INSTALLED_APPS = list(settings.INSTALLED_APPS)[:]
                settings.INSTALLED_APPS.remove('vk_iframe')
            self.notify(self._data(user_id='123'), 'success')
        finally:
            settings.INSTALLED_APPS = old_apps


    def test_items(self):
        order_id = BASIC_REQUEST['order_id']
        response = self.notify(BASIC_REQUEST, 'success')
        assert order_id in response, response
        order = Order.objects.get(order_id=order_id)
        items = order.items.all()
        self.assertEqual(items.count(), 1)



