from zope.interface import Interface, Attribute

class IOracle(Interface):
    """ Root object """

class ICategory(Interface):
    """ A category """
    title = Attribute("A pretty title")

class IDebugger(Interface):
    """ ZCA aware PDB """

    # TODO.
