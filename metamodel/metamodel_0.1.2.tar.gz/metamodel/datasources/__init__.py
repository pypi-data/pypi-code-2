"""
DataSources are responsible for creating and deleting nodes.

They are 'intelligent' models capable of creating, tracking and possibly
persisting a number of submodels and changes to those models.

They are themselves models too, so they become persisted by the parent
datasource, and can delegate persistence of any number of subnodes to
their parent datasources.

The node creation process plays a key role in this mechanism, and is where
the datasource can claim owning of a model node (which is the default
behaviour).

Node creation works as follows:
 - SubscribableModel.new (called on an instance) will create an instance
   belonging to the same datasource, and calls DataSource.new so the datasource
   can process the request.
 - SubscribableModel() (called on an instance) will create a "free" instance.

Node deletion always works through SubscribableModel.invalidate()
"""

from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property
from metamodel.meta import ClassRegistry

class Folder(SubscribableModel):
    name = Property(str,"a folder")
    builds = ["SubscribableModel"]
    builtby = ["DataSource"]

class DataSource(SubscribableModel):
    """
    Base class for all datasources.
    """
    name = Property(str,"a data source")

    def new(self, clsname, instance_uuid=None, *args, **kwargs):
        """
        Create a new model from a classname, with the given args and kwargs.
        """
        if isinstance(clsname,str):
            klass = ClassRegistry[clsname]
        else:
            klass = clsname
        inst = klass(instance_uuid,
                     self,
                     *args,
                     **kwargs)
        return inst

    def invalidate(self, node = None):
        """
        Invalidate a node, or this datasource.
        """
        if node and not isinstance(node, bool):
            node.invalidate(True)
        else:
            SubscribableModel.invalidate(self)

    def own(self, model, recursive=True, stack=None):
        """
        Own a model, by releasing from the previous datasource
        and aquiring it.
        """
        if not stack:
            stack = []
        if not model in stack:
            if model._datasource:
                model._datasource.release(model)
            self.accept(model)
            if recursive:
                stack.append(model)
                for child in model.getAllReferences():
                    self.own(child, recursive, stack)

    def accept(self, model):
        """
        Accept a model into this datasource.
        Throw an exception if the datasource cannot accept.
        """
        model._datasource = self

    def release(self, model):
        """
        Release a model from this datasource.
        Throw an exception if the datasource cannot release.
        """
        model._datasource = None


class DataSourceRoot(SubscribableModel):
    """
    Common root datasources can use as a container for other nodes,
    as datasources cannot directly serialize themselves as it would cause
    recursive loading of itself.
    """
    pass

