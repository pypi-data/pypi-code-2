import dm.testunit
import kforge.builder
import kforge.soleInstance

class TestCase(dm.testunit.TestCase):
    pass

class ApplicationTestSuite(dm.testunit.ApplicationTestSuite):
    appBuilderClass = kforge.builder.ApplicationBuilder

