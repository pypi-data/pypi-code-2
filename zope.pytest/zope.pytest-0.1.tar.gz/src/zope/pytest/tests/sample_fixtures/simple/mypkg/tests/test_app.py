from zope.interface.verify import verifyClass, verifyObject
from mypkg.app import SampleApp
from mypkg.interfaces import ISampleApp

def test_app_create():
    # Assure we can create instances of `SampleApp`
    app = SampleApp()
    assert app is not None

def test_app_class_iface():
    # Assure the class implements the declared interface
    assert verifyClass(ISampleApp, SampleApp)

def test_app_instance_iface():
    # Assure instances of the class provide the declared interface
    assert verifyObject(ISampleApp, SampleApp())
