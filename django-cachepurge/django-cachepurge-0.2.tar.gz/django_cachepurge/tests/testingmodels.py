# -*- coding: utf-8 -*-
"""Models we want only for tests
"""
from django.db import models
from django.http import HttpResponse

class NoUrlModel(models.Model):
    """ This model has no url, it should not trigger any purge
    """
    title = models.CharField(max_length=255)

    class Meta:
        app_label = 'cachepurge_test_app'

class UrlModel(models.Model):
    """ This model has urls, it can be purged
    """
    title = models.CharField(max_length=255)

    class Meta:
        app_label = 'cachepurge_test_app'

    def get_absolute_url(self):
        return '/content/%d' % self.pk

    def get_purge_urls(self):
        return ['/some/related/url']

def edit_url_model(request, pk):

    instance = UrlModel.objects.get(pk=int(pk))
    title = request.POST['title']
    instance.title = title
    instance.save()
    return HttpResponse('edited model %s' % pk,
                        mimetype='text/plain')

class OnlyPurgeUrls(models.Model):
    """ this model doesn't have get_absolute_url, only get_purge_urls. Useful
    for join models, for example.
    """

    title = models.CharField(max_length=255)

    class Meta:
        app_label = 'cachepurge_test_app'

    def get_purge_urls(self):
        return ['/some/other/url']

