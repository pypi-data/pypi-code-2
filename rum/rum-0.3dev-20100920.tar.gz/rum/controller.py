import os
import sys
import logging
import re

from rum.component import Component
from rum.wsgiutil import RumResponse, RumRequest,\
                         HTTPNotImplemented, HTTPNotFound, HTTPBadRequest,\
                         status_map, HTTPException, HTTPRedirection, HTTPForbidden
from rum.genericfunctions import generic, NoApplicableMethods
from rum.basefactory import BaseFactory
from rum.router import resource_action, get_resource_actions
from rum import exceptions, app, fields, util, _, N_
from webflash import Flash
from rum import csvoutput, pdfoutput
import simplejson

log = logging.getLogger(__name__)


__all__ = [
    "ControllerFactory",
    "CRUDController",
    "Controller",
    "call_action",
    "process_output",
    "handle_exception",
    "formats",
    ]

get = BaseFactory.get.im_func

class RumFlash(Flash):
    def __call__(self, message, *args, **kw):
        #Force evaluation of lazystrings
        return super(RumFlash, self).__call__(unicode(message), *args, **kw)

class ControllerFactory(BaseFactory):

    @generic
    def get(self, resource, parent=None, remote_name=None, action=None,
            prefix=None, args=None):
        """
        Returns a class implementing :class:`rum.interfaces.IController`
        """

class SafeContext(object):
    def __getattr__(self, name):
        return u''

def formats(*formats):
    """
    Tags a controller action as supporting ``formats``.
    """
    def decorate(action):
        action.supported_formats = formats
        return action
    return decorate
    



        
class Controller(object):
    default_formats = ['html', 'json']
    renderer = None
    format_map = {
        'text/html': 'html',
        'application/json': 'json',
        'text/csv': 'csv',
        'application/vnd.ms-excel':'xls',
        'application/pdf': 'pdf',
        'text/plain': 'text',
        'application/x-latex':'latex'
        }
    def __init__(self):
        # Set these here to save some trips to the SOPs
        self.app = app._current_obj()
        self.request = self.app.request

    def __call__(self, environ, start_response):
        self.start_response = start_response
        self.template = None
        self.ctx = SafeContext()
        self.response = RumResponse()
        routes = self.routes = self.request.routes
        self._initialize_flash()
        try:
            output = self.call_action(routes)
        except Exception, e:
            self.exc_info = sys.exc_info()
            try:
                # try to handle it
                output = self.handle_exception(e, routes)
            except NoApplicableMethods:
                # no handler available, raise original exc. + traceback
                raise self.exc_info[0], self.exc_info[1], self.exc_info[2]
            except HTTPException, e:
                # allow flash+redirect to be used inside an exception handler
                self._copy_cookies_into_response(e)
                raise e
            except Exception:
                # Exception raised on handler, re-raise it
                del self.exc_info
                raise
            else:
                # Exception was properly handled, process handler's output
                del self.exc_info
        self.process_output(output, routes)
        return self.response(environ, self.start_response)

    get_resource_actions = classmethod(get_resource_actions)

    def _initialize_flash(self):
        self.flash = RumFlash(get_response=lambda: self.response)

    def forward(self, action, **kw):
        self.routes.update(**kw)
        self.routes['action'] = action
        return self.call_action(self.routes)

    @generic
    def handle_exception(self, exception, routes):
        """
        Do something when :meth:`call_action` raises an exception. Probably
        raise an appropiate HTTPException.

        The output from this function will be processed by
        :meth:`process_output`
        """

    @handle_exception.when((exceptions.SecurityDenial,))
    def _handle_denial(self, e, routes):
        self.flash(unicode(e), status='alert')
        raise HTTPForbidden(unicode(e).encode('utf-8')).exception

    def _copy_cookies_into_response(self, resp):
        for k,v in self.response.headerlist:
            if k.lower() == 'set-cookie':
                resp.headerlist.append((k,v))
        
    @handle_exception.when((HTTPException,))
    def _handle_http_exception(self, e, routes):
        """
        Makes sure that any cookies that have been set in the response
        (eg: by flash) are copied into the HTTPRedirection response
        """
        typ, inst, tb = self.exc_info[0], self.exc_info[1], self.exc_info[2]
        self._copy_cookies_into_response(inst)
        raise typ, inst, tb



    #
    # Content negotiation helpers
    #
    def get_format(self, routes):
        try:
            action = getattr(self, routes['action'])
        except (KeyError, AttributeError):
            # Need to be robust as we're called on pattern matching before
            # the wrapper that raises HTTPNotImplemented is called
            pass
        else:
            if 'format' in routes:
                return routes['format']
            accept = self.request.accept
            mimes = map(self.mime_for_format, self.formats_for_action(action))
            # see ticket #72
            bms = accept.best_matches()
            if 'MSIE' in self.request.user_agent and \
               'text/html' not in bms and '*/*' in bms:
                best_mime = mimes[0]
            else:
                best_mime = accept.best_match(mimes, mimes[0])
            log.debug("accept=%r, mimes=%r, best_mime=%r", accept, mimes,
                      best_mime)
            return self.format_for_mime(best_mime)

    def formats_for_action(self, action):
        if isinstance(action, basestring):
            action = getattr(self, action)
        return getattr(action, 'supported_formats', self.default_formats)

    def format_supported(self, routes): 
        try:
            formats = self.formats_for_action(routes['action'])
        except (AttributeError, KeyError):
            # Need to be robust as we're called on pattern matching before
            # the wrapper that raises HTTPNotImplemented is called
            return False
        return self.get_format(routes) in formats


    @generic
    def call_action(self, routes):
        """
        Call the controller action
        """

    @call_action.when()
    def call_action_default(self, routes):
        meth = getattr(self, routes['action'])
        return util.adapt_call(meth, **routes)

    @call_action.around("getattr(self, routes['action'], None) is None",
                        prio=20)
    def _method_not_implemented(self, routes):
        raise HTTPNotImplemented().exception

    @call_action.before("not self.format_supported(routes)")
    def _unsupported_media(self, routes):
        raise status_map[415]().exception

    @call_action.before("self.app.locale is None")
    def _unsupported_locale(self, routes):
        # This is only triggered when the user requests a specific locale
        # though the lang routing arg, not on Accept-Language headers since we
        # fallback to the default lang when none match
        raise HTTPNotFound(
            "The requested resource is not available in that language"
            ).exception

    #XXX: Change the protocol of this function so the result is returned instead
    #     of setting the response's body. What was I thinking about...
    @generic
    def process_output(self, output, routes):
        """
        Process output from action.
        """

    @process_output.when()
    def _set_response(self, output, routes):
        # assume output is a WSGI application
        self.response = output


    @process_output.when("isinstance(output, unicode)")
    def _process_unicode_output(self, output, routes):
        self.process_output(output.encode(self.response.charset), routes)

    @process_output.when("isinstance(output, str)")
    def _process_str_output(self, output, routes):
        self.response.body = output

    @process_output.before(
        "isinstance(output,dict) and self.get_format(routes) != 'json'")
    def _inject_template_vars(self, output, routes):
        def get_view(**kw):
            """A conveniente function to get the view for the current routes
            from the template. Keyword arguments will override those vars. in
            the routes dict."""
            if not getattr(self, 'view', None) is  None:
                return self.view
            routes_ = routes.copy()
            routes_.update(**kw)
            self.view = util.adapt_call(self.app.viewfactory, **routes_)
            return self.view
        # These variables will be available in any template, the dispatch rule
        # prevents these end up contaminating the json response
        def sort_key(r):
            return self.app.names_for_resource(r)[1]
        resources = sorted(self.app.resources, key=sort_key)
        output.update(
            ctx = self.ctx,
            _ = self.app.translator.ugettext,
            ungettext = self.app.translator.ungettext,
            app = self.app,
            config = self.app.config,
            widgets = self.app.config['widgets'],
            resources = resources,
            request = self.request,
            url_for = self.app.url_for,
            get_view = get_view,
            flash = self.flash,
            master_template = self.app.config['templating'].get(
                'master_template','master.html'
                )
            )
        output.update(routes)

    @process_output.when(
        "isinstance(output,dict) and self.get_format(routes) == 'json'")
    def _process_dict_as_json(self, output, routes):
         json_output = self.app.jsonencoder.encode(output)
         self.response.body = json_output
         
    @process_output.when(
        "isinstance(output,dict) and 'items' in output and self.get_format(routes) in ['xls', 'csv', 'pdf']")
    def _process_dict_as_csv(self, output, routes):
        output=output['items']
        resource = routes['resource']
        action=routes['action']
        fields_for_resource=self.app.fields_for_resource(resource)
        if fields_for_resource:
            csv_fields=[f for f in fields_for_resource if not 
                (isinstance(f, fields.Binary) or
                    isinstance(f, fields.Collection))]
            csv_fields=[f for f in csv_fields if 
                app.policy.has_permission(obj=resource, attr=f.name, action=action)]
        else:
            #testing purposes
            csv_fields=[]
        format=self.get_format(routes)
        if format=='csv':
            self.response.body = csvoutput.to_csv(output, csv_fields)
        else:
            if format=='pdf':
                self.response.body = pdfoutput.to_pdf(output, csv_fields)
            else:
                assert format=='xls'
                self.response.body = csvoutput.to_xls(output, csv_fields)
    @process_output.when(
          "isinstance(output,dict) and "
          "self.get_format(routes) in ['txt','html','xml']"
          )
    def _render_template(self, output, routes):
        possible_templates = self._get_possible_templates(routes)
        rendered_output = self.app.render(output, possible_templates,
                                          self.renderer)
        self.process_output(rendered_output, routes)
        
    @process_output.when(
          "isinstance(output, str) and self.get_format(routes) == 'html'"
          )
    def _inject_tw_resources(next_method, self, output, routes):
        log.debug("Injecting TW resources")
        from tw.api import inject_resources
        output = inject_resources(output, encoding=self.response.charset)
        next_method(self, output, routes)

    def _get_possible_templates(self, routes):
        possible_dirs = []
        resource = routes['resource']
        format = self.get_format(routes)
        prefix = os.path.sep + (routes.get('prefix') or '')
        if self.template:
            template_name = self.template + '.' + format
        else:
            template_name = routes['action'] + '.' + format

        if resource:
            names_for_resource = self.app.names_for_resource
            possible_dirs.extend(prefix + names_for_resource(cls)[1]
                                 for cls in resource.__mro__)
        possible_dirs.append('')
        return [os.path.join(dir, template_name) for dir in possible_dirs]

    #
    # call_action before methods to initialize stuff before calling the action
    #
    @call_action.before("self.get_format(routes) is not None")
    def _set_content_type(self, routes):
        format = self.get_format(routes)
        self.response.content_type = self.mime_for_format(format)



    def mime_for_format(self, format):
        for ct, fmt in self.format_map.iteritems():
            if fmt == format:
                return ct

    def format_for_mime(self, mime):
        for ct, fmt in self.format_map.iteritems():
            if ct in mime:
                return fmt
    #
    # call_action after methods to do stuff after the action has been called
    #
    @call_action.after("'paste.testing_variables' in self.request.environ")
    def _save_testing_variables(self, routes):
        self.request.environ['paste.testing_variables'].update(
            controller = self,
            routes = routes,
            )


    
call_action = Controller.call_action.im_func
process_output = Controller.process_output.im_func
handle_exception = Controller.handle_exception.im_func

class BinaryController(Controller):
    def __init__(self,resource,remote_name,*args,**kwd):
        self.remote_name=remote_name
        #self.content_type=resource.content_type
        super(BinaryController,self).__init__()

    @resource_action('collection', 'GET')
    def index(self,resource):
        res=getattr(self.parent_obj,self.remote_name)
        if res is None:
            return ""
        else:
            return str(res)


    @call_action.around("routes.get('parent_id')", prio=49)
    def _fetch_parent(next_method, self, routes):
        self.parent_obj = self.parent_repository.get(
            routes['parent_id']
            )        
        return next_method(self, routes)
    
    @call_action.around(prio=48)
    def _check_permission(next_method, self, routes):
        self.app.policy.check(obj=self.parent_obj, attr=self.remote_name, action="download")
        return next_method(self, routes)
    
    @call_action.around( prio=51)
    def _fetch_field(next_method, self, routes):
        
        #for f in self.app.fields_for_resource(self.parent_repository.resource):
        #    if f.name==self.remote_name:
        #        self.field=f
        #        return next_method(self, routes)
        self.field=self.app.field_for_resource_with_name(self.parent_repository.resource,self.remote_name)
        return next_method(self, routes)

    @call_action.before()
    def _set_content_type_disposition(self, routes):
        self.content_type=self.field.content_type_for(self.parent_obj)
        self.response.content_type = str(self.content_type)
        
        disposition="attachment"
        if routes["action"]=="preview":
            disposition="inline"
        try:
            suffix="."+self.content_type.split("/")[1]
        except IndexError:
            suffix=""
        filename=self.field.name+"-"+routes["parent_id"]+suffix
        if isinstance(filename,unicode):
            filename=filename.encode("utf-8")
        self.response.headers.add('Content-Disposition', disposition+';filename='+filename)
        
    @call_action.around("routes.get('resource')", prio=100)
    def _initialize_repository(next_method, self, routes):
        self.parent_repository = util.adapt_call(self.app.repositoryfactory, resource=routes["parent"])
        return next_method(self, routes)

    @handle_exception.when((exceptions.ObjectNotFound,))
    def _handle_object_not_found(self, e, routes):
        raise HTTPNotFound(str(e)).exception    

class ImageController(BinaryController):
    @resource_action('collection', 'GET')
    def preview(self,resource):
        try:
            import Image
        except ImportError:
            log.error("PIL - The Python imaging library is not installed! "
                      "You must install it for preview of images")
            raise HTTPNotFound("preview image could not be generated").exception
        
        width=self.field.preview_width
        height=self.field.preview_height
        data=getattr(self.parent_obj,self.remote_name)
        if not data:
            return ""
        
        buffer_=str(data)

        
        from cStringIO import StringIO

       
        out=StringIO()

        img=Image.open(StringIO(data))

        factor=width/float(img.size[0])
        if img.size[1]*factor>height:
            factor=height/float(img.size[1])

        width=min(img.size[0]*factor,width)
        width=int(width)
        height=min(img.size[1]*factor,height)
        height=int(height)
        img=img.resize((width,height),Image.ANTIALIAS)
        format=self.content_type.split("/")[1]
        img.save(out,format)
        out.flush()
        return out.getvalue()


class CRUDController(Controller):
    """REST Controller styled on the Atom Publishing Protocol"""
    _special_vars = ('_method', '_next_redirect', '_form_action')
    error_handlers = {
        'create': 'new',
        'update': 'edit',
        'preview': 'new',
        'delete': 'confirm_delete',
        }
    parent_obj = None
    
    @generic
    def default_limit(self, resource):
        """Default pagination items limit"""
    
    @default_limit.when()
    def _default_default_limit(self, resource):
        return self.app.config.get('default_page_size', 15)
    
    def __init__(self, error_handlers=None):
        super(CRUDController, self).__init__()
        self.error_handlers = error_handlers or self.error_handlers

    @property
    def routeable_actions(self):
        actions = get_resource_actions(self.__class__, 'member')
        actions.update(get_resource_actions(self.__class__, 'collection'))
        return actions

    @property
    def input_actions(self):
        input_methods = ('DELETE', 'POST', 'PUT')
        return [action for action,method in self.routeable_actions.iteritems()
                if method.upper() in input_methods]

    @handle_exception.when((exceptions.ObjectNotFound,))
    def _handle_object_not_found(self, e, routes):
        raise HTTPNotFound(str(e)).exception

    @handle_exception.when((exceptions.Invalid,))
    def _handle_validation_errors(self, e, routes):
        self.validation_errors = e
        self.response.status_int = 400
        self.flash(_(u"Form has errors. Please correct"), status="alert")
        log.debug("Validation failed: %s", e)
        return self.forward(self.form_action)

    @handle_exception.when((exceptions.BadId,))
    def _handle_bad_id(self, e, routes):
        raise HTTPBadRequest().exception
    

    

    @call_action.around("routes['action'] in self.input_actions", prio=200)
    def _validate_input(next_method, self, routes):
        self.view = util.adapt_call(self.app.viewfactory, **routes)
        validator = self.view
        old_method = self.request.method
        # trick webob Request so it leaves us PUT data in POST
        if self.request.method not in ['POST','GET']:
            self.request.method = 'POST'

        input = getattr(self.request, self.request.method.upper()).mixed()

        self.form_action = input.get(
            '_form_action',
            self.error_handlers[routes['action']]
            )
        if self.form_action and self.form_action not in self.routeable_actions:
            raise HTTPBadRequest(_(u"Don't be so smart")).exception

        try:
            self.form_result = validator.validate(input)
            self._remove_special_vars(self.form_result)
            return next_method(self, routes)
        finally:
            self.request.method = old_method

    def _remove_special_vars(self, input):
        input = input.copy()
        for var in self._special_vars:
            if var in input:
                del input[var]
        return input
            
    @call_action.around("routes.get('resource')", prio=100)
    def _initialize_repository(next_method, self, routes):
        self.repository = util.adapt_call(self.app.repositoryfactory, **routes)
        return next_method(self, routes)

    @call_action.around("routes.get('id')", prio=50)
    def _fetch_resource(next_method, self, routes):
        self.obj = self.repository.get(routes['id'])
        self.request.environ['rum.obj'] = self.obj
        return next_method(self, routes)
        

    @call_action.around("routes.get('parent_id')", prio=49)
    def _fetch_parent(next_method, self, routes):
        self.parent_obj = self.repository.parent_repository.get(
            routes['parent_id']
            )
        return next_method(self, routes)
    
    @call_action.around( prio=48)
    def _check_security(next_method, self, routes):
        check_on=routes["resource"]
        obj=getattr(self, "obj", None)
        if obj is not None:
            check_on=obj
        parent=getattr(self, "parent_obj",None)
        if not parent is None:
            remote_name=routes['remote_name']
            self.app.policy.check(obj=parent, action="show", attr=remote_name)
        self.app.policy.check(obj=check_on,action=routes["action"])
        return next_method(self, routes)
    
    @call_action.before()
    def _set_names(self, routes):
        if routes['resource']:
            r_names, r_namep = self.app.names_for_resource(routes['resource'])
            self.resource_name = self.app.translator.ugettext(r_names)
            self.resource_plural_name = self.app.translator.ugettext(r_namep)
        else:
            self.resource_name, self.resource_plural_name = None, None
        if routes['parent']:
            p_names, p_namep = self.app.names_for_resource(routes['parent'])
            self.parent_name = self.app.translator.ugettext(p_names)
            self.parent_plural_name = self.app.translator.ugettext(p_namep)
        else:
            self.parent_name = None
            self.parent_plural_name = None

            

    @process_output.before(
        "isinstance(output,dict) and self.get_format(routes) != 'json'")
    def _inject_template_vars(self, output, routes):
        output.update(
            validation_errors = getattr(self, 'validation_errors', None),
            resource = routes["resource"],
            parent_obj = self.parent_obj,
            resource_name = self.resource_name,
            resource_plural_name = self.resource_plural_name,
            parent_name = self.parent_name,
            parent_plural_name = self.parent_plural_name,
            )



    def resolve_conflict(self, new):
        """
        Shows a form to the user where the current state of an object is
        shown besides a form with the old state (left in self.form_result)
        so the user can resolve the conflict.

        .. note::
            This method is not routeable, it is intended to be called from a
            routeable method or exception handler.
        """
        self.response.status_int = 409 # Conflict
        self.flash(_(u"Someone else has modified the resource"),
                   status='alert')
        self.template = 'resolve_conflict'
        old = self.form_result
        old['_next_redirect'] = self.request.next_redirect
        v_field = None
        for f in self.app.fields_for_resource(new.__class__):
            if isinstance(f, fields.VersionID):
                v_field = f.name
                break
        assert v_field
        old[v_field] = getattr(new, v_field)
        output = {'old': old, 'new': new}
        return output


    #
    # Routeable methods
    #
    N_('_meta')
    @resource_action('collection', 'GET')
    def _meta(self, resource):
        return dict(
            fields = self.app.fields_for_resource(resource) or [],
            resource_name = self.resource_name,
            parent_name = self.parent_name,
            )

    N_('index')
    @formats('html', 'json', 'csv', 'xls', 'pdf')
    @resource_action('collection', 'GET')
    def index(self, resource):
        query = self.repository.make_query(self.request.GET)
        query = self.app.policy.filter(resource, query)
        if query:
            if not self.get_format(self.routes) in ['csv', 'xls', 'pdf']:
                if query.limit is None:
                    
                    query = query.clone(
                        limit=self.default_limit(resource)
                        #
                        )
                elif query.limit > self.app.config.get('max_page_size', 100):
                    raise HTTPBadRequest(
                        _(u"Too many results per page requested")
                        ).exception
        items = self.repository.select(query)
        return {
            'items': items,
            'query': query,
            }
            
            
    N_('complete')
    @resource_action('collection', 'GET')
    def complete(self, resource):
        #XXX: Perhaps this functionality could be provided by the index()
        #     method? This will allow us to feed any ItemReadStore and populate
        #     grids, etc...
        from rum.query import startswith, eq, or_, Query
        import rum.fields as fields
        limit=None
        offset=0
        
        request_args=self.request.GET
        
        if 'offset' in request_args:
            offset=int(request_args['offset'])
        else:
            offset=0
        if "match" in request_args:
            match=request_args['match']
        else:
            match=""
            
        items=[]
        if "id" in request_args and request_args["id"]:
            id_value=request_args["id"]
            try:
                if id_value:
                    items=items+[self.repository.get(id_value)]
            except:
                pass
        else:
            if 'limit' in request_args:
                limit=request_args['limit']
                if limit=='Infinity':
                    limit=None
                else:
                    limit=int(limit)

            

            #TODO: implement that generically, maybe generic functions
            #alternative: let the user provide/override this function


            
            if match:
                match_expr=re.compile(".*".join([re.escape(m) for m in match.split("*")]),flags=re.I) 
            else:
                match_expr=None
 
            #try:
            #    items=items+[self.repository.get(match)]
            #except:
            #    pass
            
            query = self.repository.make_query()
            if match or not len(items)==0:
                items = items+[i for i in self.repository.select(query) if match_expr.match(unicode(i)) or match_expr.match(unicode(self.repository.get_id(i)))]
            items=set(items)
        items=[dict(id=self.repository.get_id(i), description=unicode(i)) for i in items]
        def sort_key(i):
            return (i['description'],i['id'])
        items=sorted(items,key=sort_key)
        if offset:
            items=items[offset:]
        if limit:
            items=items[:limit]
        return {
            'identifier':'id',
            'label':'description',
            'items': items
            }

    N_('create')
    @resource_action('collection', 'POST')
    def create(self):
        obj = self.repository.create(self.form_result)
        self.flash(_(u'Object %(obj)s was succesfully created') % {'obj': obj})
        self.repository.save(obj)
        self.app.redirect_to(action='index', _use_next=True, id=None)
        

    N_('new')
    @resource_action('collection', 'GET')
    def new(self):
        return {'item': self.repository.default_value}


    N_('preview')
    @resource_action('collection', 'POST')
    def preview(self):
        obj = self.repository.create(self.form_result)
        return {'item':obj}


    N_('update')
    @resource_action('member', 'PUT')
    def update(self):
        for k in self.form_result:
            self.app.policy.check(obj=self.obj, action="update", attr=k)
        self.repository.update(self.obj, self.form_result)
        self.flash(_(u'Object %(obj)s was succesfully updated')
                   % {'obj':self.obj})
        #should include parent here
        self.app.redirect_to(obj=self.obj, action='show', _use_next=True)


    N_('confirm_delete')
    @resource_action('member', 'GET')
    def confirm_delete(self):
        return {'item': self.obj}


    N_('delete')
    @resource_action('member', 'DELETE')
    def delete(self):
        self.flash(_(u'Object %(obj)s was succesfully deleted')
                   % {'obj':self.obj})
        self.repository.delete(self.obj)
        member_actions = [self.app.url_for(obj=self.obj, action=a) for a in
                          get_resource_actions(self.__class__, 'member')]
        # Only use next_redirect if we're not redirecting to a member action
        # on the object we're going to delete
        use_next = self.request.next_redirect not in member_actions
        self.app.redirect_to(action='index', _use_next=use_next, id=None)


    N_('show')
    @resource_action('member', 'GET')
    def show(self):
        return {'item': self.obj}


    N_('edit')
    @resource_action('member', 'GET')
    def edit(self):
        return {'item': self.obj}

# Register controllers.

# CRUDController is the default
ControllerFactory.register(CRUDController, object)
ControllerFactory.register(BinaryController, fields.Binary)
ControllerFactory.register(ImageController, fields.Image)
    
default_limit=CRUDController.default_limit.im_func
