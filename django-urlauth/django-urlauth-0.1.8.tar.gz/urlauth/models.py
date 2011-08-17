import os
from binascii import hexlify
import time
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.utils import simplejson
from django.contrib.auth.models import User
from django.db.utils import IntegrityError

class URLAuthError(Exception):
    pass

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
            key.onetime = kwargs.pop('onetime')
        key.data = simplejson.dumps(kwargs)

        # Try 10 times to create AuthKey instance with unique PK
        for x in xrange(10):
            key.pk = hexlify(os.urandom(20))
            try:
                key.save(force_insert=True)
            except IntegrityError:
                key.pk = None
            else:
                break

        if not key.pk:
            raise URLAuthError('Could not create unique key')

        return key.id

    def wrap_url(self, url, **kwargs):
        """
        Create new authorization key, append it to the url and return modified url.
        """

        key_id = self.create_key(**kwargs)
        clue = '?' in url and '&' or '?'
        parts = url.rsplit('#', 1)
        if len(parts) > 1:
            url, hash = parts
            hash = '#%s' % hash
        else:
            hash = ''
        url = '%s%s%s=%s%s' % (url, clue, settings.URLAUTH_AUTHKEY_NAME, key_id, hash)
        return url


class AuthKey(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    uid = models.PositiveIntegerField(null=True)
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

    def get_user(self):
        if self.uid:
            return User.objects.get(pk=self.uid)
        else:
            return None
