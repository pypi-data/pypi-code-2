import time
import datetime

from django.db import models
from api_auth.utils import config


def time_limit():
    timestamp_limit = time.time() - config('timeout')
    return datetime.datetime.fromtimestamp(timestamp_limit)


class ValidManager(models.Manager):
    def get_query_set(self):
        q = super(ValidManager, self).get_query_set()
        return q.filter(timestamp__gt=time_limit())


class NonceManager(models.Manager):
    def delete_old(self):
        q = super(NonceManager, self).get_query_set()
        return q.filter(timestamp__lt=time_limit()).delete()


class Nonce(models.Model):
    """
    This model keeps track of used nonces if API_AUTH_NONCE is True.
    * value - the nonce value that is a random string matching the
              ^[a-zA-Z0-9\-]$ regular expression.
    * consumer_key - the "public" key used to identify the consumer
    * timestamp - the number of seconds since January 1, 1970 GTM
                  used to test if a nonce is valid or not.
                  If a nonce is older than API_AUTH_TIMEOUT seconds
                  it's considered valid.
    """

    value = models.CharField(max_length=64)
    consumer_key = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = NonceManager()
    valid = ValidManager()

    def __unicode__(self):
        return self.value

    def status(self):
        return self.timestamp > time_limit()
    status.boolean = True