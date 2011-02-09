try:
    from hashlib import sha1
except ImportError:
    from sha import new as sha1
import time
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.utils import simplejson


class AuthKeyManager(models.Manager):

    def create_key(self, **kwargs):
        """
        Create AuthKey object and return its ID.
        """

        key = AuthKey()
        key.uid = kwargs.pop('uid')
        if 'expired' in kwargs:
            key.expired = kwargs.pop('expired')
        else:
            key.expired = datetime.now() + timedelta(seconds=settings.URLAUTH_AUTHKEY_TIMEOUT)

        if 'onetime' in kwargs:
            key.onetime = kwargs['onetime']

        source = '%s%d%d' % (settings.SECRET_KEY, time.time(), id({}))
        key.id = sha1(source).hexdigest()
        key.data = simplejson.dumps(kwargs)
        key.save()
        return key.id


class AuthKey(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    uid = models.PositiveIntegerField()
    expired = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    onetime = models.BooleanField(blank=True, default=True)
    data = models.TextField()

    objects = AuthKeyManager()

    def __unicode__(self):
        return 'AuthKey #%s' % self.id

    @property
    def extra(self):
        return simplejson.loads(self.data)
