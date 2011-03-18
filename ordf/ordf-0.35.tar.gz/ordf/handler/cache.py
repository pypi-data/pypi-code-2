#from ordf.handler import HandlerPlugin
#from ordf.namespace import RDFS
#import redis
#
#class Redis(HandlerPlugin):
#    def __init__(self, *av, **kw):
#        self.db = redis.Redis(*av, **kw)
#    def cset(self, cs):
#        self.db.lpush("RecentChanges", cs.metadata.serialize(format="n3"))
#        if self.db.llen("RecentChanges") > 10:
#            self.db.rpop("RecentChanges")
