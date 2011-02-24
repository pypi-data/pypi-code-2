from dm.testunit import ApplicationTestSuite
from dm.testunit import TestCase
from provide.builder import ApplicationBuilder

class TestCase(TestCase):
    "Base class for provide TestCases."

class ApplicationTestSuite(ApplicationTestSuite):
    appBuilderClass = ApplicationBuilder

