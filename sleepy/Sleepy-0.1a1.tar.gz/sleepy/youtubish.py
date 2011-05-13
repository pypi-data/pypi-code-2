from gdata.youtube.service import YouTubeService

from sleepy.shorties import Ago, s, Duration, date_parse
from sleepy.lonsies import Entries

class Video( object ):
    def __init__( self,
                  entry,
                  user=None,
                  use_cache=True ):
        self.title = entry.media.title.text
        self.description = entry.media.description.text
        self.duration = Duration( entry.media.duration.seconds )
        self.published = date_parse( entry.published.text )
        self.updated = date_parse( entry.updated.text )
        self.watch_url = entry.media.player.url
        self.flash_url = entry.GetSwfUrl()
        self.thumbnail = entry.media.thumbnail[ 3 ].url

    @property
    def ago( self ):
        return Ago( self.published )

def uri( user ):
    return s( "http://gdata.youtube.com/feeds/api/users/{{ user }}/uploads",
              user=user )

def service():
    return YouTubeService()

videos = Entries( entry_class=Video,
                  user_config_key="youtube_user",
                  createfunc=lambda user:
                              service()
                               .GetYouTubeVideoFeed( uri( user ))
                               .entry,
                  cache_name="youtube_feed" )
