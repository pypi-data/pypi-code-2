from random import choice
from lxml.html import fromstring

from tools.net.browser import Browser

COUNTRIES = ['au', 'as', 'bg', 'ca', 'cyen', 'cygk', 'dk', 'fi', 'fr', 'gr', 'hu', 'is', 'it', 'sl', 'sp', 'sw', 'sz', 'uk', 'us']

class NameGenerator(object):
    def __init__(self):
        self.browser = Browser(log_file='log.html')

    def build_url(self):
        # random gender, US name set, random country
        return 'http://www.fakenamegenerator.com/gen-random-us-%s.php' % choice(COUNTRIES)

    def generate(self):
        response = self.browser.request(self.build_url())
        return self.parse_response(response)

    def parse_response(self, data):
        tree = fromstring(data)
        return {
            'given_name': tree.xpath('//span[@class="given-name"]')[0].text_content(),
            'family_name': tree.xpath('//span[@class="family-name"]')[0].text_content(),
        }
