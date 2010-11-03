"""
Model for model description.
"""

from basemodel import SubscribableModel

from properties import Property

class NamespaceFolder(SubscribableModel):
    """
    Dummy model that creates ontologies.
    """
    builds = ["Namespace"]

class MetaProperty(SubscribableModel):
    """
    Information about a property.
    """
    name = Property(str,"unnamed_property")
    type = Property(str,"str")
    ro = Property(bool,False)
    default = Property(str,"default")

class MetaModel(SubscribableModel):
    """
    Information about a class.
    """
    classname = Property(str,"UnnamedModel")
    name = Property(str,"A yet unnamed model")

    inheritfrom = Property(list,[])

    builtby_list = Property(list,[])
    builds_list = Property(list,[])

    builds = ["MetaProperty"]

class Namespace(SubscribableModel):
    """
    A set of classes.
    """
    name = Property(str,"Unnamed Namespace")

    builds = ["MetaModel", "Namespace"]

