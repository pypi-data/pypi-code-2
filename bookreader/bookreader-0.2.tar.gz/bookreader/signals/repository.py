
def lookup_name(sender, instance, **kwargs):
    instance.name = unicode(instance.connection().getName())
    
