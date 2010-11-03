from django.test import TestCase
from django.core.urlresolvers import reverse

from netcash.models import NetcashGateway, NetcashOrder
from netcash.forms import NetcashForm
import netcash.signals

class NetcashTest(TestCase):

    def setUp(self):
        self.gateway = NetcashGateway.objects.all()[0]
        self.gateway.netcash_ip = '127.0.0.1'
        self.gateway.save()

        # reload the gateway
        self.gateway = NetcashGateway.objects.all()[0]

        self.gateway_url = reverse('netcash_data', args = [self.gateway.secret])

    def test_invalid_data_request(self):
        response = self.client.post(self.gateway_url, {})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(NetcashOrder.objects.count(), 0)

    def test_invalid_gateway(self):
        response = self.client.post(self.gateway_url.rstrip('/')+'123/', {})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(NetcashOrder.objects.count(), 0)

    def test_data_request(self):
        # signal handler
        def data_handler(sender, order, **kwargs):
            data_handler.called = True
            data_handler.order = order
        data_handler.called = False
        data_handler.order = None

        netcash.signals.data.connect(data_handler)

        # this will create an order
        form = NetcashForm(initial={
            'p3': 'description',
            'p4': 100,
        })
        reference = str(form.order.pk)

        self.assertFalse(data_handler.called)

        # ... user posts the form and pays the purchase on netcash.co.za site
        # ... then Netcash sends a notification to our Data URL

        response = self.client.post(self.gateway_url, {
           'TransactionAccepted': 'true',
           'Reference': reference,
           'RETC': '123',
           'Reason': '',
           'Amount': '100'
        })

        self.assertEqual(response.status_code, 200)

        order = NetcashOrder.objects.get(pk=reference)
        self.assertEqual(order.TransactionAccepted, True)
        self.assertEqual(order.Amount, 100)
        self.assertEqual(order.RETC, '123')
        self.assertEqual(order.gateway, self.gateway)
        self.assertEqual(order.request_ip, '127.0.0.1')

        self.assertTrue(data_handler.called)
        self.assertEqual(data_handler.order, order)

