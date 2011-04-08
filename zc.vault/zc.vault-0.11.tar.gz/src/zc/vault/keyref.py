import itertools
import persistent
from ZODB.interfaces import IConnection
from zope import interface
from zope.cachedescriptors.property import Lazy
import zope.app.keyreference.interfaces
import zope.app.container.contained
from zc.vault import interfaces

class AbstractUniqueReference(object):
    interface.implements(
        zope.app.keyreference.interfaces.IKeyReference,
        interfaces.IUniqueReference)

    __slots__ = ()

    # must define identifiers and key_type_id

    def __call__(self):
        return self

    def __hash__(self):
        return hash(tuple(self.identifiers))

    def __cmp__(self, other):
        if interfaces.IUniqueReference.providedBy(other):
            return cmp(tuple(self.identifiers), tuple(other.identifiers))
        if zope.app.keyreference.interfaces.IKeyReference.providedBy(other):
            assert self.key_type_id != other.key_type_id
            return cmp(self.key_type_id, other.key_type_id)
        raise ValueError(
            "Can only compare against IUniqueIdentity and "
            "IKeyReference objects")

# XXX this is API; need to highlight in tests...
def getPersistentIdentifiers(obj):
    if obj._p_oid is None:
        connection = IConnection(obj, None)
        if connection is None:
            raise zope.app.keyreference.interfaces.NotYet(obj)
        connection.add(obj)
    return (obj._p_jar.db().database_name, obj._p_oid)

class Token(AbstractUniqueReference, persistent.Persistent,
            zope.app.container.contained.Contained):

    interface.implements(interfaces.IToken)

    __slots__ = ()

    key_type_id = 'zc.vault.keyref.Token'

    @Lazy
    def identifiers(self):
        return (self.key_type_id,) + getPersistentIdentifiers(self)

class _top_token_(AbstractUniqueReference): # creates singleton

    interface.implements(interfaces.IToken)

    __slots__ = ()

    key_type_id = 'zc.vault.keyref.TopToken'

    identifiers = (key_type_id,)

    def __reduce__(self):
        return _top_token, ()

top_token = _top_token_()

def _top_token():
    return top_token
_top_token.__safe_for_unpickling__ = True
