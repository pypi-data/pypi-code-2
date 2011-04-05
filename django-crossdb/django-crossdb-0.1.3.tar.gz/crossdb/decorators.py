from functools import wraps


def fks_from_objects(method, **name_mapping):
    '''
    A decorator for getting foreign key values from objects by
    getting their ``id`` attribute.

    Example usage::

        def filter(book_fk=None, author_fk=None):
            # ...
        filter = fks_from_objects(filter, book_fk='book')

    In this example, the ``filter`` function will take the ``book`` 
    keyword argument and send the ``id`` attribute of it as the
    ``book_fk`` keyword argument.

    This is most useful for changing the interface of a function. It
    is primarily used by :func:`crossdb.ManagerMetaclassFactory`.
    '''
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        for new_name, name in name_mapping.iteritems():
            if name in kwargs:
                obj = kwargs.pop(name)
                kwargs[new_name] = obj.id

        return method(self, *args, **kwargs)

    return wrapper

