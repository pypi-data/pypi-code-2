class Engine(object):
    def __init__(self, query, tld, country, lang):
        self.tld     = tld
        self.country = country
        self.lang    = lang
        
        self.endpoint = 'http://www.google.%s/search' % self.tld
        self.options  = {'q'  : query,
                         'hl' : self.lang,
                         'gl' : self.country,
                         'start' : 0
                        }
    
    def _get_start(self):
        return self.options['start']
    def _set_start(self, value):
        self.options['start'] = value
    
    start = property(_get_start, _set_start, "Paging start set")

def parse(results, start=0):
    """Parse the html results into a data structure."""
    
    from pyquery           import PyQuery as pq
    from searchpy.adapters import remove_tags
    
    doc = pq(results)
    res = doc("#ires")
    rec = res(".g")
    
    # Make each element an instance of pq
    recs  = [pq(x) for x in rec]
    items = [{'start' : start}]
    
    # Step through each element and build a dictionary of their useful values
    for record in recs:
        url    = record('.vsc')('.tl')('.r')('a')
        
        if len(url) > 0:
            pieces = {'url'    : url.attr('href'),
                      'title'  : remove_tags(url.text()),
                      'cached' : record('.vsc')('.s')('a').attr('href')}
            
            items.append(pieces)
    
    return items
