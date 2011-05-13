from sleepy.shorties import s, date_parse
from sleepy.lonsies import Entries
from gdata.photos.service import PhotosService

_pws = None
def _pw_service():
    global _pws
    if not _pws:
        _pws = PhotosService()
    return _pws

class Album( object ):
    sort_key = "updated"

    def __init__( self,
                  entry,
                  user=None,
                  use_cache=True ):
        self.yd = entry.gphoto_id.text
        self.title = entry.title.text
        self.published = date_parse( entry.published
                                          .text )
        self.updated = date_parse( entry.updated
                                        .text )
        self.pictures = pictures( self,
                                  user,
                                  use_cache )

class Picture( object ):
    def __init__( self,
                  entry,
                  user=None,
                  use_cache=True ):
        self.title = entry.title.text
        self.uri = entry.content.src
        self.thumbnail = entry.media.thumbnail[ 1 ].url

def pictures( album,
              user=None,
              use_cache=True ):
    return Entries( entry_class=Picture,
                    user_config_key="picasaweb_user",
                    createfunc=lambda user:
                                _pw_service()
                                   .GetFeed( s( "/data/feed/api/user"
                                                 "/{{ user }}/albumid"
                                                 "/{{ album }}?kind=photo",
                                                user=user,
                                                album=album.yd ))
                                   .entry,
                    cache_name=s( "picasaweb_album_{{ album }}",
                                  album=album.yd ))( user=user,
                                                     use_cache=use_cache )

albums = Entries( entry_class=Album,
                  user_config_key="picasaweb_user",
                  createfunc=lambda user:
                              _pw_service()
                               .GetUserFeed( user=user )
                               .entry,
                  cache_name="picasaweb_feed" )
