from zope.interface import Interface

class TestTestSwarmBrowserLayer(Interface):
    """ To avoid test resources and views being registered for users
    of the TESTSWARM_LAYER
    """

