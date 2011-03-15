import urllib
import mechanize
import random

providers = ('google', 'bing')

class SearchException(Exception):
    """Search API exception class."""
    pass

class NoResults(SearchException):
    pass

class Search(object):
    """Interface class for scraping web search."""
    
    def __init__(self, query, engine='google', tld='com', country='US', lang='en', ua=None, proxies=None):
        """Prepare to scrape!"""
        
        engine = engine.lower()
        
        if engine not in providers:
            raise SearchException('the specified provider is not supported')
        
        self.adapter_module  = __import__('searchpy.adapters.%s' % engine, fromlist=['searchpy.adapters'])
        self.adapter    = self.adapter_module.Engine(query, tld, country, lang)
        
        self.query      = query
        self.proxies    = proxies
        self.endpoint   = self.adapter.endpoint
        
        self.raw        = None
        self.results    = None
        self.request    = None
        self.proxy      = None
        self.ua         = ua
        
        self.garbage    = []
        
        self.index      = 0
        
        self._search()
    
    def _search(self, start=0):
        """Run a query against the Search Search API."""
        
        # Start is always a multiple of the number of results returned
        self.adapter.start = start
        self.start         = self.adapter.start
        
        rq = mechanize.Browser()
        
        # Proxy? (I hope so!)
        if self.proxies != None:
            self.proxy = random.choice(self.proxies)
            rq.set_proxies({'http' : self.proxy})
        
        # Set options
        rq.set_handle_robots(False)
        rq.set_handle_equiv(True)
        rq.set_handle_gzip(True)
        rq.set_handle_redirect(True)
        rq.set_handle_referer(True)
        rq.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
        
        # User-Agent
        rq.addheaders = [('User-agent', (self.ua if self.ua != None else 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; en-US) AppleWebKit/534.13 (KHTML, like Gecko) Chrome/9.0.597.84 Safari/534.13'))]
        
        # Debug messages
        #rq.set_debug_http(True)
        #rq.set_debug_redirects(True)
        #rq.set_debug_responses(True)
        
        # Make the connection...
        request      = self.endpoint + '?' + urllib.urlencode(self.adapter.options)
        self.request = request
        
        response     = self._try(rq, request)
        response     = response.read()
        
        self.raw     = response
        self.results = self.adapter_module.parse(response, start)
        
        # Be sure to reset the request index so the iterator can "restart"
        self.index = 0
    
    def page(self, page=None):
        """Page the search results.
        
        If no argument is provided it defaults to fetching and
        returning the next "page". If a page number is provided it
        will be calculated based on the start values in the result
        set.
        
        """
        
        if page:
            # Deliberate seek
            if page < 1:
                raise SearchException('page must be 1..n')
            
            page = (page - 1) * 10
        else:
            # Implicit seek
            page = self.adapter.options.start + 10
            
        self._search(start=page)
    
    def _try(self, browser, request):
        try:
            response = browser.open(request)
        except mechanize.HTTPError as error:
            if (self.proxies != None) and (error.code in (503, 504, 305, 403)):
                print 'HTTP Error: %d' % error.code
                
                # First, let's make sure garbage doesn't match the proxy list
                grb = set(self.garbage)
                prx = set(self.proxies)
                
                if prx.issubset(grb):
                    raise SearchException('all proxies have been exhausted')
                
                # Put the failed proxy into garbage
                self.garbage.append(self.proxy)
                
                # Select a new one
                self.proxy = random.choice(self.proxies)
                browser.set_proxies({'http' : self.proxy})
                
                # Recursion... (too bad Python doesn't TCR)
                response = self._retry(browser, request)
            else:
                raise
        
        return response
    
    def __repr__(self):
        """Object representation of the search object."""
        
        query  = self.query if self.query is not None else 'Empty'
        
        msg = '<%s at 0x%x Query: "%s", Page Index:%s>' % (self.__class__.__name__, abs(id(self)), query, self.index)
        
        return msg
    
    def __str__(self):
        """String representation will return the query."""
        
        return self.query
    
    def next(self):
        """Produce the next item in the result set."""
        
        # Have we any results to begin with?
        if self.results == None:
            raise StopIteration
        
        # Pop the first value off the list, it's just he start value dict...        
        results = self.results[1:]
        
        if self.index >= len(results):
            raise StopIteration
        
        result = results[self.index]
        self.index += 1
        
        return result
    
    def __iter__(self):
        """Iterable representation of the search results."""
        
        return self
