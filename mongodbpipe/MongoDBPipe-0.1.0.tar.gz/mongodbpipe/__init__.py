from pipestack.pipe import Marble, MarblePipe
from bn import AttributeDict
from conversionkit import Field
from stringconvert import unicodeToUnicode, unicodeToInteger
from pymongo import Connection

#
# Pipe representing a database
#

class MongoDBDatabaseMarble(Marble):
    def __getitem__(marble, name):
        return marble.__dict__['persistent_state'].database[name]

    def __getattr__(marble, name):
        return marble.__dict__['persistent_state'].database[name]

class MongoDBDatabasePipe(MarblePipe):
    marble_class = MongoDBDatabaseMarble
    options = dict(
        host = Field(
            unicodeToUnicode(),
            missing_or_empty_default = "localhost",
        ),
        port = Field(
            unicodeToInteger(),
            missing_or_empty_default = 27017
        ),
        database = Field(
            unicodeToUnicode(),
            missing_or_empty_error = "Expected the %(name)s.database option to be present"
        )
    )

    def on_parse_options(self, bag):
        MarblePipe.on_parse_options(self, bag)
        # PyMongo uses a threadsafe connection pool internally and MongoDB
        # doesn't support transactions so no harm in keeping one global
        # connection shared between requests.
        self.persistent_state = AttributeDict(
            database = getattr(
                Connection(
                    bag.app.config[self.name].host, 
                    bag.app.config[self.name].port,
                ),
                bag.app.config[self.name].database,
            ),
        )

##
## Pipe representing a connection
##
#
#class MongoDBConnectionMarble(Marble):
#    def __getitem__(marble, name):
#        return marble.__dict__['persistent_state'].connection[name]
#
#    def __getattr__(marble, name):
#        return marble.__dict__['persistent_state'].connection[name]
#
#    def on_set_persistent_state(self, persistent_state):
#        self.connection = persistent_state.connection
#
#class MongoDBConnectionPipe(MarblePipe):
#    marble_class = MongoDBConnectionMarble
#    options = dict(
#        host = Field(
#            unicodeToUnicode(),
#            missing_or_empty_default = "localhost",
#        ),
#        port = Field(
#            unicodeToInteger(),
#            missing_or_empty_default = 27017
#        ),
#    )
#
#    def on_parse_options(self, bag):
#        MarblePipe.on_parse_options(self, bag)
#        connection = Connection(bag.app.config.host, bag.app.config.port)
#        self.persistent_state = AttributeDict(connection=connection)

