import urllib
import simplejson
import itertools
import logging

URL = 'http://boss.yahooapis.com/ysearch/web/v1/%s?appid=%s&style=raw&type=html&count=%d'

def api_call(url):
    data = urllib.urlopen(url=url).read()
    print url
    print data
    return simplejson.loads(data)['ysearchresponse']


def search(apikey, query, per_page=50, start=0, page_limit=0):
    if type(query) == unicode:
        query = query.encode('utf-8')
    base_url = URL % (urllib.quote_plus(query), apikey, per_page)

    for page_count in itertools.count():
        url = base_url + '&start=%d' % start
        logging.debug('Parsing %d offset' % start)
        resp = api_call(url)

        # No more results
        if not 'resultset_web' in resp:
            return

        for item in resp['resultset_web']:
            yield item

        if 'nextpage' in resp:
            start += per_page
        else:
            logging.debug('End of search results')
            return

        if page_limit and page_count >= page_limit - 1:
            logging.debug('Reached page limit')
            return
