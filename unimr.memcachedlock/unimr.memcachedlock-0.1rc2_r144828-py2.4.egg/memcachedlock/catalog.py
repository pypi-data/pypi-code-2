import memcachedlock

from wrapper import wrap_method, call

def get_key(fun,*args,**kargs):
    fun, instance = args[0:2]
    return '/'.join(instance.getPhysicalPath())

@memcachedlock.zlock(get_key)
def catalog_object(self, *args, **kw):
    """ ZCatalog's catalog_object """

    call(self, 'catalog_object', *args, **kw)


def patch(scope,original,replacement):
    wrap_method(scope, original, replacement)

