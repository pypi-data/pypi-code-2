from django.test import TestCase
from django.core.urlresolvers import reverse

from netcash.models import NetcashGateway, NetcashOrder
from netcash.forms import NetcashForm

class NetcashTest(TestCase):

    def setUp(self):
        self.gateway = NetcashGateway.objects.all()[0]
        self.gateway_url = reverse('netcash_data', args = [self.gateway.secret])

    def test_invalid_data_request(self):
        response = self.client.post(self.gateway_url, {})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(NetcashOrder.objects.count(), 0)

    def test_invalid_gateway(self):
        response = self.client.post(self.gateway_url+'123', {})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(NetcashOrder.objects.count(), 0)

    def test_data_request(self):

        # this will create an order
        form = NetcashForm(initial={
            'p3': 'description',
            'p4': 100,
        })
        reference = str(form.order.pk)

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
