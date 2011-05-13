import twitter

from sleepy.shorties import Ago
from sleepy.lonsies import Entries

class Tweet( object ):
    def __init__( self,
                  d,
                  user=None,
                  use_cache=True ):
        self.published = d.published
        self.message = d.text

    @property
    def ago( self ):
        return Ago( self.published )

posts = Entries( entry_class=Tweet,
                 user_config_key="twitter_user",
                 cache_name="twitter_posts",
                 createfunc=lambda user:
                             twitter.Api()
                                    .GetUserTimeline( user ))
