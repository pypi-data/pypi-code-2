import facebook
import re

from sleepy.shorties import Ago, date_parse, date_str
from sleepy.lonsies import Entries, cacher

import logging

log = logging.getLogger( __name__ )
if not logging.root.handlers:
    logging.basicConfig()
log.setLevel( logging.DEBUG )

event_re = re.compile( r"""
                            facebook.com
                            .*
                            event
                           """,
                          re.X )

class Event( object ):
    def __init__( self,
                  d ):
        self.start = date_parse( d[ "start_time" ] )
        self.end = date_parse( d[ "end_time" ] )
        self.updated = date_parse( d[ "updated_time" ] )
        self.description = d.get( "description" )
        self.name = d.get( "name" )
        self.id = d.get( "id" )
        self.location = d.get( "location" )
        self.privacy = d.get( "privacy" )
        self.venue = d.get( "venue" )

class Post( object ):
    def __init__( self,
                  d,
                  user=None,
                  use_cache=True ):
        self.published = date_parse( d[ "created_time" ] )
        self.updated = date_parse( d[ "updated_time" ] )
        self.message = d.get( "message" )
        self.link = d.get( "link" )
        self.frum = d.get( "from" )
        self.tipe = d.get( "type" )
        self.id = d.get( "id" )
        self.object_id = d.get( "object_id" )
        self.name = d.get( "name" )
        self.icon = d.get( "icon" )
        self.event = self._event()
        self.properties = self._properties( d.get( "properties" ))
        self.picture = d.get( "picture" )
        self.description = d.get( "description" )
        self.source = d.get( "source" )
        self.caption = d.get( "caption" )

    def _event( self ):
        if not self.link:
            return None
        match = event_re.search( self.link )
        if not match:
            return None
        else:
            return Event( cacher( cache_name="facebook_events",
                                  key=self.object_id,
                                  createfunc=lambda:
                                              facebook.GraphAPI()
                                                      .get_object( self.object_id )))

    def _properties( self,
                     props ):
        if not props:
            return []

        def _property( prop ):
            try:
                # was parsing video lengths as dates
                if len( prop[ "text" ] ) < 10:
                    return prop

                dt = date_parse( prop[ "text" ] )
                prop[ "text" ] = date_str( self.event
                                               .start,
                                           smusher=None,
                                           time_space=False )
                return prop
            except ( ValueError, KeyError ):
                return prop

        properties = []
        for prop in props:
            _p = _property( prop )
            properties.append( _p )
        return properties

    @property
    def ago( self ):
        return Ago( self.published )

posts = Entries( entry_class=Post,
                 user_config_key="facebook_user",
                 cache_name="facebook_posts",
                 createfunc=lambda user:
                             facebook.GraphAPI()
                                     .get_connections( user,
                                                       "posts" )
                                     [ "data" ] )
