from django.test import TestCase
from django.db.models import Model
from django.db import IntegrityError
from ipyfield.models import IPyField
from IPy import IP


class DummyModel(Model):
    field = IPyField()
    null_field = IPyField(null=True)

    def __str__(self):
        return '<DummyModel %s>' % self.pk

    __repr__ = __str__

class IPyFieldTests(TestCase):

    def setUp(self):
        self.obj = DummyModel()

    def test_empty(self):
        self.assertEqual(None, self.obj.field)

    def test_iptype(self):
        self.obj.field = '127.0.0.1'
        self.assertEqual(self.obj.field.iptype(),'PRIVATE')
        self.obj.field = '100.80.90.100'
        self.assertEqual(self.obj.field.iptype(), 'PUBLIC')


    def test_lookups_in_CIDR(self):
        ip_block = IP('127.0.0.0/28')
        [DummyModel.objects.create(field=ip) for ip in ip_block]
        self.assertEqual(16, len(ip_block), DummyModel.objects.count())
        self.assertTrue(DummyModel.objects.count() > 
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30'))\
               .count())
        self.assertEqual(4, DummyModel.objects.filter(
               field__in=IP('127.0.0.0/30')).count())
        # testing lookups work with str as __in param rather than 
        # requiring an IP instance
        self.assertQuerysetEqual(
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30')),
               [repr(o) for o in DummyModel.objects.filter(
                                            field__in='127.0.0.0/30')])

        self.assertQuerysetEqual(
               DummyModel.objects.filter(field__in=IP('127.0.0.0/30')),
               [repr(o) for o in DummyModel.objects.filter(
                               field__in='127.0.0.0/255.255.255.252')])


    def test_null_values(self):
        with self.assertRaises(IntegrityError):
            # non-null field should require value
            DummyModel.objects.create()
        # null field is fine unspecified
        DummyModel.objects.create(field='1.1.1.1')

    def test_ipv6_support(self):
        obj = DummyModel.objects.create(field='2001:dead:beef::1')
        self.assertEqual(obj.field.version(), 6)


