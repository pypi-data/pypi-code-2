from pylons.controllers import WSGIController
from pylons.controllers.util import abort, redirect
from pylons import request, response, config, tmpl_context as c, session, url
from mako.exceptions import TopLevelLookupException

from sleepy.shorties import s
from sleepy.lonsies import set_content_type, render, render_mako
from sleepy.path import Path

default_controller = "sleepy.controllers:ResourceController"
update_controller = "sleepy.controllers:UpdateController"
login_controller = "sleepy.controllers:LoginController"

class TemplateController( WSGIController ):
    def __before__( self,
                    action,
                    **kwargs ):
        url.environ[ "SCRIPT_NAME" ] = ""

    def template( self,
                  page ):
        try:
            for _page in config[ "pylons.app_globals" ].pages:
                if _page.name == page:
                    c.page = _page
                    break
        except AttributeError:
            pass
        try:
            getattr( self.Prep,
                     "_all" )()
        except AttributeError:
            pass
        try:
            getattr( self.Prep,
                     page )()
        except AttributeError:
            pass
        try:
            return render_mako( s( "/pages/{{ page }}.mako",
                                   page=page ))
        except TopLevelLookupException:
            abort( 404 )

def _login_redirect():
    redirect( url( "login" ))

def _authenticate():
    if "user" not in session:
        session[ "path_before_login" ] = request.path_info
        session.save()
        _login_redirect()

class LoginController( WSGIController ):
    def __before__( self,
                    action,
                    **kwargs ):
        url.environ[ "SCRIPT_NAME" ] = ""

    def login( self ):
        return render_mako( "/sleepy/update/login.mako" )

    def submit( self ):
        def _user( username ):
            from sleepy import resource
            for user in resource.read_obj_path( "users" ):
                if user[ "login" ]._obj == username:
                    return user
            return None

        user = _user( request.params.get( "username" ))
        if not user or user[ "password" ]._obj != request.params.get( "password" ):
            _login_redirect()

        session[ "user" ] = user[ "login" ]._obj
        session.save()
        if session.get( "path_before_login" ):
            redirect( session[ "path_before_login" ] )

        return render_mako( "/sleepy/update/loggedin.mako" )

    def logout( self ):
        if "user" in session:
            del session[ "user" ]
            session.save()
        return render_mako( "/sleepy/update/loggedout.mako" )

class UpdateController( WSGIController ):
    def __before__( self,
                    *args,
                    **kwargs ):
        url.environ[ "SCRIPT_NAME" ] = ""

        _authenticate()

    def template( self,
                  page ):
        c.roots = config[ "sleepy.resources" ]
        return render( "/sleepy/update/home.mako" )

class ResourceController( WSGIController ):
    public_actions = [ "playlist" ]

    def __before__( self,
                    names_path,
                    **kwargs ):
        url.environ[ "SCRIPT_NAME" ] = ""

        if kwargs[ "action" ] not in self.public_actions:
            _authenticate()
        from sleepy import resource
        self._path = Path( names_path=names_path ).concretize( kwargs )
        self._res = self._path.tip
        self._format = kwargs.get( "format" ) or "html"
        self._kwargs = kwargs
        set_content_type( self._format )

    def _handle_error( self ):
        if config[ "debug" ]:
            raise
        else:
            response.status = "200 OK"
            return render( "/sleepy/update/failed.mako" )
            
    def create( self,
                **kwargs ):
        try:
            ret = self._res.create( self._path,
                                    self._res
                                        .tipe
                                        .item
                                        .tipe
                                        .create_obj( request.params ))
            response.status = "201 Created"
            return ret
        except Exception:
            self._handle_error()

    def update( self,
                **kwargs ):
        try:
            ret = self._res.update( self._path,
                                    self._res
                                        .tipe
                                        .create_obj( request.params ))
    #        response.status = "201 Created"
            return ret
        except Exception:
            self._handle_error()

    def resurrection( self,
                     **kwargs ):
        return self._res.resurrection( self._path )

    def resurrect( self,
                   **kwargs ):
        try:
            return self._res.resurrect( self._path )
        except Exception:
            self._handle_error()

    def show( self,
              **kwargs ):
        return self._res.show( self._path )

    def edit( self,
              **kwargs ):
        return self._res.edit( self._path )

    def new( self,
             **kwargs ):
        return self._res.new( self._path )

    def delete( self,
                **kwargs ):
        try:
            return self._res.delete( self._path )
        except Exception:
            self._handle_error()

    def reorder( self,
                 **kwargs ):
        try:
            return self._res.reorder( self._path,
                                      request.params[ "other" ] )
        except Exception:
            self._handle_error()

    def playlist( self,
                  **kwargs ):
        return self._res.playlist( self._path )
