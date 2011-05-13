from pylons import config
from sleepy.exceptions import PathException
from sleepy.shorties import s
from sleepy.s3ish import uri

class Step( object ):
    @property
    def name( self ):
        return self.res.name

class ConcreteStep( Step ):
    def __init__( self,
                  res,
                  chunk ):
        self.res = res
        self.chunk = chunk
        self.route_chunk = chunk
    @property
    def xpath( self ):
        return self.res.xpath_step( self.chunk )

class VarStep( Step ):
    def __init__( self,
                  res ):
        self.res = res
        self.chunk = self.res.name
    @property
    def xpath( self ):
        return self.chunk
#        raise PathException( "Can't xpath an abstract path" )
    @property
    def route_chunk( self ):
        return "{" + self.name + "}"

class Path( object ):
    def __init__( self,
                  root=None,
                  steps=None,
                  names_path=None,
                  roots=None ):
        if names_path:
            if names_path[ 0 ] == "/":
                names_path = names_path[ 1 : ]
            self.root = root or ( roots
                                   or config[ "sleepy.resources" ]
                                 )[ names_path.split( "/" )
                                               [ 0 ]]
            self.names_path = names_path
            self.steps = self._steps()
        else:
            self.root = root or steps[ 0 ].res
            self.steps = steps
            self.names_path = self._names_path()

    def kwargs_dict( self ):
        return dict(( step.name,
                      step.chunk )
                    for step
                    in self.steps
                    if step.name != step.chunk )

    def __getitem__( self,
                     index_or_slice ):
        if isinstance( index_or_slice,
                       slice ):
            return Path( self.root,
                         steps=self.steps[ index_or_slice ] )
        return self.steps[ index_or_slice ]

    @property
    def tip( self ):
        return self[ -1 ].res

    @property
    def tipe( self ):
        return self[ -1 ].res.tipe

    @property
    def stip( self ):
        return self[ -1 ]

    def concretize( self,
                    vars ):
        if isinstance( vars,
                       ( list,
                         tuple )):
            vars = list( vars )

        def _get_var( step ):
            if isinstance( vars,
                           list ):
                return vars.pop()
            else:
                return vars[ step.name ]

        def _concrete_step( step ):
            if isinstance( step,
                           ConcreteStep ):
                return step
            else:
                return ConcreteStep( step.res,
                                     _get_var( step ))

        return Path( self.root,
                     steps=[ _concrete_step( step )
                             for step
                             in self.steps ] )

    def __add__( self,
                 step ):
        assert isinstance( step,
                           Step )
        return Path( self.root,
                     steps=self.steps + [ step ] )

    def add( self,
             res=None,
             chunk=None,
             name=None ):
         if name is not None:
            return self + ConcreteStep( self.tip
                                            .child( name ),
                                        name )
         res = res if res is not None else self.tipe.item
         if chunk is not None:
            return self + ConcreteStep( res,
                                        chunk )
         else:
            return self + VarStep( res )

    def s3_uri( self,
                filename,
                bucket=None ):
        return uri( self.file_path( filename ),
                    bucket )

    def _step( self,
               name,
               parent_res ):
        res = parent_res.child( name )
        return ( res._step(),
                 res )

    def _steps( self ):
        res = self.root
        names = self.names_path.split( "/" )
        steps = [ ConcreteStep( res,
                                names[ 0 ] ) ]
        for name in names[ 1 : ]:
            ( step,
              res ) = self._step( name,
                                  res )
            steps.append( step )
        return steps

    @property
    def xpath( self ):
        return self._joined( "xpath" )

    @property
    def chunk_path( self ):
        return self._joined( "chunk" )

    @property
    def route( self ):
        return self._joined( "route_chunk" )

    def _names_path( self ):
        return self._joined( "name" )

    @property
    def names_str( self ):
        return self._joined( "name",
                             sep="_" )

    @property
    def chunk_str( self ):
        return self._joined( "chunk",
                             sep="_" )

    def _joined( self,
                 attr,
                 sep="/" ):
        return sep.join( getattr( step,
                                  attr )
                         for step
                         in self.steps )

    def file_path( self,
                   filename,
                   project=None ):
        return s( "{{ project }}"
                   "/{{ chunk_path }}"
                   "/{{ filename }}",
                  project=project
                           if project is not None
                           else config[ "pylons.package" ],
                  chunk_path=self.chunk_path,
                  filename=filename )
