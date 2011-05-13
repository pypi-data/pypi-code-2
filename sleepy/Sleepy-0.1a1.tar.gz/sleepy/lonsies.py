import os.path
from pylons import response, config, url
from pylons.templating import pylons_globals, render_mako as pylons_render_mako
from mako.util import FastEncodingBuffer, StringIO
from mako.runtime import Namespace, Context
from webhelpers.html import tags, tools
from gdata.service import RequestError
from sleepy.shorties import *
from sleepy import shorties
import sleepy

format_content_types = dict( html="text/html",
                             xml="application/xml",
                             text="text/plain",
                             json="application/json",
                             swf="application/x-shockwave-flash",
                             xspf="application/xspf+xml" )

def set_content_type( format ):
    response.content_type = format_content_types[ format ]

def _dir( name,
          path="root" ):
    return config.get( s( "{{ name }}_dir",
                          name=name ),
                       os.path.join( config[ "pylons.paths" ]
                                           [ path ],
                                     name ))

def _data_subdir( name ):
    return config.get( s( "{{ name }}_dir",
                          name=name ),
                       os.path.join( data_dir(),
                                     name ))

def _path( name,
           filename,
           ext=True,
           dir=None ):
    return os.path.join( dir
                          or _dir( name ),
                         filename if filename[ - ( len( name )
                                                    + 1 ) : ]
                                      == s( ".{{ name }}",
                                            name=name )
                                      or not ext
                                  else s( "{{ filename }}.{{ name }}",
                                          locals()))

def data_dir():
    return _dir( "data" )

def data_path( filename ):
    return _path( "data",
                  filename,
                  ext=False )

def db_dir():
    return _data_subdir( "db" )

def db_path( filename ):
    return _path( "db",
                  filename,
                  dir=db_dir())

def xml_dir():
    return _data_subdir( "xml" )

def xml_path( filename ):
    return _path( "xml",
                  filename,
                  dir=xml_dir())

def xslt_dir():
    return _data_subdir( "xslt" )

def xslt_path( filename ):
    return _path( "xslt",
                  filename,
                  dir=xslt_dir())

def images_dir():
    return _dir( "images",
                 path="static_files" )

def _get_buffer( template,
                 as_unicode ):
    if as_unicode:
        return FastEncodingBuffer( unicode=True )
    elif template.output_encoding:
        return FastEncodingBuffer( unicode=as_unicode,
                                   encoding=template.output_encoding,
                                   errors=template.encoding_errors )
    else:
        return StringIO()

def render( uri,
            kwargs={},
            lookup=None ):
    if lookup is None:
        lookup = _lookup()
    template = lookup.get_template( uri )
    return template.render_unicode( **dict( kwargs,
                                            **pylons_globals()))

extra_template_vars = dict( tags=tags,
                            tools=tools,
                            s=s,
                            shorties=shorties,
                            sleepy=sleepy )

def render_mako( template_name,
                 extra_vars=None,
                 cache_key=None,
                 cache_type=None,
                 cache_expire=None ):
    return pylons_render_mako( template_name,
                               extra_vars=dict( extra_vars
                                                 or {},
                                                **extra_template_vars ),
                               cache_key=cache_key,
                               cache_type=cache_type,
                               cache_expire=cache_expire )

def render_virtual_def( uri,
                        deff,
                        kwargs={},
                        as_unicode=True,
                        lookup=None,
                        escape=False ):
    if lookup is None:
        lookup = _lookup()
    template = lookup.get_template( uri )
    if escape:
        create_or_append( "escape",
                          template,
                          "default_filters" )
        create_or_append( "from webhelpers.html import escape",
                          template,
                          "imports" )
    try:
        globs = pylons_globals()
    except TypeError:
        globs = dict()

    context = Context( _get_buffer( template,
                                    as_unicode ),
                       **dict( kwargs,
                               tags=tags,
                               tools=tools,
                               s=s,
                               shorties=shorties,
                               sleepy=sleepy,
                               **globs ))
    context._outputting_as_unicode = as_unicode
    context._with_template = template
    getattr( Namespace( s( "self:{{ template.uri }}",
                           locals()),
                        context,
                        template=template ),
             deff )( **kwargs )
    return context._pop_buffer().getvalue()

def _cache( use_cache=True ):
    if use_cache is True:
        return config[ "pylons.app_globals" ].cache
    else:
        return use_cache

def _lookup():
    return config[ "pylons.app_globals" ].sleepy_lookup

class Page( object ):
    def __init__( self,
                  name,
                  link_text=None,
                  nav=True,
                  section=None,
                  **kwargs ):
        self.name = name
        self.nav = nav
        self.section = section
        for ( k,
              v ) in dict( link_text=link_text,
                           **kwargs ).items():
            if v is not None:
                setattr( self,
                         s( "_{{ k }}",
                            k=k ),
                         v )

    @property
    def link_text( self ):
        try:
            return self._link_text
        except AttributeError:
            return self.name

    @property
    def header_text( self ):
        try:
            return self._header_text
        except AttributeError:
            return self.link_text

    @property
    def title( self ):
        try:
            return self._title
        except AttributeError:
            return self.header_text

    @property
    def url( self ):
        try:
            return self._url
        except AttributeError:
            return url.current( page=self.name )

class Entries( object ):
    def __init__( self,
                  entry_class,
                  user_config_key,
                  createfunc,
                  cache_name,
                  cache_expire=600,
                  cache_type="file" ):
        self.entry_class = entry_class
        self.user_config_key = user_config_key
        self.createfunc = createfunc
        self.cache_name = cache_name
        self.cache_type = cache_type
        self.cache_expire = cache_expire

    def __call__( self,
                  user=None,
                  use_cache=True ):
        def _entries():
            def _user():
                return ( user
                         if user is not None
                         else config[ self.user_config_key ] )
            def _create():
                return self.createfunc( _user())
            if use_cache:
                return _cache( use_cache ).get_cache( self.cache_name,
                                                      type=self.cache_type,
                                                      expire=self.cache_expire
                                         ).get( key=_user(),
                                                createfunc=_create )
            else:
                return _create()
        try:
            return [ self.entry_class( entry,
                                       user=user,
                                       use_cache=use_cache )
                     for entry
                     in _entries() ]
        except RequestError:
            return []

def cacher( cache_name,
            key,
            createfunc,
            cache_expire=600,
            cache_type="file" ):
    return ( _cache().get_cache( cache_name,
                                 type=cache_type,
                                 expire=cache_expire )
                     .get( key=key,
                           createfunc=createfunc ))
