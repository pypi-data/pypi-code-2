#coding: utf-8
import random
import string
from datetime import datetime
from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site

def full_url(link):
    current_site = Site.objects.get_current()
    return current_site.domain + link

def data_url(gateway):
    return full_url(reverse('netcash_data', args=[gateway.secret]))

def random_secret():
    return "".join([random.choice(string.letters) for x in range(0,40)])


class NetcashGateway(models.Model):
    """ Secure settings for payment gateway """

    name = models.CharField(max_length=50, default='gateway')
    secret = models.CharField(max_length=40, editable=False,
                              help_text='Data URL secret')

    netcash_ip = models.IPAddressField('Netcash server ip address', null=True, blank=True,
                    help_text='If specified, the requests to Data URL would '
                    'be only considered valid if they came from this ip')

    def data_url(self):
        return data_url(self)

    def accept_url(self):
        return full_url(reverse('netcash_accept'))

    def reject_url(self):
        return full_url(reverse('netcash_reject'))

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = random_secret()

        return super(NetcashGateway, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Netcash gateway'
        verbose_name_plural = 'Netcash gateway settings'


class NetcashOrder(models.Model):

    # field names are not pep-08 in order to match Netcash API docs

    Reference = models.AutoField(primary_key=True,
                          help_text='This is the unique reference that have '
                          'been sent to Netcash in the original request')

    TransactionAccepted = models.NullBooleanField(default=None)
    CardHolderIpAddr = models.IPAddressField(u'Cardholder ip address', null=True, blank=True)
    Amount = models.DecimalField(decimal_places=2, max_digits=12, null=True, blank=True)

    Reason = models.CharField(max_length=255, null=True, blank=True,
                       help_text='If the transaction failed this is the reason '
                       'returned for the failure')

    RETC = models.CharField(max_length=25, null=True, blank=True,
                     help_text = "This is a code returned by the system for "
                    "this transaction. Should you need to make an "
                    "enquiry you will use this number to reference "
                    "this transaction")

    Extra1 = models.CharField(null=True, blank=True, max_length = 50)
    Extra2 = models.CharField(null=True, blank=True, max_length = 50)
    Extra3 = models.CharField(null=True, blank=True, max_length = 50)

    # utility fields
    created_at = models.DateTimeField(default=datetime.now)
    updated_at = models.DateTimeField(default=datetime.now)
    gateway = models.ForeignKey(NetcashGateway, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super(NetcashOrder, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'NetCash #%s (%s)' % (self.pk, self.created_at)

    class Meta:
        verbose_name = 'NetCash order'
        verbose_name_plural = 'NetCash orders'
