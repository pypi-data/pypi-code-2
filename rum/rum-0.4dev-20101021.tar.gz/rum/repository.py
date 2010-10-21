import sys
import types
import logging
from itertools import ifilter, chain
from inspect import getargspec, isclass

from peak.util.decorators import decorate_assignment, decorate_class
from peak.rules.core import istype

from rum.genericfunctions import generic, when, NoApplicableMethods
from rum.basefactory import BaseFactory
from rum.query import QueryFactory
from rum import util, interfaces, fields, transaction
from rumcomponent.util import import_string

__all__ = ["RepositoryFactory", "Repository", "names_for_resource"]

log = logging.getLogger(__name__)

class RepositoryFactory(BaseFactory):
    field_factory = fields.FieldFactory()
    
    def __init__(self, scan_modules=[], models=[], field_factory=None): 
        self._models = list(models)
        self._scan_modules = list(scan_modules)
        self.resources = {}
        if field_factory:
            self.field_factory = field_factory

    @generic
    def get(self, resource, parent=None, remote_name=None, action=None,
            args=None):
        """
        Returns a class implementing :class:`rum.interfaces.IRepository`.
        """

    def __call__(self, resource, parent=None, remote_name=None, action=None,
                 parent_id=None):
        get_repo = super(RepositoryFactory, self).__call__
        repo = get_repo(resource, parent, remote_name=remote_name,
                        action=action)
        repo.parent_id = parent_id
        repo.join_transaction()
        return repo

    def get_id(self, obj):
        return self(obj.__class__).get_id(obj)


    @generic
    def names_for_resource(self, resource):
        pass
    names_for_resource.__doc__ = interfaces.IRepositoryFactory.names_for_resource.__doc__


    @names_for_resource.when("isclass(resource)", prio=-1)
    def _default_names_for_resource(self, resource):
        name = resource.__name__.lower()
        if name.endswith('s'):
            plural = name + 'es'
        elif name.endswith('y'):
            plural = name[:-1] + 'ies'
        else:
            plural = name + 's'
        return name, plural

    @names_for_resource.when("not isclass(resource)", prio=-1)
    def _default_names_for_instance(self, resource):
        return self.names_for_resource(resource.__class__)




    def set_names(cls, obj, singular, plural):
        pred_type = "isinstance(self, cls) and resource is obj"
        pred_inst = "isinstance(self, cls) and isinstance(resource, obj)"
        NAMES = lambda self, resource: (singular, plural)
        cls.names_for_resource.when(pred_type)(NAMES)
        cls.names_for_resource.when(pred_inst)(NAMES)
    
    set_names.__doc__ = interfaces.IRepositoryFactory.set_names.__doc__
    set_names = classmethod(set_names)


    def fields_for_resource(self, resource, attr=None):
        return self.field_factory(resource, attr)


    def load_resources(self):
        to_scan = []
        for mod in self._scan_modules:
            mod = import_string(mod)
            for name in getattr(mod, '__all__', dir(mod)):
                if not name.startswith('_'):
                    to_scan.append(getattr(mod, name))
        to_scan.extend(map(import_string, self._models))
        log.debug('loading_resources from %r', to_scan)
        map(self.register_from, to_scan)
        log.debug('loaded: %r', self.resources)
        return self.resources

    def cleanup(self, app):
        pass



    def register_resource(self, resource, parent=None, attr=None):
        log.debug("register_resource: %r", locals())
        if parent:
            assert attr
            self.resources.setdefault(parent, {})[attr] = resource
        else:
            self.resources.setdefault(resource, {})





    @generic
    def register_from(self, obj):
        """
        Registers resources it finds and knows how to handle in obj-
        """
    # Don't crash on NoApplicableMethods
    register_from.when()(lambda self,obj:None)

    @register_from.when("isclass(obj) and self.can_handle(obj)", prio=-10)
    def _register_obj(self, obj):
        log.debug('_register_obj: %r', locals())
        self.register_resource(obj)
        for field in (self.fields_for_resource(obj) or []):
            if isinstance(field, fields.Collection):
                self.register_resource(field.other, parent=obj, attr=field.name)
            else:
                if isinstance(field, fields.Binary):
                    self.register_resource(
                        field.__class__,
                        parent=obj,
                        attr=field.name
                    )


class Repository(object):
    """
    A base repository.

    Handles all access to the data backend.

    It also implemenents the IDataManager interface so it can
    participate in a transaction.
    """
    # These should be a string that never appears in a stringified id
    composite_id_separator = ':::'
    slash_replacement = ';;;'  # This one is because routes will fail to parse
                               # the url if an id contains a slash

    transaction_manager = None
    queryfactory = QueryFactory()

    _parent_obj = None
    _parent_repository = None

    def __init__(self, resource, factory, parent=None, remote_name=None,
                 parent_id=None):
        self.resource = resource
        self.parent = parent
        self.remote_name = remote_name
        self.factory = factory
        self.parent_id = parent_id
    
    @property
    def parent_repository(self):
        if self._parent_repository is None and self.parent:
            self._parent_repository = self.factory(self.parent) 
        return self._parent_repository

    @property
    def parent_obj(self):
        if self._parent_obj is None and self.parent_repository:
            assert self.parent_id is not None
            self._parent_obj = self.parent_repository.get(self.parent_id)
        return self._parent_obj

    @property
    def default_value(self):
        return self.factory.field_factory.defaults(self.resource)

    def make_query(self, request_args=None, **kw):
        return self.queryfactory(self.resource, request_args, **kw)

    def join_transaction(self):
        # Add the repository to the transaction manager
        current = transaction.get()
        current.join(self)


    def get_id(self, obj):
        """
        Returns a string representing the id for this object.
        This expression should always be True::

            repository.get(repository.get_id(obj)) == obj
        """
        raise NotImplementedError("Subclasses must extend this method")

    def split_id(self, id):
        """
        Returns a tuple with the components of an id
        """
        return id.split(self.composite_id_separator)

    def commit(self, transaction):
        """ See IDataManager.
        """

    def abort(self, transaction):
        """ See IDataManager.
        """

    def tpc_begin(self, transaction):
        """ See IDataManager.
        """

    def tpc_vote(self, transaction):
        """ See IDataManager.
        """

    def tpc_finish(self, transaction):
        """ See IDataManager.
        """

    def tpc_abort(self, transaction):
        """ See IDataManager.
        """

    def sortKey(self):
        """ See IDataManager.
        """
        return str(id(self))

# Note that these are not the same as the shortcuts in rum.*!
# They exported here to be extended with custom rules
names_for_resource = RepositoryFactory.names_for_resource.im_func
register_from = RepositoryFactory.register_from.im_func