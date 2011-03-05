from zope.interface import implements
from mypkg.interfaces import ISampleApp

class SampleApp(object):
    implements(ISampleApp)
