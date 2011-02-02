import logging
from itertools import count

from peak.util.decorators import decorate_assignment, decorate_class
import routes

from rum.exceptions import RoutesException
from rum.genericfunctions import generic
from rum.util import adapt_call, safe_issubclass
from rum.wsgiutil import RumRequest
from rum import app
from copy import copy

__all__ = ["RumRouter", "resource_action", "get_resource_actions"]


log = logging.getLogger(__name__)

class DefaultController(object):
    def __call__(self, environ, start_response):

        next_app = adapt_call(app.controllerfactory, **app.request.routes)
        return next_app(environ, start_response)

# XXX: the router is *very* messy, *must* be cleaned up sometime soon and
#      optimized since it's a very hot path
class RumRouter(object):
    _route_args = frozenset(["parent", "resource", "remote_name", "prefix"])
    def __init__(self, always_scan=True):
        self._controllers = {} # str -> args
        self._controller_keys = {} # args -> str
        self._resource_reg = {}
        self._key_to_resource = {}
        self._resource_to_key = {}
        self._route_to_resource_dict = {}
        self._resource_to_route_dict = {}
        self._named_route_keys = {}
        self._serial = count(0)
        self.mapper = routes.Mapper(
            register=True,
            explicit=True,
            always_scan=always_scan,
            controller_scan = self._controllers.keys
            )
        self.mapper.minimization=True
        self._connect_resource_routes()
    
    def _resource_route_name(self, parent, member_action,prefix, format, lang, action_name):
        """
            Generate a name for the route
        """
        res=['resource']
        if format is not None:
            res.append('format')
        if lang is not None:
            res.append('lang')
        if prefix is not None:
            res.append('prefix')
        if member_action:
            res.append('member')
        if parent:
            res.append('parent')
        if self._is_default_action({'member_action': member_action, 'action':'action_name'}):
            action_name=''
        if action_name:
            res.append('action')
        return "_".join(res)
    
    
    def _is_default_action(self, kw):
        member_action = kw.get('id', None) is not None
        if member_action:
            default_action = 'show'
        else:
            default_action ='index'
        return kw.get('action', '')==default_action or not kw['action']
    
    def _resource_filter(self, kw):    
        parent= kw.get('parent', None)
        if parent:
            parent = self._key_to_resource.get(parent, parent)
        resource = kw.get('resource', None)
        resource = self._key_to_resource.get(resource, resource)
        
        #TODO: should enforce, that member routes are only generated when
        #member action and collection routes other wise
        member_action = kw.get('id', None) is not None
        is_default_action = self._is_default_action(kw)

        action = kw.get('action', '')
        prefix = kw.get('prefix', None)
        #parent_name = kw.get('parent_name', None)
        resource_name = kw.get('resource_name', None)
        remote_name = kw.get('remote_name', None)
        
        for class_ in resource.__mro__:
            resource = class_
            try:
                match_info = self._resource_to_route(prefix,
                    resource, parent, remote_name, action, member_action)
                break
            except KeyError:
                pass
        if not "match_info" in locals():
            raise RoutesException
        kw.update(match_info)
        kw.pop('resource', None)
        kw.pop('member_action', None)
        kw.pop('parent', None)
        parent_name = kw.get('parent_name', None)
        for k in ['parent_name', 'parent_id','id', 'prefix']:
            if kw.get(k, None) is None:
                kw.pop(k, None)
        kw.pop('remote_name', None)
        if is_default_action:
            kw.pop('action_name')
        return kw

    
    def _resource_conditions(self, environ, kw):
        parent_name=kw.get('parent_name', None)
        resource_name=kw.get('resource_name', None)
        prefix=kw.get('prefix', None)
        action_name=kw.get('action_name','')
        member_action='id' in kw
        method=environ['REQUEST_METHOD']
        try:
            resource_dict =self._route_to_resource(prefix=prefix,
                method=method, resource_name=resource_name,
                parent_name=parent_name,
                action_name=action_name,
                member_action=member_action)
        except KeyError, e:
            return False
        kw.update(resource_dict)
        if kw.get('parent_name',None):
            kw['remote_name']=kw.get('resource_name', None)
            #compat with older versions
        self._encode_resource(kw)
        return True
        
    def _connect_resource_routes(self):
        place_holder='place_holder'
        
        for prefix in (None, place_holder):
            for parent in (None, place_holder):
                for member_action in (False, True):
                    #First collection actions, as actions have precendence before ids
                    for action_name in ['',place_holder]:
                        for lang in (place_holder, None):
                            for format in (place_holder, None):
                                #order for format, lang is important (it is tested)
                                if lang and not format:
                                    continue
                                route=[]
                                if prefix:
                                    route.append("{prefix}/")
                                if parent:
                                    route.append("{parent_name}/{parent_id}/")
                                #     route.append("{remote_name}")
                                # else:
                                route.append("{resource_name}")
                                if member_action:
                                    route.append("/{id}")
                                if action_name:
                                    route.append("/{action_name}")
                                if lang:
                                    route.append(".{lang:\w+}")
                                if format:
                                    route.append(".{format:\w+}")

                                route_string="".join(route)
                                #route_name=adapt_call(self._resource_route_name,**locals())
                                route_name = self._resource_route_name(
                                    parent=parent,
                                    member_action=member_action,
                                    prefix=prefix,
                                    format=format,
                                    lang=lang,
                                    action_name=action_name)
                                key = self.connect(route_name, route_string,
                                    conditions=dict(function=self._resource_conditions),
                                    _filter=self._resource_filter,
                                    )
                                self._named_route_keys[route_name]=key

    def _register_route(self, prefix, method, resource, resource_name, action, action_name, parent, parent_name, remote_name, member_action):
        self._resource_to_route_dict[(prefix,resource,parent, remote_name, action,member_action)] =\
            dict([(k,locals()[k]) for k in "resource_name,parent_name,action_name,member_action".split(",")] )
        self._route_to_resource_dict[(prefix, method, resource_name, parent_name, action_name, member_action)]=\
            dict([(k,locals()[k]) for k in "resource,parent,action".split(",")] )

    def _resource_to_route(self, prefix, resource,parent, remote_name, action, member_action):
        return self._resource_to_route_dict[(prefix,
            resource,parent, remote_name, action, member_action)]
    
    def _route_to_resource(self, prefix, method, resource_name, parent_name, action_name, member_action):
        return self._route_to_resource_dict[(prefix, method, resource_name,parent_name,
            action_name, member_action)]
    
    def _resource_key(self, resource):
        return "%s %s %s" %(id(resource), resource.__module__, resource.__name__)
        
    def _store_resource_key(self, resource):
        key = self._resource_key(resource)
        self._resource_to_key[resource]=key
        self._key_to_resource[key]=resource
        
    def connect(self, *args, **kw):
        log.debug("Connect called with: %r", locals())
        
        resource = kw.get('resource', None)
        
        if len(args) == 1:
            name, route = None, args[0]
        elif len(args) == 2:
            name, route = args
        if kw.get('remote_name') is not None:
            assert 'parent' in kw
            self._resource_reg[(kw['parent'], kw['remote_name'])] = kw['resource']
            

        args = self._extract_args(kw)
        args['controller'] = kw.pop('controller', DefaultController)
        key = self._add_controller_key(args)
        #first register, add controller key, then encode
        self._encode_resource(kw)
        log.debug("Connect produced key %r", key)
        self.mapper.connect(name, route, controller=key, **kw)
        log.debug("mapper.connect(%r, controller=%r, **%r)", route, key, kw)
        return key

    def _get_resource_actions(self, typ, resource, parent, prefix, remote_name):
        controller_cls = app.controllerfactory.get(
            resource, parent, remote_name, None, prefix, {}
            )
        return get_resource_actions(controller_cls, typ)

    def resource(self, resource, parent=None, prefix=None, remote_name=None):
        self._resource_reg[(parent, remote_name)] = resource
        # Provide some sane defaults...
        prefix_param=prefix
        names_for_resource = app.names_for_resource
        resource_name = remote_name or names_for_resource(resource)[1]
        if parent is not None:
            parent_name = names_for_resource(parent)[1]
        else:
            parent_name = None
        member = self._get_resource_actions('member', resource, parent,
                                            prefix, remote_name)
        collection = self._get_resource_actions('collection', resource,
                                                parent, prefix,
                                                remote_name)

        connect_args = dict((k,v) for (k,v) in locals().iteritems()
                            if k in self._route_args)
        if parent:
            if prefix:
                prefix = '%s/%s/:(parent_id)' % (prefix, parent_name)
            else:
                prefix = '%s/:(parent_id)' % parent_name

        if prefix:
            route_base = prefix + '/' + resource_name
        else:
            route_base = resource_name

        


        # Connect collection which their action is in the url
        #
        # Connect 'index' when it is implicit
        if 'index' in collection:
            for action_name in ['index', '']:
                self._register_route(prefix=prefix_param, method=collection['index'], resource=resource,
                    resource_name = resource_name, action='index',
                    action_name=action_name, parent=parent,
                    parent_name=parent_name, remote_name=remote_name, member_action=False)
                
        for (action, method) in collection.iteritems():
            self._register_route(prefix_param, method=method, resource=resource,
                resource_name = resource_name, action=action,
                action_name=self._canonical_action_name(action, False), parent=parent,
                parent_name=parent_name, remote_name=remote_name, member_action=False)
       
        
        # Connect 'show' when it is implicit
        if 'show' in member:
            self._register_route(prefix_param, 
                method=member['show'],
                resource=resource, resource_name=resource_name,
                action='show', action_name='', parent=parent, parent_name=parent_name,
                remote_name=remote_name, member_action=True)


        if 'confirm_delete' in member:
            self._register_route(prefix_param, 
                method=member['confirm_delete'],
                resource=resource, resource_name=resource_name,
                action='show', action_name='delete', parent=parent, parent_name=parent_name,
                remote_name=remote_name, member_action=True)


        for (action, method) in member.iteritems():
            self._register_route(prefix_param, 
                method=method,
                resource=resource, resource_name=resource_name,
                action=action, action_name=self._canonical_action_name(action, True), parent=parent, parent_name=parent_name,
                remote_name=remote_name, member_action=True)
                

        # Connect collection methods which their action is not in the url
        if 'create' in collection:

            self._register_route(prefix_param, 
                method='POST',
                resource=resource, resource_name=resource_name,
                action='create', action_name='', parent=parent, parent_name=parent_name,
                remote_name=remote_name, member_action=False)



        # Connect member methods which their action is not in the url
        if 'update' in member:

        
        
            self._register_route(prefix_param, 
                method='PUT',
                resource=resource, resource_name=resource_name,
                action='update', action_name='', parent=parent, parent_name=parent_name,
                remote_name=remote_name, member_action=True)
        
            # self.connect(route, **args)
        
        if 'delete' in member:

            # self.connect(route, **args)
            
            self._register_route(prefix_param, 
                method='DELETE',
                resource=resource, resource_name=resource_name,
                action='delete', action_name='', parent=parent, parent_name=parent_name,
                remote_name=remote_name, member_action=True)



    def _encode_resource(self, kw):
        for keyword in ('resource', 'parent'):
            resource = kw.get(keyword, None)
            if resource is not None:
                self._store_resource_key(resource)
                kw[keyword]=self._resource_to_key[resource]
    def _decode_resource(self, kw):
        for keyword in ('resource', 'parent'):
            if kw.get(keyword, None) is not None:
                kw[keyword]=self._key_to_resource.get(kw[keyword], kw[keyword])

    def _canonical_action_name(self, action, member_action):
        if (member_action and action == 'show') or (not member_action and action=='index'):
            return ''
        if member_action and action=='confirm_delete':
            return 'delete'
        return action
    def url_for(self, *args, **kw):
        if len(args)>0:
            args=list(args)
            if isinstance(args[0], unicode):
                args[0] = args[0].encode('ascii')
        if len(args) == 1:
            args = list(args)
            arg = args.pop(0)
            if isinstance(arg, basestring):
                # handle external urls
                if 'http' in arg:
                    return arg
                return routes.url_for(arg)
            kw['resource'] = arg

        obj = kw.pop('obj', None)
        if obj:
            kw['resource'] = obj.__class__
            kw['id'] = app.repositoryfactory.get_id(obj)
            kw.setdefault('action', 'show')

        parent_obj = kw.pop('parent_obj', None)
        if parent_obj:
            kw['parent'] = parent_obj.__class__
            kw['parent_id'] = app.repositoryfactory.get_id(parent_obj)

        orig_kw = kw.copy()
        if kw.get('remote_name') and not kw.get('resource'):
            assert 'parent' in kw
            kw['resource'] = self._resource_reg[(kw['parent'],
                                                 kw['remote_name'])]
        config = self.request_config
        use_memory = kw.pop('_memory', False)
        mapper_dict = getattr(config, 'mapper_dict', None)
        if mapper_dict:
            # Propagate lang and format regardless of use_memory
            for k in 'lang', 'format':
                if mapper_dict.get(k) is not None:
                    kw[k] = mapper_dict[k]
            if kw.get('resource', None) is None:
                if mapper_dict.get('resource', None) is not None:
                    kw['resource'] = mapper_dict['resource']
            if use_memory:
                # emulate route memory for our special route args
                kw.update((k,v) for (k,v) in mapper_dict.iteritems()
                                if k not in kw and k in self._route_args)
                if 'controller' in mapper_dict.keys():
                    kw.setdefault('controller', mapper_dict['controller'])
                if 'lang' in mapper_dict and mapper_dict['lang'] is None:
                    del mapper_dict['lang']
        if kw.get('id', None)==None:
            kw.pop('id', None)
            
        if 'id' in kw:
            kw.setdefault('action', 'show')
        
        member_action =  'id' in kw
        if not 'action' in kw:
            if member_action:
                kw['action']='show'
            else:
                kw['action']='index'
        
        c_args = self._extract_args(kw)
        c_args['controller'] = kw.pop('controller', DefaultController)
        try:
            resource_bak = c_args['resource']
            key = self._get_controller_key(c_args)
        except KeyError, e:
            c_args['resource']=resource_bak
            
            route_name= self._resource_route_name(
                #resource=kw.get('resource'),
                parent= kw.get('parent'),
                member_action = member_action,
                prefix=kw.get('prefix'),
                format=kw.get('format'),
                lang=kw.get('lang'),
                action_name=self._canonical_action_name(kw.get('action','') , member_action)
            )
            key = self._named_route_keys[route_name]
            # Try using the DefaultController in case we're being called
            # from another controller and routes memory is screwing up
            #controller = c_args['controller']
            
            #I do not know how handle this error properly with new router
            # if safe_issubclass(controller, DefaultController):
            #     raise routes.util.RoutesException(str(e))
            
            
            #orig_kw['controller'] = DefaultController
            #no encoding necessary and allowed, is just recursive call
            #return self.url_for(*args, **orig_kw)
        # if not use_memory:
        #     key = '/'+key
        kw['controller'] = key
        kw['resource'] = c_args['resource']
        # Grab updated resource as left by _get_controller_key

        
        self._encode_resource(kw)
        
        log.debug("routes.url_for(*%r, **%r)", args, kw)
        #route_name(resource, parent, member_action,prefix, format, lang, action_name)
        if 'route_name' in locals():
            args=(route_name,)+tuple(args)
        url = routes.url_for(*args, **kw)
        if hasattr(config, 'environ'):
            url = config.environ['SCRIPT_NAME'] + url
        return url


    @property
    def request_config(self):
        config = routes.request_config()
        config_mapper = config.mapper
        assert config_mapper is self.mapper, "Router has not been activaed!"
        return config

    def activate(self, app=None):
        config = routes.request_config()
        if hasattr(config, 'using_request_local'):
            log.debug('Setting request_local')
            request_local = _RumReqLocal()
            config.request_local = lambda: request_local
            config = routes.request_config()
            config.mapper = self.mapper
        return config
        
    def deactivate(self, app=None):
        orig_config = routes.request_config(original=True)
        try:
            del orig_config.request_local
            log.debug('Cleared request_local')
        except AttributeError:
            log.debug('No need to clear request_local')
            pass

    def dispatch(self, environ):
        request = RumRequest(environ)
        new_method = request.params.get('_method')
        if new_method:
            request.method = new_method.upper()
        config = self.request_config
        
        #is that safe? environ is passed in routematch with route >=1.12
        self.mapper.environ = environ
        
        result = adapt_call(self.mapper.routematch,url=request.path_info, environ=environ)
        if result is not None:
            config.mapper_dict, config.route = result[:2]
            self._extend_match(config.mapper_dict)
            
        else:
            config.mapper_dict, config.route = None, None

        return config.mapper_dict
        
    def _extend_match(self, match):
        if match:
            self._inject_args(match, match['controller'])
            match.setdefault('lang', None)
            self._decode_resource(match)
            if not 'action' in match:
                match['action']='index'

    def match(self, url):
        match = self.mapper.match(url)
        self._extend_match(match)
        return match



    def _get_controller_key(self, args, named_route=None):
        resource = args['resource']
        # lookup all base classes
        if resource is not None: 
            for klass in resource.__mro__:
                args['resource'] = klass
                try:
                    return self._controller_keys[dct_key(args)]
                except KeyError:
                    pass
            # args = copy(args)
            # args['resource'] = None
            # return None
            raise KeyError(dct_key(args))
        else:
            return self._controller_keys[dct_key(args)]

    def _add_controller_key(self, args):
        args_key = dct_key(args)
        if args_key in self._controller_keys:
            return self._controller_keys[args_key]
        controller_key = '__auto%d' % self._serial.next() 
        self._controllers[controller_key] = args_key
        self._controller_keys[args_key] = controller_key
        return controller_key

    def _extract_args(self, dct, meth=dict.get):
        return dict((k, meth(dct, k, None)) for k in self._route_args)

    def _inject_args(self, route_dct, controller_key):
        args = self._controllers[controller_key]
        for (k,v) in args:
            if not route_dct.get(k,None) or k=='controller':
                route_dct[k]=v
        


def dct_key(dct):
    """Returns a hashable obj from a dict"""
    return frozenset(dct.iteritems())



def resource_action(typ, method='GET'):
    """
    Tags a controller action as being accesible by given HTTP `method` to
    handle a ``typ`` of either ``member`` or ``collection``.

    Example::

        >>> class DummyController(object):
        ...     @resource_action('collection', 'GET')
        ...     def index(self): pass
        ...     @resource_action('member', 'GET')
        ...     def show(self): pass
        ...     @resource_action('member', 'PUT')
        ...     def update(self): pass

        >>> get_resource_actions(DummyController, 'collection')
        {'index': 'GET'}
        >>> d = get_resource_actions(DummyController, 'member')
        >>> d['update']
        'PUT'
        >>> d['show']
        'GET'

    Actions are inheritted::

        >>> class SubDummyController(DummyController):
        ...     @resource_action('member', 'DELETE')
        ...     def delete(self): pass
        ...     @resource_action('collection', 'POST')
        ...     def index(self): pass

        >>> get_resource_actions(SubDummyController, 'collection')
        {'index': 'POST'}
        >>> d = get_resource_actions(SubDummyController, 'member')
        >>> d['update']
        'PUT'
        >>> d['show']
        'GET'
        >>> d['delete']
        'DELETE'
        
    """
    def callback(frame, name, func, old_locals):
        def register_controller_action(cls):
            methods = resource_action._registry.setdefault(cls, {})
            methods_for_typ = methods.setdefault(typ, {})
            methods_for_typ[name] = method
            return cls
        decorate_class(register_controller_action, frame=frame)
        return func
    return decorate_assignment(callback)
resource_action._registry = {}

def get_resource_actions(cls, typ):
    all = {}
    for c in cls.__mro__[-2::-1]: # from base to sub skipping `object`
        all.update(resource_action._registry.get(c, {}).get(typ, {}))
    return all

class _RumReqLocal(object):
    """RumRouter's request local"""
    pass
