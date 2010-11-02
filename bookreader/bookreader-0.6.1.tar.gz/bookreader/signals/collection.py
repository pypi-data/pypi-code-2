from bookreader import harvesting

def lookup_name(sender, instance, **kwargs):
    connection = instance.repository.connection()
    setSpec = connection._extractSet(instance.handle)
    
    collections = dict(connection.getCollections())
    
    if setSpec in collections:
        instance.name = unicode(collections[setSpec])
        return
    
    instance.handle = None
    instance.name = None

def load_books(sender, instance, created, **kwargs):
    harvesting.load_books(instance)
