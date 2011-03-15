from unittest           import TestCase

from googlepy.utilities import *

class TestUtilities(TestCase):
    """Test GooglePy utlities functions."""
    
    def test_pagerank(self):
        """Test the page rank utility."""
        
        pr = PageRank.calculate('http://python.org')
        assert isinstance(pr, int)
