# modelmanager.py
#
# Copyright (C) 2009-2011 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
ModelManager machinery for the softwarefabrica.django.director django application.

Copyright (C) 2009-2011 Marco Pantaleoni. All rights reserved.

@author: Marco Pantaleoni
@copyright: Copyright (C) 2009-2011 Marco Pantaleoni
"""

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2009-2011 Marco Pantaleoni"
__license__   = "GPL v2"

from django.db import models

from softwarefabrica.django.common.models import *
#from softwarefabrica.django.common.views import *
from softwarefabrica.django.director.views import *

import logging

def _app_label_from_name(app_name):
    return app_name.rsplit('.', 1)[-1]

def _lookup_model(app_name, model_name):
    """
    Return the ``model`` class given ``app_name`` and ``model_name``.
    WARNING: ``app_name`` is not an "app label", but a fully qualified name
    (with all the package components for namespace packages).
    """
    from django.db.models.loading import get_apps, get_models
    apps = get_apps()
    for app in get_apps():
        full_app_name = app.__name__.rsplit('.', 1)[0]
        if full_app_name != app_name:
            continue
        assert full_app_name == app_name
        model_list = get_models(app)
        for model in model_list:
            opts = model._meta
            if opts.object_name == model_name:
                return model
    return None

def _lookup_model_from_fullname(full_model_name):
    """
    Return the ``model`` class from the fully qualified model name.
    """
    return _lookup_model(*full_model_name.rsplit('.', 1))

def _lookup_model_from_applabel(app_label, model_name):
    from django.contrib.contenttypes.models import ContentType
    assert app_label and model_name
    c_type = ContentType.objects.get(app_label=app_label, model=model_name)
    return c_type.model_class()

def _fullname_from_model(model):
    assert issubclass(model, models.Model)
    app_name = model.__module__.rsplit('.', 1)[0]
    app_label = _app_label_from_name(app_name)
    #model_name = model._meta.object_name.lower()
    model_name = model._meta.object_name
    full_model_name = '%s.%s' % (app_name, model_name)
    return full_model_name

class ViewMapperError(Exception):
    pass

class ViewMapping(object):
    """
    Represents a tuple:

      (short name, Django url name, urlconf entry, view function).
    """
    def __init__(self, view_mapper, view_name, canonical_name, view_function,
                 urlpattern,
                 urlconf_view_name=None,
                 is_instance_view=True):
        """
        `view_name` is the short name of the ViewMapping.
        The `view_name` is also used as a component in the urlconf view name.

        The `canonical_name` is the standard short view name for
        default views, like 'absolute' for base detail view (as returned
        by get_absolute_url(), 'list' for list view (as returned by
        get_list_url(), 'create', 'detail', 'edit', 'delete'.

        The `canonical_name` is also used to build the
        url function name (as in get_*absolute*_url()).
        """
        assert isinstance(view_mapper, ViewMapper)
        assert isinstance(view_name, basestring)
        assert isinstance(canonical_name, basestring)
        assert callable(view_function)
        self.view_mapper       = view_mapper
        self.short_name        = view_name
        self.canonical_name    = canonical_name
        self.view_function     = view_function
        self.urlpattern        = urlpattern
        self.urlconf_view_name = urlconf_view_name
        self.is_instance_view  = is_instance_view
        self._trace            = False

        self.view_mapper._add_mapping(self, delete=False)

        #self._register_urlpattern()
        self._register_get_url_function()
        if self.view_function:
            self.view_function.mapping = self

    def __repr__(self):
        return "<ViewMapping model:%s view:%s>" % (self.manager.model,
                                                   self.short_name)

    @property
    def manager(self):
        """(property) - ModelManager for this mapping."""
        return self.view_mapper.manager

    @property
    def model(self):
        """(property) - Django models.Model for this mapping."""
        return self.view_mapper.manager.model

    def __call__(self, request, *args, **kwargs):
        """Proxy method for the actual view function."""
        if self._trace:
            logging.debug("view %r called (args:%r, kwargs:%r)" % (self.urlconf_view_name, args, kwargs))
        if self.view_function and callable(self.view_function):
            return self.view_function(request, *args, **kwargs)
        logging.warn("view function not installed for %r (args:%r, kwargs:%r)" % (self.urlconf_view_name, args, kwargs))
        raise ViewMapperError("view function undefined for %r" % self)

    def set_tracing(self, enable):
        """Enable or disable logging of view invocations."""
        self._trace = enable
        return self

    def _get_urlpatterns(self, urlconf=None):
        """Return Django urlpatterns object."""
        return self.view_mapper._get_urlpatterns(urlconf)

    def _get_url_function_name(self):
        """
        Return the get_*_url() method *NAME*, which is in fact:
            "get_<CANONICALNAME>_url"
        """
        return 'get_%s_url' % self.canonical_name

    def _get_instance_url_function(self):
        """
        Return the get_*_url() method implementation, for instance-based views
        (those receiving an instance, like 'view', 'detail', 'edit', 'delete').
        The underlying view *must* expect an `object_id` argument, with the
        instance primary key.
        """
        return self.view_mapper._get_instance_url_function(self.short_name,
                                                           self.canonical_name,
                                                           self.urlconf_view_name)
    def _get_model_url_function(self):
        """
        Return the get_*_url() method implementation, for class/model-wide
        views (those not receiving an instance, but operating on collections,
        like 'list' and 'create' views).
        """
        return self.view_mapper._get_model_url_function(self.short_name,
                                                        self.canonical_name,
                                                        self.urlconf_view_name)

    def _register_urlpattern(self):
        """
        Register the mapping/view inside Django URL dispatcher.
        
        We register the mapping itself as the view function inside
        Django URL dispatcher, as this allows a level of indirection:
        it's possible to change the underlying view function without
        reconfiguring the URL dispatcher, and it's possible to easily
        trace calls to the view.
        """
        urlpatterns = self._get_urlpatterns()
        urlpatterns += patterns('',
                                url(self.urlpattern,
                                    self,
                                    name=self.urlconf_view_name))
        return self

    def _register_get_url_function(self):
        """Add the proper get_*_url() method to the Django models.Model."""
        url_function_name = self._get_url_function_name()
        if self.is_instance_view:
            url_function = self._get_instance_url_function()
        else:
            url_function = self._get_model_url_function()
        if not hasattr(self.model, url_function_name):
            setattr(self.model, url_function_name, url_function)
        return self

class ViewMapper(object):
    """
    Handled creation and registration of views for Django models.

    It creates appropriate entries in urlconf and adds the
    relevant get_*_url() methods to the model.

    It is designed to be fully reconfigurable by overriding a
    selection of its methods (where the constructor parameters are not
    sufficient).
    """

    class ViewParams(object):
        def __init__(self, view_name,
                     urlpattern,
                     view_function=None, view_class=None,
                     urlconf_view_name=None,
                     is_instance_view=True,
                     canonical_view_name=None):
            self.view_name           = view_name
            self.urlpattern          = urlpattern
            self.view_function       = view_function
            self.view_class          = view_class
            self.urlconf_view_name   = urlconf_view_name
            self.is_instance_view    = is_instance_view
            self.canonical_view_name = canonical_view_name or self.view_name

        def __repr__(self):
            return "<ViewParams for view_name:%r>" % self.view_name

    DEFAULT_SPECS = (
        ViewParams('list',   '^%(url_prefix)s%(object_name)s/$',                                           view_class=ListObjectView,   is_instance_view=False),
        ViewParams('create', '^%(url_prefix)s%(object_name)s/%(create)s/$',                                view_class=CreateObjectView, is_instance_view=False),
        ViewParams('view',   '^%(url_prefix)s%(object_name)s/(?P<object_id>[a-zA-Z0-9_\-]+)/$',            view_class=DetailObjectView, is_instance_view=True, canonical_view_name='absolute'),
        #ViewParams('detail', '^%(url_prefix)s%(object_name)s/(?P<object_id>[a-zA-Z0-9_\-]+)/%(detail)s/$', view_class=DetailObjectView, is_instance_view=True),
        ViewParams('edit',   '^%(url_prefix)s%(object_name)s/(?P<object_id>[a-zA-Z0-9_\-]+)/%(edit)s/$',   view_class=UpdateObjectView, is_instance_view=True),
        ViewParams('delete', '^%(url_prefix)s%(object_name)s/(?P<object_id>[a-zA-Z0-9_\-]+)/%(delete)s/$', view_class=DeleteObjectView, is_instance_view=True),
    )

    def __init__(self, manager,
                 specs=None,
                 views={}, urlpatterns={},
                 views_constructors_args={},
                 url_prefix=None, url_name_prefix=None,
                 view_names_overrides={},
                 full_url_prefix=False,
                 full_urlname_prefix=False):
        """
        `specs` is a tuple containing ViewMapper.ViewParams instances as
        pecifications for default view mappings to create. If not specified,
        ViewMapper.DEFAULT_SPECS is used.

        `views` is an optional mapping `view_name` -> `view_function`.
        It takes precedence over the view function specified in `specs`.

        `urlpatterns` is an optional mapping `view_name` -> `urlpattern`.
        It takes precedence over the url pattern specified in `specs`.
        If a value contains %(NAME)s formatting, it is expanded using the
        dict returned by `_get_view_dict()`.

        `url_prefix` is used as the prefix in url pattern construction (followed
        by default by the class name). It defaults to the app_label.

        `url_name_prefix` is used as the prefix when constructing the urlconf
        view name (name of the url as used by Django named urls, the `name`
        parameter to url()).
        It is followed by default by "-<model_name>-<view_name>".
        (see _get_model_url_function() and _get_urlconf_view_name()).

        `view_names_overrides` is an optional mapping overriding the
        view dict used in constructing url patterns and urlconf view names.
        """
        from django.utils.datastructures import SortedDict
        import copy
        assert isinstance(manager, ModelManager)
        self.manager               = manager
        self.url_prefix            = url_prefix
        self.url_name_prefix       = url_name_prefix
        self.model_url_name_prefix = None
        self.specs                 = list(copy.deepcopy(specs or self.DEFAULT_SPECS))
        self.params_default        = SortedDict()
        self.views                 = views or {}
        self.urlpatterns           = urlpatterns or {}
        self.views_constructors_args = views_constructors_args or {}
        self.view_names_overrides  = view_names_overrides
        self.full_url_prefix       = full_url_prefix
        self.full_urlname_prefix   = full_urlname_prefix
        self._mappings             = []
        self._mapping_by_name      = {}
        self._base_mappings_created = False

        for spec in self.specs:
            assert isinstance(spec, ViewMapper.ViewParams)
            self.params_default[spec.view_name] = copy.deepcopy(spec)

        self._set_url_prefixes()
        #self._make_base_mappings()

    def __repr__(self):
        return "<ViewMapper model:%s>" % self.manager.model

    @property
    def model(self):
        """(property) - Django models.Model for this mapper."""
        return self.manager.model

    @property
    def mappings(self):
        """Return ViewMapping instances for this ViewMapper."""
        return self._mappings

    def get_mapping(self, name):
        """Return ViewMapping by name."""
        assert isinstance(name, basestring)
        return self._mapping_by_name.get(name, None)

    def delete_mapping(self, mapping_or_name):
        """
        Remove an existing ViewMapping.

        @todo: remove/replace the corresponding Django URL dispatcher entry.
        """
        if isinstance(mapping_or_name, basestring):
            old_mapping = self._mapping_by_name.get(mapping_or_name, None)
        else:
            old_mapping = mapping_or_name
        self._mappings.remove(old_mapping)
        self._mapping_by_name[old_mapping.short_name] = None
        del self._mapping_by_name[old_mapping.short_name]
        return self

    def _add_mapping(self, mapping, delete=True):
        """
        Add the given mapping to this mapper.
        If there is a previous mapper with the same name,
        an error is raised if `deleted` is False, otherwise if
        `deleted` is True, it is replaced by the new one.

        @todo: remove/replace the corresponding Django URL dispatcher entry,
        when a mapping is replaced.
        """
        assert isinstance(mapping, ViewMapping)
        if mapping not in self._mappings:
            old_mapping = self._mapping_by_name.get(mapping.short_name, None)
            if old_mapping is not None:
                if delete:
                    self.delete_mapping(old_mapping)
                else:
                    raise ViewMapperError("a mapping with the name %r is already present in %s" % (mapping.short_name, self))
            self._mappings.append(mapping)
            self._mapping_by_name[mapping.short_name] = mapping
        return self

    def get_url(self, view_name, *args, **kwargs):
        """Return the URL for the view named `view_name`."""
        from django.core.urlresolvers import reverse
        mapping = self.get_mapping(view_name)
        assert isinstance(mapping, ViewMapping)
        return reverse(mapping.urlconf_view_name, *args, **kwargs)

    def list_view_url(self, *args, **kwargs):
        """Return the URL for the 'list' view."""
        return self.get_url('list', *args, **kwargs)
    def create_view_url(self, *args, **kwargs):
        """Return the URL for the 'create' view."""
        return self.get_url('create', *args, **kwargs)
    def view_url(self, *args, **kwargs):
        """Return the URL for the 'view' (absolute) view."""
        return self.get_url('view', *args, **kwargs)
    def detail_url(self, *args, **kwargs):
        """Return the URL for the 'detail' view."""
        return self.get_url('detail', *args, **kwargs)
    def edit_view_url(self, *args, **kwargs):
        """Return the URL for the 'edit' view."""
        return self.get_url('edit', *args, **kwargs)
    def delete_view_url(self, *args, **kwargs):
        """Return the URL for the 'delete' view."""
        return self.get_url('delete', *args, **kwargs)

    def _get_view_mapping_class(self, view_name, canonical_view_name):
        """Return the ViewMapping subclass to use to create instances."""
        return ViewMapping

    def _get_urlresolver(self, urlconf=None):
        """Return Django url resolver object."""
        from django.core import urlresolvers
        return urlresolvers.get_resolver(urlconf)
    
    def _get_urlpatterns(self, urlconf=None):
        """Return Django urlpatterns object."""
        from django.core import urlresolvers
        return urlresolvers.get_resolver(urlconf).urlconf_module.urlpatterns

    def _get_instance_url_function(self, view_name, canonical_view_name, urlconf_view_name):
        """
        Return the get_*_url() method implementation, for instance-based views
        (those receiving an instance, like 'view', 'detail', 'edit', 'delete').
        The underlying view *must* expect an `object_id` argument, with the
        instance primary key.
        """
        def get_url_function(self):
            return (urlconf_view_name, (), { 'object_id': self.pk })
        get_url_function = models.permalink(get_url_function)
        return get_url_function

    def _get_model_url_function(self, view_name, canonical_view_name, urlconf_view_name):
        """
        Return the get_*_url() method implementation, for class/model-wide
        views (those not receiving an instance, but operating on collections,
        like 'list' and 'create' views).
        """
        def get_url_function(cls):
            return (urlconf_view_name, (), {})
        get_url_function = models.permalink(get_url_function)
        get_url_function = classmethod(get_url_function)
        return get_url_function

    def register_urlpatterns(self):
        """Register urlpatterns in Django for all the ViewMapping instances
        in this ViewMapper."""
        for mapping in self.mappings:
            assert isinstance(mapping, ViewMapping)
            mapping._register_urlpattern()
        return self

    def getViewParams(self, view_name):
        """Get ViewMapper.ViewParams for the view named `view_name`."""
        for vparams in self.specs:
            assert isinstance(vparams, ViewMapper.ViewParams)
            if vparams.view_name == view_name:
                return vparams
        return None

    def delViewParams(self, view_name):
        """Remove the ViewMapper.ViewParams instance for the view named `view_name`."""
        for i in range(0, len(self.specs)):
            vp = self.specs[i]
            assert isinstance(vp, ViewMapper.ViewParams)
            if vp.view_name == view_name:
                del self.specs[i]
                return self
            i += 1
        return self

    def setViewParams(self, vparams):
        """Set/add a ViewMapper.ViewParams instance."""
        assert isinstance(vparams, ViewMapper.ViewParams)
        for i in range(0, len(self.specs)):
            vp = self.specs[i]
            assert isinstance(vp, ViewMapper.ViewParams)
            if vp.view_name == vparams.view_name:
                self.specs[i] = vparams
                return self
            i += 1
        self.specs.append(vparams)
        return self

    def setViewParam(self, view_name, param, value):
        """Set view parameter named `param` to `value` in ViewMapper.ViewParams
        for the view named `view_name`."""
        vparams = self.getViewParams(view_name)
        assert isinstance(vparams, ViewMapper.ViewParams)
        setattr(vparams, param, value)
        return self

    def make_view_mapping(self, view_name, canonical_view_name, view_function,
                          urlpattern, is_instance_view, urlconf_view_name=None):
        """
        Return/register a new ViewMapping instance.

        Variable expansion is performed on `urlconf_view_name` and `urlpattern`.
        """
        if view_function is False:
            return None
        view_function = view_function or self.views.get(view_name, self.views.get(canonical_view_name, None))
        # NOTE: we have to repeat the `False` check, since the value could be different
        if view_function is False:
            return None
        assert view_function is not None
        viewmapping_class = self._get_view_mapping_class(view_name, canonical_view_name)
        view_dict = self._get_view_dict(view_name, canonical_view_name)
        urlconf_view_name = urlconf_view_name or self._get_urlconf_view_name(view_name, canonical_view_name)
        if '%(' in urlconf_view_name:
            urlconf_view_name = urlconf_view_name % view_dict
        if '%(' in urlpattern:
            urlpattern = urlpattern % view_dict
        logging.debug("adding view mapping for view:%r pattern:%r urlconf-name:%r (view function:%r)" % \
                      (view_name, urlpattern, urlconf_view_name, view_function))
        return viewmapping_class(view_mapper=self,
                                 view_name=view_name, canonical_name=canonical_view_name,
                                 view_function=view_function,
                                 urlpattern=urlpattern, urlconf_view_name=urlconf_view_name,
                                 is_instance_view=is_instance_view)

    def create_views(self):
        """Create related base views (ViewMapping instances) (those defined
        through the `specs` constructor parameter)."""
        return self._make_base_mappings()

    def _make_base_mappings(self):
        """
        Create ViewMapping instances for views defined through the `specs`
        constructor parameter (hence also for default ones: 'list', 'create',
        'view', 'detail', 'edit', 'delete').
        """
        if self._base_mappings_created:
            return self
        #for vparam in self.params_default.values():
        for vparam in self.specs:
            assert isinstance(vparam, ViewMapper.ViewParams)

            urlconf_view_name = vparam.urlconf_view_name

            view_function = self.views.get(vparam.view_name, self.views.get(vparam.canonical_view_name, vparam.view_function))
            if view_function is False:
                logging.debug("view %s skipped for %r per user request" % (vparam.view_name, self))
                continue
            if (view_function is None) and not issubclass(self.model, CommonModel):
                logging.warn("Automatic views are supported only for CommonModel subclasses. Skipping %r for %s" % (vparam.view_name, self))
                continue
            view_class = vparam.view_class
            if (view_function is None) and issubclass(self.model, CommonModel) and view_class:
                const_args = dict(model = self.model)
                const_args.update(self.views_constructors_args.get(vparam.view_name, {}))
                view_function = view_class(**const_args)
                view_function.MODEL = self.model
            assert view_function is not None
            urlpattern = self.urlpatterns.get(vparam.view_name, None) or vparam.urlpattern
            self.make_view_mapping(view_name=vparam.view_name,
                                   canonical_view_name=vparam.canonical_view_name,
                                   view_function=view_function,
                                   urlpattern=urlpattern,
                                   is_instance_view=vparam.is_instance_view,
                                   urlconf_view_name=urlconf_view_name)
        self._base_mappings_created = True
        return self

    def _set_url_prefixes(self):
        """
        Adjust or set default values for `url_prefix` and `url_name_prefix`,
        if not provided or not normalized.
        """
        if self.url_prefix is None:
            if self.full_url_prefix:
                self.url_prefix = '%s' % self.manager.app_name
                self.url_prefix = self.url_prefix.replace('.', '/')
            else:
                self.url_prefix = '%s' % self.manager.app_label
        if (self.url_prefix != '') and (not self.url_prefix.endswith('/')):
            self.url_prefix += '/'
        if self.url_name_prefix is None:
            if self.full_urlname_prefix:
                self.url_name_prefix = '%s' % self.manager.app_name
                self.url_name_prefix = self.url_name_prefix.replace('.', '-')
            else:
                self.url_name_prefix = '%s' % self.manager.app_label
        if (self.url_name_prefix != '') and (not self.url_name_prefix.endswith('-')):
            self.url_name_prefix += '-'
        logging.debug("url_prefix:%r url_name_prefix:%r" % (self.url_prefix, self.url_name_prefix))
        self.model_url_name_prefix = self._get_model_url_name_prefix()
        return self

    def _get_model_url_name_prefix(self):
        """Get the model-specific url name prefix."""
        class_name = self.manager.opts.object_name
        return '%s%s' % (self.url_name_prefix, class_name.lower())

    def _get_view_dict(self, view_name, canonical_view_name):
        """
        `view_name` is the short name of the ViewMapping.
        The `view_name` is also used as a component in the urlconf view name.

        The `canonical_view_name` is the standard short view name for
        default views, like 'absolute' for base detail view (as returned
        by get_absolute_url(), 'list' for list view (as returned by
        get_list_url(), 'create', 'detail', 'edit', 'delete'.

        The `canonical_view_name` is also used to build the
        url function name (as in get_*absolute*_url()).
        """
        #assert isinstance(mapping, ViewMapping)
        #view_name           = mapping.short_name
        #canonical_view_name = mapping.canonical_name
        class_name = self.manager.opts.object_name
        assert isinstance(view_name, basestring)
        assert isinstance(canonical_view_name, basestring)
        default_view_dict = {
            'base_prefix': self.url_name_prefix,
            'prefix':      self.model_url_name_prefix,
            'url_prefix':  self.url_prefix,
            'app_label':   self.manager.app_label,
            'object_name': class_name.lower(),
            'view_name':   view_name,
            'canonical_view_name': canonical_view_name,
            'list':        'list',
            'create':      'create',
            'absolute':    'view',
            'view':        'view',
            'detail':      'detail',
            'edit':        'edit',
            'delete':      'delete',}
        default_view_dict[canonical_view_name] = view_name
        view_dict = dict(default_view_dict)
        view_dict.update(self.view_names_overrides)
        return view_dict

    def _get_urlconf_view_name(self, view_name, canonical_view_name):
        """Return the name used for the named url in Django URL dispatcher."""
        view_dict = self._get_view_dict(view_name, canonical_view_name)
        return '%(prefix)s-%(view_name)s' % view_dict

class ModelManager(object):
    """
    The ModelManager handles registration of urls, views and models in the admin.
    """

    _managers                = []
    _manager_by_model        = {}
    _manager_by_fullname     = {}
    _managers_by_app_name    = {}
    _registered_apps         = []

    def __init__(self, model,
                 register_admin=True, register_views=True,
                 specs=None, views={}, urlpatterns={},
                 views_constructors_args={},
                 url_prefix=None,
                 url_name_prefix=None,
                 view_names_overrides={},
                 full_url_prefix=False,
                 full_urlname_prefix=False,
                 menu=True,
                 create_link=True):
        """
        `specs` is a tuple containing ViewMapper.ViewParams instances as
        pecifications for default view mappings to create. If not specified,
        ViewMapper.DEFAULT_SPECS is used.
        """
        from django.utils.datastructures import SortedDict
        assert issubclass(model, models.Model)
        self.model                = model
        self.register_admin       = register_admin
        self.register_views       = register_views
        self.specs                = specs or ViewMapper.DEFAULT_SPECS
        self.viewparams           = SortedDict()
        self.views                = views
        self.urlpatterns          = urlpatterns
        self.views_constructors_args = views_constructors_args
        self.url_prefix           = url_prefix
        self.url_name_prefix      = url_name_prefix
        self.view_names_overrides = view_names_overrides
        self.full_url_prefix      = full_url_prefix
        self.full_urlname_prefix  = full_urlname_prefix
        self.menu                 = menu
        self.create_link          = create_link

        self.view_mapper          = None

        self._admin_registered    = False
        self._views_registered    = False

        for spec in self.specs:
            assert isinstance(spec, ViewMapper.ViewParams)
            self.viewparams[spec.view_name] = spec

        if model not in ModelManager._manager_by_model:
            logging.debug("registering ModelManager for %s" % self.full_name)
            fullname = self.full_name
            ModelManager._manager_by_model[model]       = self
            ModelManager._manager_by_fullname[fullname] = self
            ModelManager._managers.append(self)

            if self.app_name not in ModelManager._registered_apps:
                ModelManager._registered_apps.append(self.app_name)
            managers_by_app_name = ModelManager._managers_by_app_name.get(self.app_name, [])
            if self not in managers_by_app_name:
                managers_by_app_name.append(self)
            ModelManager._managers_by_app_name[self.app_name] = managers_by_app_name
        else:
            logging.warn("A ModelManager for %s is already registered!" % self.full_name)
            print "A ModelManager for %s is already registered!" % self.full_name

        self.view_mapper = self._create_view_mapper()

    def __repr__(self):
        return "<ModelManager %s>" % self.model

    def _get_view_mapper_class(self):
        return ViewMapper

    def _create_view_mapper(self):
        logging.debug("creating ViewMapper for %s" % self.full_name)
        mapper_class = self._get_view_mapper_class()
        specs = self.viewparams.values()
        return mapper_class(manager=self, specs=specs, views=self.views,
                            urlpatterns=self.urlpatterns,
                            views_constructors_args=self.views_constructors_args,
                            url_prefix=self.url_prefix,
                            url_name_prefix=self.url_name_prefix,
                            view_names_overrides=self.view_names_overrides,
                            full_url_prefix=self.full_url_prefix,
                            full_urlname_prefix=self.full_urlname_prefix)

    def _register_admin(self):
        if self._admin_registered:
            logging.warn("admin registration for %s has already been performed" % self.full_name)
            return self
        if hasattr(self.model, 'Register_admin'):
            logging.debug("registering %s in admin" % self.full_name)
            self.model.Register_admin()
            self._admin_registered = True
        else:
            logging.debug("skipping admin registration for %s (no 'Register_admin' method)" % self.full_name)
        return self

    def _register_views(self):
        if self._views_registered:
            logging.warn("urlpatterns for %s have already been registered" % self.full_name)
            return self
        if self.view_mapper is None:
            self.view_mapper = self._create_view_mapper()
        assert isinstance(self.view_mapper, ViewMapper)
        self.view_mapper.create_views()
        self.view_mapper.register_urlpatterns()
        self._views_registered = True
        return self

    @property
    def opts(self):
        """(property) - Model._meta for the registered model"""
        return self.model._meta

    @property
    def full_name(self):
        """(property) - full model name for the registered model"""
        return _fullname_from_model(self.model)

    @property
    def app_name(self):
        """(property) - app_name for the registered model"""
        return self.model.__module__.rsplit('.', 1)[0]

    @property
    def model_name(self):
        """(property) - model_name for the registered model"""
        return self.model._meta.object_name

    @property
    def app_label(self):
        """(property) - app_label for the registered model"""
        #app_name = self.model.__module__.rsplit('.', 1)[0]
        #return _app_label_from_name(app_name)
        return self.model._meta.app_label

    @classmethod
    def Register(cls, model,
                 register_admin=True, register_views=True,
                 specs=None, views={}, urlpatterns={},
                 views_constructors_args={},
                 url_prefix=None,
                 url_name_prefix=None,
                 view_names_overrides={},
                 full_url_prefix=False,
                 full_urlname_prefix=False,
                 menu=True, create_link=True):
        """Create a ModelManager for the given Django model."""
        return cls(model=model,
                   register_admin=register_admin, register_views=register_views,
                   specs=specs, views=views, urlpatterns=urlpatterns,
                   views_constructors_args=views_constructors_args,
                   url_prefix=url_prefix, url_name_prefix=url_name_prefix,
                   view_names_overrides=view_names_overrides,
                   full_url_prefix=full_url_prefix,
                   full_urlname_prefix=full_urlname_prefix,
                   menu=menu, create_link=create_link)

    @classmethod
    def RegisterAdmin(cls):
        """Register in Django admin all models with a ModelManager."""
        for app_name in cls._registered_apps:
            managers = cls._managers_by_app_name.get(app_name, [])
            for manager in managers:
                assert isinstance(manager, ModelManager)
                if manager.register_admin:
                    manager._register_admin()
        return cls

    @classmethod
    def RegisterViews(cls):
        """Create URLconf entries and views for all models with a ModelManager."""
        for app_name in cls._registered_apps:
            managers = cls._managers_by_app_name.get(app_name, [])
            for manager in managers:
                assert isinstance(manager, ModelManager)
                if manager.register_views:
                    manager._register_views()
        return cls

    @classmethod
    def ManagersForApp(cls, app_name):
        """ModelManager instances for the app identified by `app_name`"""
        return cls._managers_by_app_name.get(app_name, [])

    @classmethod
    def FromModel(cls, model):
        """
        Return the ModelManager for the given model (either a models.Model or
        a string representing the "full model name"), or None.
        """
        if isinstance(model, basestring):
            return cls._manager_by_fullname.get(model, None)
        assert issubclass(model, models.Model)
        modelmanager = cls._manager_by_model.get(model, None)
        assert isinstance(modelmanager, ModelManager)
        return modelmanager

    @classmethod
    def FromAppLabelAndName(cls, app_label, model_name):
        """
        Return the ModelManager for the model identified by the
        given (app_label, model_name) pair, or None.
        """
        model = _lookup_model_from_applabel(app_label, model_name)
        app_name = model.__module__.rsplit('.', 1)[0]
        app_label = _app_label_from_name(app_name)
        full_model_name = '%s.%s' % (app_name, model_name)
        return cls.FromModel(fullname)

    @classmethod
    def FromAppNameAndName(cls, app_name, model_name):
        """
        Return the ModelManager for the model identified by the
        given (app_name, model_name) pair, or None.
        """
        model = _lookup_model(app_name, model_name)
        app_label = _app_label_from_name(app_name)
        full_model_name = '%s.%s' % (app_name, model_name)
        return cls.FromModel(fullname)
