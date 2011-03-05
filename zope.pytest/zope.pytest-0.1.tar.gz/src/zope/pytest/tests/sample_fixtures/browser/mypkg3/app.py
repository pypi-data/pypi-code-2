from zope.interface import implements
from mypkg3.interfaces import ISampleApp, IFoo

class SampleApp(object):
    implements(ISampleApp)

class FooUtility(object):
    implements(IFoo)

    def do_foo(self):
        return "Foo!"
