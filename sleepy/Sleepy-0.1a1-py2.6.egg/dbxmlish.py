from os.path import splitext, basename
from collections import MutableMapping
import dbxml
from lxml import etree

from sleepy.lonsies import db_path, render_virtual_def
from sleepy.shorties import s, uuid4
from sleepy.util import MakoDef

def _filename_ext( filename ):
    return splitext( basename( filename ))

def create_db( manager,
               path,
               doc_name=None,
               root_tag=None,
               input_path=None,
               res=None ):
    doc_name = doc_name or _filename_ext( path )[ 0 ]
    if input_path is not None:
        input = manager.createLocalFileInputStream( input_path )
    else:
        input = s( "<{{ tag }}"
                     "{{if res and ( getattr( res, 'uuid', None ) or getattr( res.tipe, 'uuid', None )) }}"
                       " uuid={{ uuid }}"
                     "{{endif}}"
                   "></{{ tag }}>",
                   tag=root_tag
                        or doc_name,
                   res=res,
                   uuid=uuid4())

    manager.createContainer( path
          ).putDocument( doc_name,
                         input,
                         manager.createUpdateContext())

class Collections( MutableMapping ):
    def __init__( self,
                  query_cols,
                  dbxml_context ):
        self._cols = dict()
        if dbxml_context.collection:
            self._add( dbxml_context.collection )
        self._add( query_cols )
        if not isinstance( query_cols,
                           str ) and not isinstance( query_cols,
                                                     CollectionBase ):
            for query_col in query_cols:
                self._add( query_col )
        if dbxml_context.collection:
            self.default = dbxml_context.collection
        elif isinstance( query_cols,
                         str ):
            self.default = self._cols[ query_cols ]
        elif isinstance( query_cols,
                         CollectionBase ):
            self.default = query_cols
        elif isinstance( query_cols[ 0 ],
                         str ):
            self.default = self._cols[ query_cols[ 0 ]]
        else:
            self.default = query_cols[ 0 ]
    def __delitem__( self,
                     key ):
        del self._cols[ key ]
    def __getitem__( self,
                     key ):
        return self._cols[ key ]
    def __setitem__( self,
                     key,
                     value ):
        self._cols[ key ] = value
    def __iter__( self ):
        return iter( self._cols )
    def __len__( self ):
        return len( self._cols )
    def __getattr__( self,
                     name ):
        return getattr( self.default,
                        name )
    def _add( self,
              col ):
        self._add_str( col )
        self._add_col( col )
    def _add_col( self,
                  col ):
        if isinstance( col,
                       CollectionBase ):
            self._cols[ col.name ] = col
    def _add_str( self,
                  col ):
        if isinstance( col,
                       str ):
            self._cols[ col ] = CollectionName( col )

class CollectionBase( object ):
    def db_path( self ):
        return db_path( self.name )

    def fn_col( self ):
        return s( """collection( "///{{ path }}" )""",
                  path=self.db_path())

class CollectionName( CollectionBase ):
    def __init__( self,
                  name ):
        self.name = name

class Context( object ):
    def __init__( self,
                  collection=None ):
        self.manager = dbxml.XmlManager()
        self.collection = collection

    def _createdb( self,
                   doc_name=None,
                   root_tag=None ):
        create_db( self.manager,
                   self.collection
                       .db_path(),
                   doc_name
                    or self.collection
                           .name,
                   root_tag
                    or self.collection
                           .name,
                   res=getattr( self,
                                "root",
                                None ))

    def _create_missing_db( self ):
        if not self.manager.existsContainer( self.collection
                                                 .db_path()):
            self._createdb()

    def _collections( self,
                      collections ):
        return Collections( collections,
                            self )

    def query( self,
               q,
               collections=[],
               vars=None,
               qc=None,
               update=False,
               lookup=None,
               return_type=None ):
        def _render():
            return render_virtual_def( q.template,
                                       q.deff,
                                       dict( col=_collections,
                                             **q.kwargs ),
                                       as_unicode=False,
                                       lookup=lookup )
        _collections = self._collections( collections )
        containers = [ self.manager
                           .openContainer( collection.db_path())
                       for collection
                       in _collections.values() ]
        if qc is None:
            qc = self.manager.createQueryContext()
        if vars is not None:
            for var in vars:
                qc.setVariableValue( var,
                                     dbxml.XmlValue( str( vars[ var ] )))

        # allow mako in-place string rendering?
        assert isinstance( q, MakoDef )
        result = self.manager.query( _render(),
                                     qc )
        if return_type == "size":
            ret = result.size()
        elif update:
            ret = ""
        else:
            ret = result.next().asString()[ : ].decode( "utf-8" )
            if return_type == "xml":
                ret = etree.fromstring( ret )
        result.__swig_destroy__( result )
        return ret

class ResourceCollection( CollectionBase ):
    def __init__( self,
                  root ):
        self.root = root

    @property
    def name( self ):
        return self.root.name

class ResourceContext( Context ):
    def __init__( self,
                  root ):
        self.root = root
        Context.__init__( self,
                          ResourceCollection( root ))
        self._create_missing_db()

def dump( name,
          pretty_print=True ):
    mgr = dbxml.XmlManager()
    ctr = mgr.openContainer( s( "{{ name }}.db",
                                name=name ))
    doc = ctr.getDocument( name )
    return etree.tostring( etree.XML( doc.getContent()),
                           pretty_print=pretty_print )
