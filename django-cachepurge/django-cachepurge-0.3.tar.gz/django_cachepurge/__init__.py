# -*- coding: utf-8 -*-
from urlparse import urlsplit
from django.db.models import signals
from threading import currentThread
from django.core.urlresolvers import NoReverseMatch

_urls_to_purge = {}

def add_purge_url(url):
    if url is None:
        return

    if isinstance(url, basestring):
        parsed = urlsplit(url)
        if parsed.scheme != '' or parsed.netloc != '':
            # Only accept relative url, i.e. no 'http://...'
            return

    _urls_to_purge.setdefault(currentThread(), set()).add(url)

def get_urls():
    return _urls_to_purge.get(currentThread(), set())

def clear_urls():
    try:
        del _urls_to_purge[currentThread()]
    except KeyError:
        pass

def purge_instance_urls(sender, instance, **kwargs):
    """ callback for django post_save / post_delete signal
    request url purge when a model is changed or deleted
    """
    if getattr(instance, 'get_absolute_url', None) is not None:
        try:
            add_purge_url(instance.get_absolute_url())
        except NoReverseMatch:
            pass

    if getattr(instance, 'get_purge_urls', None) is not None:
        for url in instance.get_purge_urls():
            add_purge_url(url)

def register_model(sender, **kwargs):
    """ register post_save / post_delete callback for models with appropriate
    methods
    """
    if (getattr(sender, 'get_absolute_url', None) is None
        and getattr(sender, 'get_purge_urls', None) is None):
        return

    signals.post_save.connect(purge_instance_urls, sender=sender)
    signals.post_delete.connect(purge_instance_urls, sender=sender)

signals.class_prepared.connect(register_model)
