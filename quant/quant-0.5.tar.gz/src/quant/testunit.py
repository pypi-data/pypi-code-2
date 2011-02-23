from dm.testunit import ApplicationTestSuite
from dm.testunit import TestCase
from quant.builder import ApplicationBuilder

VOLATILITY_MEDIUM = 1.0
VOLATILITY_LOW = 0.3333
VOLATILITY_HIGH = 3.0
VOLATILITY_ZERO = 0.00001

class TestCase(TestCase):
    "Base class for quant TestCases."

class ApplicationTestSuite(ApplicationTestSuite):
    appBuilderClass = ApplicationBuilder

