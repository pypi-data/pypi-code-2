import logging
import warnings

import pkg_resources
from configobj import ConfigObj
from paste.registry import StackedObjectProxy, RegistryManager
from repoze.tm import make_tm
from tw.api import make_middleware as tw_middleware
from tw import framework as tw_framework

import rum
from rum import interfaces, util, exceptions
from rum.component import Component
from rum.controller import Controller
from rum.wsgiutil import RumRequest, HTTPNotFound, HTTPException, status_map
from rum.util import keywords_to_str, safe_issubclass
from rum.widgets import DEFAULT_WIDGETS
from rum.templating.base import BaseRenderer

__all__ = ["RumApp", "make_app"]
        

log = logging.getLogger(__name__)

DEBUG_WARN_MSG = """\
Debug mode is ON.
*** THIS POSES A SEVERE SECURITY HOLE! USE AT YOUR OWN RISK!!! ***
Remote code execution is possible via the web-based debugger and detailed
information about the system's configuration is given on errors.
Make sure your application cannot be accessed from the network.
"""

class RootController(Controller):
    def index(self):
        self.template = 'home'
        return {}

class RumApp(object):
    """
    Rum's WSGI interface and facade to all of Rum's functionallity.

    **Parameters:**
        ``config``
            A filename or a dictionary with the application's configuration.
            See :ref:`config` for details.
        ``full_stack``
            Is RumApp the only WSGI app in the stack? Set to False if you
            are providing needed middleware yourself
        ``debug``
            Enable for debug mode. **MUST** set to False on production.
        ``finalize``
            Set to False if you want to further configure the RumApp instance
            and depend on :attr:`rum.app`` pointing to the current app.
            **MUST** call :meth:`finalize` explicitly yourself when done and
            make sure it is really called (ie: in a ``finally`` clause).
        ``root_controller``
            A :class:`rum.interfaces.IController` implementation or a WSGI
            app that should be mounted at the root of the URL dispatch tree.

    To be able to configure the app programatically after it has been
    initialized you can pass the ``finalize = False`` parameter when
    instantiating it and call :meth:`rum.app.RumApp.finalize` when you're done.

    .. warning:: 

       It is mandatory that :meth:`finalize` is called or else bad things
       **will** happen.
    """
    controllerfactory = Component('rum.controllerfactory', default='default')
    repositoryfactory = Component("rum.repositoryfactory", default='default')
    viewfactory = Component('rum.viewfactory', default='default')
    router = Component('rum.router', default='default')
    policy = Component('rum.policy', default='default')
    jsonencoder = Component('rum.jsonencoder', default='default')
    translator = Component('rum.translator', default='default')
    request = StackedObjectProxy(name='rum Request', default=None)

    def __init__(self, config=None, full_stack=True, debug=False,
                 finalize=True, root_controller=RootController):
        self._finalized = False
        self._renderers = {}
        self.root_controller = root_controller
        self.config = self.load_config(
            config,
            full_stack=full_stack,
            debug=debug,
            )
        self.on_start_request = []
        self.on_end_request = []
        if self.config['debug']:
            map(log.warn, DEBUG_WARN_MSG.splitlines())
        self._setup(finalize)

    def add_middleware(self):
        """
        Wraps :meth:`wsgi_app` with needed middleware.

        Override this method to customize the way middleware is stacked.
        """
        config = self.config['middleware']
        if config['toscawidgets']['on']:
            self._add_tw_middleware()
        if config['transactions']['on']:
            self._add_tm_middleware()
        if config['evalexception']['on']:
            self._add_ee_middleware()
        self.wsgi_app = RegistryManager(self.wsgi_app)

    def _add_tw_middleware(self):
        self.wsgi_app = tw_middleware(self.wsgi_app, {
            'toscawidgets.middleware.inject_resources': False,
            'toscawidgets.framework.translator': self.translator.ugettext,
            })

    def _add_tm_middleware(self):
        def _commit_veto(environ, status, headers):
            # This tells repoze.tm2 to veto any transaction if we somehow
            # return a HTTP error response
            return not (200 <= int(status.split()[0]) < 400)
        self.wsgi_app = make_tm(self.wsgi_app, _commit_veto)

    def _add_ee_middleware(self):
        if self.config['debug']:
            try:
                from weberror.evalexception import EvalException
            except ImportError:
                log.error("WebError is not installed! You must install it "
                          "to enjoy debug mode in all its glory")
            else:
                self.wsgi_app = EvalException(self.wsgi_app)
        else:
            log.info("EvalException is only stacked if debug mode is on")

    def load_config(self, config, **defaults):
        """
        Loads and initilizes the configuration for this :class:`RumApp`
        """
        if config:
            if isinstance(config, basestring):
                import os
                if not os.path.exists(config):
                    raise exceptions.ConfigError(
                        "File %s could not be found" % config
                        )
            elif isinstance(config, dict):
                config = config.copy()
            config = ConfigObj(config, unrepr=True)
        else:
            config = {}
        for k,v in defaults.iteritems():
            config.setdefault(k, v)
        self._setup_i18n_config(config)
        self._setup_widgets_config(config)
        self._setup_middleware_config(config)
        self._setup_templating_config(config)
        config.update(config.pop('DEFAULT', {}))
        return config

    def _setup_i18n_config(self, config):
        i18n_config = {'locales': ['all']}
        user_config = config.get('rum.translator', {})
        i18n_config.update(user_config)
        config['rum.translator'] = i18n_config
        
    def _setup_templating_config(self, config):
        config.setdefault('templating', {}).setdefault('renderer', 'genshi')

    def _setup_widgets_config(self, config):
        widgets = DEFAULT_WIDGETS.copy()
        widgets.update(config.get('widgets', {}))
        for k,v in widgets.iteritems():
            if isinstance(v, basestring):
                widgets[k] = util.import_string(v)
        config['widgets'] = widgets

    def _setup_middleware_config(self, config):
        middleware_conf = config.setdefault('middleware', {})
        for k in 'transactions', 'toscawidgets', 'evalexception':
            middleware_conf.setdefault(k, {'on':config['full_stack']})

    def _setup(self, finalize):
        assert not self._finalized, "%r is already finalized" % self
        try:
            self.mounted_at().__enter__()
            self.repositoryfactory.load_resources()
            for rsrc, attrs in self.resources.iteritems():
                self.register(rsrc, attrs)
            self.connect_default_routes()
        finally:
            if finalize:
                self.finalize()

    def finalize(self):
        """
        When the `finalize` flag is False when initializing :class:`RumApp` this
        method **must** be called after the app has been manually tweaked after
        initialization.

        It is very important that this method is called.
        """
        assert not self._finalized
        self.add_middleware()
        self.on_start_request.append(self.router.activate)
        self.on_end_request.append(self.router.deactivate)
        self.on_end_request.append(self.repositoryfactory.cleanup)
        self._finalized = True
        self.mounted_at().__exit__()

    def call_in_context(self, func, *args, **kw):
        """
        Calls `func` with  `args` as positional and `kw` as keyword arguments
        inside the context of this app.

        It is neccesary to call this way any function that accesses any of the
        components accesible from this app when this app is not the current
        active app (ie: The one serving the request).

        If you get a traceback saying that :attr:`rum.app` is None when using
        this app the this is probably what you're looking for.

        .. warning::
            This is only here for compatibility with python < 2.6 (or python 2.5
            without "from __future__ import with_statement").
            It will be deprecated as soon as it is feasible to drop support
            for Python 2.4
        """
        warnings.warn(
            """
            This function will be deprecated as soon as 2.4 support can
            be dropped. Please use the "with" statement instead.
            """, DeprecationWarning, 2
            )
        ctx = self.mounted_at()
        ctx.__enter__()
        try:
            return func(*args, **kw)
        finally:
            ctx.__exit__()

    def connect_default_routes(self):
        """
        Connects default routes used by this app when not handling resources.

        Override this method if you want to register controllers at whatever
        URL point you need.
        """
        self.router.connect('root_i18n', '/:(lang).:(format)',
                            controller=self.root_controller,
                            requirements={'format':'[^\.]+'})
        self.router.connect('root', '/', controller=self.root_controller)

    def register(self, resource, attributes={}, prefix=None):
        """
        Registers URL endpoints to handle `resource` and a endpoints to handle
        each of the resources which are values of `attributes` with `resource`
        as a parent. The keys of the `attributes` dict are the remote names
        from which each value can be accessed from `resource`.

        Example::

            register(Person, dict(addresses=Address, jobs=Job))

        Will register `Person` at (usually) `/persons` and `Address` and
        `Job` at `/persons/${person_id}/addresses` and
        `/persons/${person_id}/jobs` respectively.
            
        All operations on `Address` and `Job` when accessed at these
        endpoints will have a particular `Person` as a parent.
        """
        log.debug("register: %r", locals())
        self.router.resource(
            resource=resource,
            prefix=prefix,
            )
        parent = resource
        for remote_name, resource in attributes.iteritems():
            self.router.resource(
                resource=resource,
                parent=parent,
                prefix=prefix,
                remote_name=remote_name,
                )


    def url_for(self, *args, **kw):
        return self.router.url_for(*args, **kw)
    url_for.__doc__ = interfaces.IRouter.url_for.__doc__

    def redirect_to(self, *args, **kw):
        """
        Isomorphic to :meth:`url_for` but issues an HTTP redirect to the
        resulting URL.
        The redirect code can be set with the `_code` keyword argument
        (`303 See Other` by default).

        If the ``_use_next`` flag is passed as a keyword arg. then it will try
        to use the URL the client provided through the _next_redirect arg. if
        provided, else it will use the URL that was requested explicitly.
        """
        code = kw.pop('_code', 303)
        use_next = kw.pop('_use_next', False)
        if use_next:
            url = self.request.next_redirect or self.router.url_for(*args, **kw)
        else:
            url = self.router.url_for(*args, **kw)
        raise status_map[code](location=url).exception


    def __call__(self, environ, start_response):
        #TODO: Probably use pyPubSub for events
        for listener in self.on_start_request:
            listener(self)
        try:
            return self.wsgi_app(environ, start_response)
        finally:
            for listener in self.on_end_request:
                listener(self)

    def wsgi_app(self, environ, start_response):
        registry = environ['paste.registry']
        request = RumRequest(environ)
        registry.register(self.request, request)
        registry.register(rum.app, self)
        try:
            return self.dispatch(request)(environ, start_response)
        except HTTPException, e:
            return e(environ, start_response)

        
    def dispatch(self, request):
        """
        Returns a controller to handle `request`. Raises a "404 Not Found" if
        no controller could be found.
        """
        match = self.router.dispatch(request.environ)
        if not match:
            raise HTTPNotFound().exception
        else:
            request.routes = keywords_to_str(match)
        controller = match['controller']()
        return controller
        
    def fields_for_resource(self, resource):
        return self.repositoryfactory.fields_for_resource(resource)
    def field_for_resource_with_name(self,resource,name):
        for f in self.fields_for_resource(resource):
            if f.name==name:
                return f
        raise KeyError

    
    fields_for_resource.__doc__ = interfaces.IRepositoryFactory.fields_for_resource.__doc__

    def names_for_resource(self, resource):
        return self.repositoryfactory.names_for_resource(resource)
    names_for_resource.__doc__ = interfaces.IRepositoryFactory.names_for_resource.__doc__

    def set_names(self, obj, singular, plural):
        return self.repositoryfactory.set_names(obj, singular, plural)
    set_names.__doc__ = interfaces.IRepositoryFactory.set_names.__doc__
    
    def get_view(self, resource, **kw):
        kw.update(resource=resource)
        return util.adapt_call(self.viewfactory, **kw)

    def __enter__(self):
        warnings.warn(
            "Using RumApp as a context manager is deprecated. Get one through "
            "the mounted_at() method", DeprecationWarning, 2)
        rum.app._push_object(self)
        return self

    def __exit__(self, type=None, value=None, traceback=None):
        warnings.warn(
            "Using RumApp as a context manager is deprecated. Get one through "
            "the mounted_at() method", DeprecationWarning, 2)
        rum.app._pop_object(self)

    @property
    def locale(self):
        return self.translator.active_locale

    @property
    def resources(self):
        return self.repositoryfactory.resources

    def render(self, data, possible_templates, renderer=None):
        """
        Renders the first template that can be loaded of `possible_templates`
        using the renderer named `renderer` with variables from the `data`
        dict.
        """
        renderer = renderer or self.config['templating']['renderer']
        if safe_issubclass(renderer, BaseRenderer):
            tw_framework.default_view = renderer.framework_name
        else:
            tw_framework.default_view = renderer
        return self._get_renderer(renderer).render(data, possible_templates)

    def _get_renderer(self, name):
        """
        Returns a plugin implementing :class:`rum.iterfaces.IRenderer` by the
        name ``name``.
        """
        renderer = None
        try:
            renderer = self._renderers[name]
        except KeyError:
            if safe_issubclass(name, BaseRenderer):
                log.debug("Found renderer %r", name)
                args = dict(self.config['templating'])
                renderer = util.adapt_call(name, **args)
                self._renderers[name] = renderer

            else:
                for ep in pkg_resources.iter_entry_points('rum.renderers'):
                    if ep.name == name:
                        log.debug("Found renderer %r", name)
                        args = dict(self.config['templating'])
                        renderer = util.adapt_call(ep.load(), **args)
                        self._renderers[name] = renderer
        if not renderer:
            raise LookupError("Could not find a renderer called %s" % name)
        return renderer
        

    def mounted_at(self, mount_point=''):
        """
        Sets up a dummy request so urls can be properly generated when using
        the app's services outside of the context of a request handled by Rum.

        Usage::

            with rum_app.mounted_at('/admin'):
                url = rum_app.url_for(obj=some_obj, action='edit')
                form = rum_app.viewfactory(SomeClass, action='new')
                etc ...

        This feature requires Python 2.6 or 2.5 with:
        "from __future__ import with_statement"
        """
        return RumContextManager(self, mount_point)

class RumContextManager(object):
    def __init__(self, app, mount_point):
        self.app = app
        self.mount_point = mount_point

    def __enter__(self):
        rum.app._push_object(self.app)
        dummy_req = RumRequest.blank('')
        dummy_req.script_name = self.mount_point
        self.app.request._push_object(dummy_req)
        self.app.router.activate()
        self.app.router.dispatch(dummy_req.environ)
        return self.app

    def __exit__(self, type=None, value=None, traceback=None):
        rum.app._pop_object(self.app)
        self.app.request._pop_object()
        self.app.router.deactivate()

        



def make_app(global_conf=None, **kw):
    from paste.deploy.converters import asbool
    conf = (global_conf or {}).copy()
    conf.update(kw)
    app = RumApp(
        config = conf.get('config'),
        full_stack = asbool(conf.get('full_stack', True)),
        debug = asbool(conf.get('debug', False)),
        )
    return app
