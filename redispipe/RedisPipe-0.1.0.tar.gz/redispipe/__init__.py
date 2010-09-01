from pipestack.pipe import Marble, MarblePipe
from redis import Redis
from bn import AttributeDict
from conversionkit import Field
from stringconvert import unicodeToUnicode

class RedisMarble(Marble):
    def on_set_persistent_state(self, persistent_state):
        self.connection = persistent_state.connection

class RedisPipe(MarblePipe):
    marble_class = RedisMarble
    options = dict(
        host = Field(
            unicodeToUnicode(),
            missing_or_empty_default = "localhost",
        ),
    )

    def on_parse_options(self, bag):
        MarblePipe.on_parse_options(self, bag)
        self.persistent_state = AttributeDict(
            connection = Redis(host=bag.app.config[self.name].host)
        )

