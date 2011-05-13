import sys
from decimal import Decimal as PyDecimal
from datetime import datetime, date, timedelta
from calendar import day_name
from webhelpers.html import escape
from tempfile import NamedTemporaryFile
import mutagen

from sleepy.exceptions import InvalidPathException, NotFoundException
from sleepy.util import OrderedDict
from sleepy.lonsies import render_virtual_def, url
from sleepy.controllers import default_controller
from sleepy.shorties import s, cleanup_filename, Day, date_parse, uuid4, total_milliseconds
from sleepy.s3ish import upload
from sleepy.routesies import resurrection
from sleepy.config import loaded_tipe_node
from sleepy.path import Path, VarStep
from sleepy.atomish import E, tostring
from sleepy.xspfish import E as xspfE

def _tipe_class_from_name( name ):
    return getattr( sys.modules[ __name__ ],
                    name.capitalize())

def create( node,
            loader ):
    if "ref" in node:
        return Ref( Path( names_path=node[ "ref" ],
                          roots=loader.roots ))
    return _tipe_class_from_name( node[ "tipe" ] )()

class Tipe( object ):
    @property
    def query_template_uri( self ):
        return s( "/sleepy/query/{{ name }}.mako",
                  name=self.__class__.__name__ )

    @property
    def markup_template_uri( self ):
        return s( "/sleepy/markup/{{ name }}.mako",
                  name=self.__class__.__name__ )

    @property
    def name( self ):
        return self.__class__.__name__.lower()

    @property
    def multipart( self ):
        return False

    @property
    def has_multipart( self ):
        return self.multipart or any( child.tipe.has_multipart
                                      for child
                                      in self.children )

    def delete( self,
                path ):
        self.res.mako_query( "delete",
                             dict( path=path ),
                             update=True )
        return self.render_def( "deleted",
                                dict( path=path ))

    def _finish( self,
                 res,
                 node,
                 loader ):
        self.res = res
        self._finish_node( node,
                           loader )

    def _finish_node( self,
                      node,
                      loader ):
        pass

    def edit( self,
              path ):
        return self.render_def( "edit",
                                dict( path=path ))

    def create_obj( self,
                    dikt ):
        return ( self.create_obj_from_string
                  if hasattr( self,
                              "create_obj_from_string" )
                  else self.from_string )( escape( dikt[ self.res.name ] ))

    def from_string( self,
                     string ):
        return string

    def new( self,
             path ):
        return self.render_def( "new",
                                dict( path=path ))

    def text( self,
              path,
              obj,
              **kwargs ):
        return self.render_def( "text",
                                dict( path=path,
                                      obj=obj ))

    def show( self,
              path,
              obj,
              **kwargs ):
        return self.render_def( "show",
                                dict( path=path,
                                      obj=obj,
                                      **kwargs ))

    def resurrection( self,
                      path,
                      obj ):
        return self.render_def( "resurrection",
                                dict( path=path,
                                      obj=obj ))

    def resurrect( self,
                   path ):
        self.res.mako_query( "resurrect",
                             dict( path=path ),
                             update=True )
        return self.render_def( "resurrected",
                                dict( path=path ))

    def new_fields( self,
                    path ):
        return self.render_def( "new_fields",
                                dict( path=path.add( self.res )))

    def update( self,
                path,
                obj ):
        self.res.mako_query( "update",
                             dict( path=path,
                                   obj=obj ),
                             update=True )
        return self.render_def( "updated",
                                dict( path=path ))

    def create_xml( self,
                    path,
                    obj,
                    yd=None,
                    add_path=True,
                    created=None ):
        def _path():
            if add_path:
                if yd is not None:
                    return path.add( self.res,
                                     chunk=yd )
                else:
                    return path.add( name=self.res.name )
            else:
                return path
        self._create( _path(),
                      obj )
        return self.render_def( "create_xml",
                                dict( path=_path(),
                                      obj=obj,
                                      created=created ))

    def _create( self,
                 path,
                 obj ):
        pass

    def _init_db( self ):
        pass

    def render_def( self,
                    deff,
                    kwargs={} ):
        return render_virtual_def( self.markup_template_uri,
                                   deff,
                                   dict( col=self,
                                         **kwargs ),
                                   escape=False )

    def map_routes( self,
                    mapper ):
        actions = [ mapper.show ]
        if self.res.mutable:
            actions += [ mapper.edit,
                         mapper.update ]
        for action in actions:
            action( controller=default_controller,
                    names_path=self.res
                                   .path
                                   .names_path )

class Ref( Tipe ):
    def __init__( self,
                  path ):
        self.path = path

    @property
    def has_multipart( self ):
        return False

    @property
    def children( self ):
        return []

    def read( self,
              node,
              path,
              deleted=False ):
        return dict(( var_node.tag,
                      var_node.text )
                    for var_node in node )

    def text( self,
              path,
              obj,
              **kwargs ):
        concrete = self.path.concretize( obj )
        return concrete.tip.text( concrete )

    def show( self,
              path,
              obj,
              **kwargs ):
        return self.render_def( "show",
                                dict( path=path,
                                      obj=obj,
                                      concrete=self.path
                                                   .concretize( obj ),
                                      **kwargs ))

    def _concrete_obj_path( self,
                            obj ):
        from sleepy import resource
        return resource.read_obj_path( self.concrete( obj ))

    def concrete( self,
                  path_or_obj ):
        def _obj():
            if isinstance( path_or_obj,
                           Path ):
                return self.res.read_obj( path_or_obj )
            else:
                return path_or_obj

        return self.path.concretize( _obj())

    def opts( self ):
        def _leaves():
            return ( self.path
                         .tip
                         .mako_query( "read",
                                      mako_kwargs=dict( path=self.path[ 0 : 1 ] ),
                                      return_type="xml" )
                         .xpath( s( "/{{ xpath }}",
                                    xpath=self.path.xpath )))

        def _objs():
            return ( self.path[ : -1 ]
                         .tipe
                         ._sorted_objs(( dict( node=leaf,
                                               obj=self.path
                                                       .tip
                                                       .read( leaf,
                                                              self.path ))
                                          for leaf
                                          in _leaves()),
                                        key=lambda x:
                                             x[ "obj" ] ))

        def _yds( leaf ):
            def _ancestors( node ):
                while node is not None:
                    yield node
                    node = node.getparent()

            return ",".join( filter( bool,
                                     ( node.get( "yd" )
                                        for node
                                        in _ancestors( leaf ))))

        for obj in _objs():
            yield dict( yds=_yds( obj[ "node" ] ),
                        text=self.path
                                 .tipe
                                 .text( self.path,
                                        obj[ "obj" ] ))

    def item_names( self ):
        for step in reversed( self.path
                                  .steps ):
            if isinstance( step,
                           VarStep ):
                yield step.res.name

    def from_string( self,
                     string ):
        return string.split( "," )

class Enum( Ref ):
    def __init__( self ):
        pass

    def _finish_node( self,
                      node,
                      loader ):
        def _empty( root ):
            return not len( root.tipe
                                .yds( root.path ))
        loaded = loaded_tipe_node( self )
        plural = loaded.get( "plural",
                             s( "{{ name }}s",
                                name=loaded[ "name" ] ))
        if plural not in loader.roots:
            loader.add( dict( tipe="collection",
                              name=plural,
                              item=loaded,
                              mutable=None,
                              updatable=False ))
            root = loader.roots[ plural ]

            if _empty( root ):
                for val in loaded[ "vals" ]:
                    root.tipe._creation( root.path,
                                         root.tipe
                                             .item
                                             .tipe
                                             .create_obj( val ))
        self.path = loader.roots[ plural ].tipe.item.path

class Atomic( Tipe ):
    def child( self,
               name ):
        raise InvalidPathException( s( "{{ name }} has no children",
                                       name=self.res.name ))

    @property
    def children( self ):
        return []

    def read( self,
              node,
              path,
              deleted=False ):
        return self.from_string( node.text )

class File( Atomic ):
    @property
    def multipart( self ):
        return True

    def create_obj( self,
                    dikt ):
        param = dikt[ self.res.name ]
        return dict( filename=cleanup_filename( param.filename ),
                     value=param.value )

    def _create( self,
                 path,
                 obj ):
        upload( path.file_path( obj[ "filename" ] ),
                obj[ "value" ])

class Image( File ):
    pass

class Int( Atomic ):
    def from_string( self,
                     string ):
        return int( string )

class Weekday( Int ):
    def read( self,
              node,
              path,
              deleted=False ):
        def _val():
            return self.from_string( node.text )
        return Day( _val())

class Date( Atomic ):
    def from_string( self,
                     string ):
        return date_parse( string )

class Datetime( Atomic ):
    def create_obj( self,
                    dikt ):
        return date_parse( " ".join( dikt[ s( "{{ name }}.{{ part }}",
                                              name=self.res.name,
                                              part=part ) ]
                                      for part
                                      in ( "date",
                                           "time" )))

    def from_string( self,
                     string ):
        return date_parse( string )

class Decimal( Atomic ):
    def from_string( self,
                     string ):
        return PyDecimal( string )

class Money( Decimal ):
    pass

class Text( Atomic ):
    def _finish_node( self,
                      node,
                      loader ):
        self.size = node.get( "size" ) or "line"
        self.format = node.get( "format" ) or "plain"

class Uri( Text ):
    pass

class Email( Text ):
    pass

class Password( Text ):
    pass

class Identifier( Text ):
    pass

class Duration( Atomic ):
    def from_string( self,
                     string ):
        return timedelta( **dict( zip(( "days",
                                        "seconds",
                                        "microseconds" ),
                                      ( int( x )
                                         for x
                                         in string.split( "," )))))

    def _parse( self,
                string ):
        if string.count( ":" ) == 2:
            parts = ( "hours",
                      "minutes",
                      "seconds" )
        elif string.count( ":" ) == 1:
            parts = ( "minutes",
                      "seconds" )
        else:
            parts = ( "minutes", )
        return timedelta( **dict( zip( parts,
                                       ( float( x )
                                          for x 
                                          in string.split( ":" )))))

    def create_obj_from_string( self,
                                string ):
        try:
            return self._parse( string )
        except ValueError:
            return timedelta( hours=0 )

    def create_obj( self,
                    dikt ):
        try:
            tmpfile = NamedTemporaryFile( suffix="mp3" )
            tmpfile.write( dikt[ dikt[ "_duration_file_key" ]]
                               .value )
            return timedelta( seconds=mutagen.File( tmpfile.name ).info.length )
        except Exception:
            return Atomic.create_obj( self,
                                      dikt )

class Collection( Tipe ):
    def _finish_node( self,
                      node,
                      loader ):
        from sleepy import resource
        self.item = loader.create( node[ "item" ],
                                   res_class=resource.Item,
                                   parent=self.res )

    def _sorted_objs( self,
                      item_objs,
                      key=lambda x: x ):
        if self.item.sorted:
            return sorted( item_objs,
                           key=lambda x:
                                ( lambda f,
                                         g:
                                   f( g( x )))( self.item
                                                    .sort_key
                                                 or ( lambda x:
                                                       x ),
                                                key ),
                           reverse=self.item
                                       .sort_reverse )
        else:
            return list( item_objs )

    def read( self,
              node,
              path,
              deleted=False ):
        def _item_nodes():
            return node.xpath( s( "{{ name }}"
                                   "{{if not deleted}}"
                                       "[ not( @deleted = 1 ) ]"
                                   "{{elif deleted is True}}"
                                       "[ @deleted ]"
                                   "{{endif}}",
                                  name=self.item
                                           .name,
                                  deleted=deleted ))

        def _item_objs():
            for item_node in _item_nodes():
                yield self.item.read( item_node,
                                      path.add( chunk=item_node.get( "yd" )))

        return self._sorted_objs( _item_objs())

    def child( self,
               name ):
        if self.item.name == name:
            return self.item
        else:
            raise InvalidPathException( s( "{{ res_name }} has no child"
                                            " {{ name }}",
                                           res_name=self.res.name,
                                           name=name ))

    @property
    def children( self ):
        return [ self.item ]

    def map_routes( self,
                    mapper ):
        actions = [ mapper.show ]
        if self.res.mutable:
            actions += [ mapper.edit,
                         mapper.create,
                         mapper.new ]
            resurrection( mapper,
                          self.res )
        for action in actions:
            action( controller=default_controller,
                    names_path=self.res
                                   .path
                                   .names_path )

    def has_yd( self,
                yd,
                path ):
        return yd in self.yds( path )

    def yds( self,
             path ):
        return [ item.yd
                 for item
                 in self.res.read_obj( path ) ]

    def reorder( self,
                 path,
                 other_yd ):
        if other_yd != "last" and not self.has_yd( path.stip
                                                       .chunk,
                                                   path[ : -1 ] ):
            abort( 404 )
        copy = self.res.mako_query( "read",
                                    mako_kwargs=dict( path=path ))
        self.res.mako_query( "remove",
                             mako_kwargs=dict( path=path ),
                             update=True )
        if other_yd == "last":
            self.res.mako_query( "insert_last",
                                 mako_kwargs=dict( nodes=copy,
                                                   path=path[ : -1 ] ),
                                 update=True )
        else:
            self.res.mako_query( "insert_before",
                                 mako_kwargs=dict( nodes=copy,
                                                   path=path[ : -1 ]
                                                            .add( chunk=other_yd )),
                                 update=True )
        return self.render_def( "reordered",
                                dict( path=path ))

    def create( self,
                path,
                obj ):
        self._creation( path,
                        obj )
        return self.render_def( "created",
                                dict( path=path ))

    def _creation( self,
                   path,
                   obj ):
        self.res.mako_query( "create",
                             dict( path=path,
                                   obj=obj,
                                   yd=self.new_yd( path )),
                             update=True )

    def new_yd( self,
                path ):
        return self.res.mako_query( "new_yd",
                                    dict( path=path ))

    def create_obj( self,
                    dikt ):
        return []

class Struct( Tipe ):
    _config_attrs = ( "text_props",
                      "show_props",
                      "sort_prop",
                      "uuid" )

    def _finish_node( self,
                      node,
                      loader ):
        try:
            loaded = loaded_tipe_node( self )
        except NotFoundException:
            loaded = {}

        def _set( attr ):
            setattr( self,
                     attr,
                     node.get( attr )
                      or loaded.get( attr ))

        [ _set( attr )
           for attr
           in self._config_attrs ]

        if self.uuid and not self.res.parent:
            self._create_missing_root_uuid()

        self._create_props( node,
                            loader,
                            loaded )

        if self.res.root is self.res:
            self._init_db()

    def _init_db( self ):
        for prop in self.props.values():
            if not prop.mako_query( "read",
                                    dict( path=prop.path ),
                                    return_type="size" ):
                self.res.mako_query( "add_node",
                                     dict( path=prop.path ),
                                     update=True )
            prop.tipe._init_db()

    def _create_missing_root_uuid( self ):
        if not self.res.mako_query( "root_uuid",
                                    dict( path=self.res.path ),
                                    return_type="size" ):
            self.res.mako_query( "add_uuid",
                                 dict( path=self.res.path,
                                       uuid=uuid4()),
                                 update=True )

    def _create_props( self,
                       node,
                       loader,
                       loaded ):
        self.props = OrderedDict()
        try:
            self._add_props( loaded[ "props" ],
                             loader )
        except KeyError:
            pass
        try:
            self._add_props( node[ "props" ],
                             loader )
        except KeyError:
            pass

    def _add_props( self,
                    node,
                    loader ):
        for prop_node in node:
            self.props[ prop_node[ "name" ]] = loader.create( prop_node,
                                                              parent=self.res )

    @property
    def sort_key( self ):
        return lambda a: a[ self.sort_prop
                             or [ prop
                                   for prop
                                   in self.props ]
                                 [ 0 ]]

    def child( self,
               name ):
        try:
            return self.props[ name ]
        except KeyError:
            raise InvalidPathException( s( "{{ res_name }} has no child"
                                            " {{ name }}",
                                           res_name=self.res.name,
                                           name=name ))

    @property
    def children( self ):
        return self.props.values()

    def create_obj( self,
                    dikt ):
        return dict(( prop.name,
                      prop.tipe
                          .create_obj( dikt ))
                    for prop
                    in self.props
                           .values())

    def read( self,
              node,
              path,
              deleted=False ):
        return OrderedDict(( prop.name,
                             prop.read( node.xpath( prop.name )
                                            [ 0 ],
                                        path.add( name=prop.name )))
                            for prop in self.props.values())

class Location( Struct ):
    pass

class Album( Struct ):
    _config_attrs = Struct._config_attrs + ( "artist", )

    def map_routes( self,
                    mapper ):
        mapper.link( rel="playlist",
                     controller=default_controller,
                     names_path=self.res
                                    .path
                                    .names_path )

        Struct.map_routes( self,
                           mapper )

    def playlist( self,
                  path ):
        album = path.tip.read_obj( path )

        def _track( track ):
            def _duration():
                return ( total_milliseconds( track[ "duration" ] )
                          if track.get( "duration" )
                          else None )

            def _artist():
                return ( track.get( "artist" )
                          or path.tipe
                                 .artist )
            node = xspfE.track(
                       xspfE.location(
                           path.add( name="tracks" )
                               .add( chunk=track.yd )
                               .add( name="file" )
                               .s3_uri( track[ "file" ] )),
                       xspfE.album(
                           album[ "name" ] ),
                       xspfE.title(
                           track[ "name" ] ))
            if _artist():
                node.append( xspfE.creator(
                                 _artist()))
            if _duration():
                node.append( xspfE.duration(
                                 _duration()))
            return node

        return tostring( xspfE.playlist(
                             xspfE.title(
                                 album[ "name" ] ),
                             xspfE.trackList(
                                 *( _track( track )
                                     for track
                                     in album[ "tracks" ] )),
                             version="1" ))

class Name( Struct ):
    pass

class Feed( Struct ):
    @property
    def atom_str( self ):
        return tostring( self.atom())

    @property
    def atom( self ):
        return self._atom( self.res
                               .read_obj())

    def _atom( self,
               obj ):
        feed = E.feed( E.id( obj.uuid ),
                       E.title( obj[ "title" ] ),
                       E.link( rel="self",
                               href=url( "feed",
                                         name=self.res.name,
                                         qualified=True )),
                       E.updated( obj.updated ))

        for entry in obj[ "entry" ]:
            path = self.path.add( chunk=obj.yd )
            feed.entries.append( path.tipe
                                     ._atom( path,
                                             entry ))

        return feed

    def map_routes( self,
                    mapper ):

        Struct.map_routes( self,
                           mapper )

class Entry( Struct ):
    def permalink( self,
                   path ):
        raise NotImplementedError

    def _atom( self,
               path,
               obj ):
        def _author():
            raise NotImplementedError

        def _to_xhtml( text ):
            raise NotImplementedError

        def _content():
            content = E.content()
            content.html = _to_xhtml( obj[ "content" ] )
            return content

        entry = E.entry( E.id( obj.uuid ),
                         E.updated( obj.updated ),
                         E.published( obj.published ),
                         E.title( obj[ "title" ] ),
                         _author(),
                         E.link( rel="alternate",
                                 href=self.permalink( path )),
                         _content()
                         )


        return entry

class User( Struct ):
    def _atom( self,
               path,
               obj,
               element_class=E.author ):
        el = element_class()
        el.name = obj[ "name" ]
        if obj[ "email" ]._obj:
            el.email = obj[ "email" ]
        if obj[ "homepage" ]._obj:
            el.uri = obj[ "homepage" ]

class Venue( Struct ):
    pass

class Track( Struct ):
    def create_obj( self,
                    dikt ):
        obj = {}
        for prop in self.props.values():
            if prop.name == "duration":
                obj[ prop.name ] = prop.tipe.create_obj( dict( _duration_file_key="file",
                                                               **dikt ))
            else:
                obj[ prop.name ] = prop.tipe.create_obj( dikt )
        return obj

class State( Enum ):
    pass
