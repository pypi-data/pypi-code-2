import yaml
from os.path import join

from mako.lookup import TemplateLookup
from pylons import config
from pylons.error import handle_mako_error

from sleepy.shorties import *
from sleepy.lonsies import *
from sleepy.path import Path, ConcreteStep, VarStep
from sleepy import tipes
from sleepy.dbxmlish import ResourceContext
from sleepy.controllers import default_controller, update_controller, login_controller
from sleepy.util import MakoDef
from sleepy.routesies import reorder, resurrect
from sleepy.config import loader, templates_dir, static_dir

def read_obj_path( names_path,
                   concrete_args={} ):
    def _path():
        if isinstance( names_path,
                       Path ):
            return names_path
        else:
            return Path( names_path=names_path )

    path = _path().concretize( concrete_args )
    return ( path.tip
                 .read_obj( path ))

class Resource( object ):
    deletable = False
    labels = True

    def __init__( self,
                  name,
                  tipe ):
        self.name = name
        self.tipe = tipe

    def _step( self ):
        return ConcreteStep( self,
                             self.name )

    def xpath_step( self,
                    chunk ):
        return self.name

    def _attributize( self,
                      node,
                      loader ):
        pass

    @property
    def label( self ):
        return self.name

    def child( self,
               name ):
        return self.tipe.child( name )

    def read( self,
              node,
              path,
              deleted=False,
              proxy_kwargs=None ):
        obj=self.tipe.read( node,
                            path,
                            deleted=deleted )
        return proxy( obj=obj,
                      uuid=node.get( "uuid" ),
                      path=path,
                      tipe=path.tipe,
                      res=path.tip,
                      ref=path.tipe
                              ._concrete_obj_path( obj )
                           if hasattr( path.tipe,
                                       "_concrete_obj_path" )
                           else None,
                      updated=date_parse( node.get( "updated" )),
                      published=date_parse( node.get( "created" )),
                      **( proxy_kwargs
                           if proxy_kwargs
                           else dict()))

    def create( self,
                path,
                obj ):
        return self.tipe.create( path,
                                 obj )

    def resurrection( self,
                      path ):
        return self.tipe.resurrection( path,
                                       self.read_obj( path,
                                                      deleted=True ))

    def resurrect( self,
                   path ):
        return self.tipe.resurrect( path )

    def update( self,
                path,
                obj ):
        return self.tipe.update( path,
                                 obj )

    def text( self,
              path,
              **kwargs ):
        return self.tipe.text( path,
                               self.read_obj( path ),
                               **kwargs )

    def show( self,
              path,
              **kwargs ):
        return self.tipe.show( path,
                               self.read_obj( path ),
                               **kwargs )

    def read_obj( self,
                  path=None,
                  deleted=False ):
        return self.read( self.mako_query( "read",
                                           mako_kwargs=dict( path=path
                                                                   or self.path ),
                                           return_type="xml" ),
                          path,
                          deleted=deleted )

    def edit( self,
              path ):
        return self.tipe.edit( path )

    def playlist( self,
                  path ):
        return self.tipe.playlist( path )

    def new( self,
             path ):
        return self.tipe.new( path )

    def new_fields( self,
                    path ):
        return self.tipe.new_fields( path )

    def map_routes( self,
                    mapper ):
        with mapper.submapper( path_prefix=s( "{{if route_prefix }}"
                                                  "/{{ route_prefix }}"
                                              "{{endif}}"
                                              "/{{ chunk }}",
                                              chunk=self._step()
                                                        .route_chunk,
                                              route_prefix=getattr( self,
                                                                    "route_prefix",
                                                                    None )),
                               resource_name=self.path
                                                 .names_path ) as m:
            self.tipe.map_routes( m )
            self._add_routes( m )
            for child in self.tipe.children:
                child.map_routes( m )

    def _add_routes( self,
                     mapper ):
        pass

    def mako_query( self,
                    deff,
                    mako_kwargs={},
                    **kwargs ):
        return self.root.dbxml.query( MakoDef( self.tipe
                                                   .query_template_uri,
                                               deff,
                                               mako_kwargs ),
                                      **kwargs )

class RootResource( Resource ):
    route_prefix="sleepy"

    def __init__( self,
                  name,
                  tipe ):
        Resource.__init__( self,
                           name,
                           tipe )
        self.parent = None
        self.root = self
        self.path = Path( self,
                          names_path=self.name )
        self.dbxml = ResourceContext( self )

class SubResource( Resource ):
    def __init__( self,
                  name,
                  tipe,
                  parent ):
        Resource.__init__( self,
                           name,
                           tipe )
        self.parent = parent
        self.root = self.parent.root
        self.path = self.parent.path + self._step()

    def delete( self,
                path ):
        return self.tipe.delete( path )

class Item( SubResource ):
    deletable = True
    labels = False

    def _step( self ):
        return VarStep( self )

    def xpath_step( self,
                    chunk ):
        return s( "{{ name }}"
                   "[ @yd = {{ chunk }} ]",
                  name=self.name,
                  chunk=chunk )

    def _add_routes( self,
                     mapper ):
        if self.parent.mutable:
            if self.reorderable:
                reorder( mapper,
                         self )
            if self.deletable:
                resurrect( mapper,
                           self )
                mapper.delete( controller=default_controller,
                               names_path=self.path.names_path )

    def reorder( self,
                 path,
                 other_yd ):
        return self.parent.tipe.reorder( path,
                                         other_yd )

    def read( self,
              node,
              path,
              deleted=False ):
        return Resource.read( self,
                              node,
                              path,
                              deleted,
                              proxy_kwargs=dict( yd=node.get( "yd" )))

    def _attributize( self,
                      node,
                      loader ):
        self.reorderable = node.get( "reorderable",
                                     True )
        self.uuid = node.get( "uuid" )
        self.sorted = node.get( "sorted",
                                True
                                 if "sort_reverse" in node
                                     or "sort_attr" in node
                                 else False )
        if self.sorted:
            self.sort_reverse = node.get( "sort_reverse",
                                          False )
            self.sort_attr = node.get( "sort_attr",
                                       None )

    @property
    def sort_key( self ):
        return (( lambda x:
                   getattr( x,
                            self.sort_attr ))
                  if self.sort_attr
                  else getattr( self.tipe,
                                "sort_key",
                                lambda x: x ))

def _create_lookup():
    config[ "pylons.app_globals" ].sleepy_lookup = TemplateLookup(
                        directories=[ templates_dir() ],
                        error_handler=handle_mako_error,
                        module_directory=join( config[ 'pylons.cache_dir' ],
                                               'sleepy_templates' ),
                        input_encoding='utf-8',
                        output_encoding='utf-8',
                        default_filters=[ "_raw",
                                          "unicode" ],
                        imports=[ "from sleepy.shorties import _raw" ] )

def _create_routes( roots,
                    mapper ):
    for root in roots.values():
        root.map_routes( mapper )
    mapper.connect( "update",
                    "/update",
                    controller=update_controller,
                    action="template",
                    page="home" )
    mapper.connect( "login",
                    "/login",
                    controller=login_controller,
                    action="login" )
    mapper.connect( "logout",
                    "/login/logout",
                    controller=login_controller,
                    action="logout" )
    mapper.connect( "login_action",
                    "/login/{action}",
                    controller=login_controller )

def init( filename,
          mapper=None ):
    _create_lookup()
    roots = Loader( filename ).roots
    _create_routes( roots,
                    mapper
                     if mapper is not None
                     else config[ "routes.map" ] )
    config[ "sleepy.resources" ] = roots
    return roots

class Loader( object ):
    def __init__( self,
                  filename ):
        self.roots = {}
        for root in loader( open( filename ).read()):
            self.add( root )

    def add( self,
             root ):
        self.roots[ root[ "name" ]] = self.create( root )

    def _attributize( self,
                      res,
                      node ):
        if res.parent and res.parent.mutable is None:
            res.mutable = None
        else:
            res.mutable = node.get( "mutable",
                                    True )
            if res.mutable == "readonly":
                res.mutable = None
        res.updatable = node.get( "updatable",
                                  True )
        try:
            res.labels = node[ "labels" ]
        except KeyError:
            pass
        res._attributize( node,
                          self )

    def create( self,
                node,
                res_class=SubResource,
                parent=None ):
        tipe = tipes.create( node,
                             self )
        if parent is None:
            res = RootResource( node[ "name" ],
                                tipe )
        else:
            res = res_class( node[ "name" ],
                             tipe,
                             parent )
        self._attributize( res,
                           node )
        tipe._finish( res,
                      node,
                      self )
        return res
