from crossdb.decorators import fks_from_objects
from crossdb.related import ForeignKey, RelatedSet


def ManagerMetaclassFactory(**fk_to_object_mapping):
    '''
    A factory function for creating a metaclass that uses the
    ``fk_to_object_mapping`` keyword arguments to wrap the ``filter`` 
    and ``exclude`` manager methods with the 
    :func:`crossdb.decorators.fks_from_objects` decorator.
    '''
    class CrossDbManager(type):
        def __new__(cls, name, bases, attrs):
            base = bases[0]

            attrs['filter'] = fks_from_objects(base.filter, **fk_to_object_mapping)
            attrs['exclude'] = fks_from_objects(base.exclude, **fk_to_object_mapping)

            return super(MultiDbManager, cls).__new__(cls, name, bases, attrs)

    return CrossDbManager
