import dm.testunit

class TestCase(dm.testunit.TestCase):
    "Base class for View TestCases."
    
    def buildRequest(self):
        return None

