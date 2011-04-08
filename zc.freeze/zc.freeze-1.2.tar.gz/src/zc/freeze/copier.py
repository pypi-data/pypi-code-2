
import zope.component
import zope.interface

import zc.copy.interfaces
import zc.freeze.interfaces

# this can be used to rip off old versioning data and put new values in place
@zope.component.adapter(zc.freeze.interfaces.IData)
@zope.interface.implementer(zc.copy.interfaces.ICopyHook)
def data_copyfactory(obj):
    def factory(location, register):
        return None
    return factory
