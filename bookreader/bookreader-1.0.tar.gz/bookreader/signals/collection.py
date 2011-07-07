from logging import getLogger
from urllib2 import URLError

from bookreader import harvesting



log = getLogger('bookreader.signals.collection')

def lookup_name(sender, instance, **kwargs):
    try:
        connection = instance.repository.connection()
        setSpec = connection._extractSet(instance.handle)
        
        collections = dict(connection.getCollections())
        
        if setSpec in collections:
            instance.name = unicode(collections[setSpec])
            return
        
        instance.handle = None
        instance.name = None
    except URLError:
        log.debug('Unable to contact the repository')
    except:
        log.exception("Error while looking up collection name")

def load_books(sender, instance, created, **kwargs):
    try:
        harvesting.load_books(instance)
    except URLError:
        log.debug('Unable to contact the repository')
    except:
        log.exception("Error while loading books in the collection")
