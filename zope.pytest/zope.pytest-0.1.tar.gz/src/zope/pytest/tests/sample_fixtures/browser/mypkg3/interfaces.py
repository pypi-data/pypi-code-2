import zope.interface

class ISampleApp(zope.interface.Interface):
    """A sample application.
    """
    pass

class IFoo(zope.interface.Interface):
    """A Foo.

    Foos can do foo.
    """
    def do_foo():
        """Do the foo.
        """
        pass
