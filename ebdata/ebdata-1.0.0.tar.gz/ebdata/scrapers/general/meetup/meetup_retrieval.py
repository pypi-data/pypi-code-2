from django.conf import settings
from ebdata.retrieval.scrapers.newsitem_list_detail import NewsItemListDetailScraper
from ebdata.retrieval.scrapers.list_detail import StopScraping, SkipRecord
from django.utils import simplejson

api_key = settings.MEETUP_API_KEY

# docs at http://www.meetup.com/meetup_api/docs/2/open_events/

class MeetupScraper(NewsItemListDetailScraper):

    logname = 'meetup_retrieval'
    has_detail = False
    max_records_per_scrape = 2000

    def __init__(self, options):
        self.api_key = settings.MEETUP_API_KEY
        self.options = options
        self.schema_slugs = [options.schema]
        self.records_seen = 0
        super(MeetupScraper, self).__init__()

    def list_pages(self):
        """generate page strings."""
        # Result of each iteration is a JSON string.
        params = dict(state='NY', city = 'New+York', key=api_key,
                      country='US', zip='10016')
        url = 'https://api.meetup.com/2/open_events?key=%(key)s&state=%(state)s&city=%(city)s&country=%(country)&zip=%(zip)s&page=200' % params
        for thingy in some_pages:
            yield page

    def parse_list(self, page):
        # parse a single detail string page into record dicts
        results = simplejson.loads(page)['results']
        for result in results:
            if self.records_seen > self.max_records_per_scrape:
                raise StopScraping("We've reached %d records" % self.max_records_per_scrape)
            self.records_seen += 1
            yield result

    def clean_list_record(self, record):
        # clean up a record dict
        cleaned = {}
        attributes = {}
        cleaned['_attributes'] = attributes
        return cleaned


    def existing_record(self, record):
        # check if the CLEANED record dict matches a NewsItem
        try:
            item = NewsItem.objects.get(schema=self.schema, x=y)
            return item
        except NewsItem.DoesNotExist:
            return None

    def save(self, old_record, list_record, detail_record):
        attributes = list_record.pop('_attributes')
        self.create_or_update(old_record, attributes, **list_record)


def main(argv=None):
    import sys
    if argv is None:
        argv = sys.argv[1:]
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option(
        "--schema", help="Slug of schema to use. Default is 'meetups'.",
        action='store', default='meetups',
        )

    options, args = parser.parse_args(argv)
    scraper = MeetupScraper(options)
    scraper.update()

if __name__ == '__main__':
    main()
