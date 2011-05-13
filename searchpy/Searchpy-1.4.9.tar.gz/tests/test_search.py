from unittest        import TestCase

from searchpy.search import Search

class TestSearch(TestCase):
    """Test Searchpy search functions."""
    
    def test_google_search(self):
        """Test standard search."""
        
        # Search with a standard query using defaults
        search = Search('python rocks')
        
        assert search.results != None
        assert isinstance(search.results, list)
        assert search.results[1]['url'] != None
        
        # Search with a different tld and different language
        search = Search('python rocks', tld='de', lang='de')
        
        assert search.results != None
        assert isinstance(search.results, list)
        assert search.results[1]['url'] != None
        
        # Search using some proxies (this is tough because google actively blocks public proxies)
        # search = Search('python rocks', proxies=['190.176.6.40', '84.11.139.211'])
        
        # assert search.results != None
        # assert isinstance(search.results, list)
        # assert search.results[1]['url'] != None

    def test_bing_search(self):
        """Test standard search."""
        
        # Search with a standard query using defaults
        search = Search('python rocks', engine='bing')
        
        assert search.results != None
        assert isinstance(search.results, list)
        assert search.results[1]['url'] != None
        
        # Search using some proxies (this is tough because google actively blocks public proxies)
        # search = Search('python rocks', proxies=['190.176.6.40', '84.11.139.211'])
        
        # assert search.results != None
        # assert isinstance(search.results, list)
        # assert search.results[1]['url'] != None
        
    def test_paging(self):
        """Test the paging functionality."""
        
        search = Search('python rocks')
        
        assert search.start == 0
        
        # Implicitly page it
        search.page()
        
        assert search.start == 10
        
        # Explicitly page it
        search.page(5)
        assert search.start == 40 # Because page results start at 0 :)
    
    def test_iter(self):
        """Test iterating over the search results."""
        
        search = Search('python rocks')
        
        for result in search:
            assert isinstance(result, dict)
