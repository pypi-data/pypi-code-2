# Copyright (c) 2010 by Manuel Saelices
#
# This file is part of django-urlresolvers.
#
# django-urlresolvers is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-urlresolvers is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-urlresolvers.  If not, see <http://www.gnu.org/licenses/>.

from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import clear_url_caches
from django.utils.importlib import import_module


class ViewNotFound(Exception):
    pass


_registry = {}


def register_view(view_func, label=None, params=None):
    view_key = '%s.%s' % (view_func.__module__, view_func.__name__)
    _registry[view_key] = {
        'label': label or view_func.__name__,
        'view': view_func,
        'params': params or {},
    }


def get_view_info(view_path):
    for view, view_info in get_registered_views():
        if view_path == view:
            return view_info
    raise ViewNotFound('View with path %s not found' % view_path)


def get_registered_views():
    return _registry.items()


def autodiscover_views():
    import imp

    for app in settings.INSTALLED_APPS:
        try:
            app_path = import_module(app).__path__
        except AttributeError:
            continue

        # use imp.find_module to find the app's forms.py
        try:
            imp.find_module('views', app_path)
        except ImportError:
            continue

        # import the app's views.py file
        views_module = import_module('%s.views' % app)
        views_to_register_func = getattr(views_module, 'views_to_register', None)
        if views_to_register_func and callable(views_to_register_func):
            views_to_register = views_to_register_func()
            for reg_item in views_to_register:
                if isinstance(reg_item, (tuple, list)):
                    view_func, label = reg_item
                    register_view(view_func, label)
                else:
                    view_func = reg_item['view']
                    label = reg_item['label']
                    params = reg_item.get('params', None)
                    register_view(view_func, label, params)


def get_dbresolver_patterns():
    from dbresolver.models import URLPattern
    urlpatterns = []
    for urlpattern in URLPattern.objects.all():
        if urlpattern.view_params:
            kwargs = urlpattern.view_params
        else:
            kwargs = None
        dburl = url(urlpattern.get_regex(), urlpattern.view_path, kwargs)
        dburl.is_dbresolver = True  # mark this pattern to invalidate it when DB is changed
        urlpatterns.append(dburl)
    dburlpatterns = patterns('', *urlpatterns)
    try:
        iter(dburlpatterns)
    except TypeError:
        raise ImproperlyConfigured("dbresolver doesn't have any patterns in it")
    return dburlpatterns


def reload_urlpatterns(sender, instance, **kwargs):
    proj_urls = import_module(settings.ROOT_URLCONF)
    proj_urls.urlpatterns = [up for up in proj_urls.urlpatterns if not hasattr(up, 'is_dbresolver')]
    proj_urls.urlpatterns += get_dbresolver_patterns()
    clear_url_caches()
