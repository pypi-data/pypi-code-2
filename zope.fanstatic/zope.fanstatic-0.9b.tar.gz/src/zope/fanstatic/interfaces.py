from zope.interface import Interface

class ISetupZopeFanstatic(Interface):
    pass

class IZopeFanstaticResource(Interface):

    def get(name, default):
        pass

    def __getitem__(self, name):
        pass

