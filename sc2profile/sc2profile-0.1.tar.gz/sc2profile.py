import re
import logging
from urllib2 import unquote
from urlparse import urljoin

from lxml.etree import tostring
from lxml.html import parse as _html_parse, HTMLParser

__author__ = u'Henry Pr\u00EAcheur <henry@precheur.org>'
__version__ = '0.1'
__license__ = 'ISCL'

_logger = logging.getLogger('sc2profile')

def html_parse(url):
    _logger.debug('Fetch: %r', url)
    return _html_parse(url, parser=HTMLParser(encoding='utf8'))

regions = ('us', 'eu', 'kr', 'tw', 'sea', 'ru', 'la')
divisions = ('Master', 'Diamond', 'Platinum', 'Gold', 'Silver', 'Bronze')
races = ('terran', 'protoss', 'zerg', 'random')

_portrait = re.compile(
'''(?xmi)
    background:\s+
    url\([\'"]?
    [^\'"]+/portraits-(?P<portrait_id>[012])-(?P<size>45|75|90)\.jpg
    [\'"]\)
    \s+
    (?P<x>-?\d+)px
    \s+
    (?P<y>-?\d+)px
''')

_url = re.compile(
'''(?xmi)
    ^
    https?://
    (?P<region>\w+)
    \.battle\.net
    /sc2/
    (?P<locale>\w+)
    /profile/
    (?P<bnet_id>\d+)
    /1/
    (?P<name>[^/]+)
    /
    $''')

def parse_bnet_url(url):
    r = _url.match(url)
    if r:
        result = r.groupdict()
        result['bnet_id'] = int(result['bnet_id'])
        result['name'] = unquote(result['name']).decode('utf8')

        return result
    else:
        raise ValueError('Unable to parse url: %r' % url)

class Profile(dict):
    def __init__(self, filename_or_url, region=None, bnet_id=None, name=None):
        self._filename_or_url = filename_or_url
        try:
            self.update(parse_bnet_url(filename_or_url))
            self._valid_url = True
        except Exception as e:
            if region and bnet_id and name:
                self.region = region
                self.bnet_id = bnet_id
                self.name = name
                self._valid_url = False
            else:
                raise TypeError('%r is not a valid URL. '
                                'region, bnet_id, and name required.' %
                                filename_or_url)

    def __repr__(self):
        return '<%s(%r, %r, %r)>' % (self.__class__.__name__,
                                     self.region, self.bnet_id, self.name)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError('%r object has no attribute %r' %
                                 (self.__class__.__name__, name))

    def url(self, path):
        path = path.encode('utf8')
        return urljoin('http://%s.battle.net' % self.region, path)

    def fetch_profile(self):
        root = html_parse(self._filename_or_url).getroot()

        portrait = root.get_element_by_id('portrait')
        span = portrait.find('span')
        r = _portrait.search(span.attrib['style'])

        size = int(r.group('size'))
        self['portrait_id'] = r.group('portrait_id')
        self['x'] = int(r.group('x')) // size
        self['y'] = int(r.group('y')) // size

        a = root.cssselect('#season-snapshot > div.module-footer > a')
        race = a[0].attrib['class'][len('race-'):]
        self['race'] = race

    def fetch_division_urls(self, url=None):
        if not url:
            if self._valid_url:
                url = self._filename_or_url + 'ladder/leagues'
            else:
                raise TypeError('url required')

        root = html_parse(url).getroot()

        a_links = root.cssselect('ul#profile-menu > li > a')[2:]
        return tuple(a.attrib['href'] for a in a_links)

    @staticmethod
    def _parse_ladder_row(cells, player_count):
        try:
            rank = int(cells[1].text[:-2])
            points = int(cells[2 + player_count].text)
            wins = int(cells[3 + player_count].text)
            losses = int(cells[4 + player_count].text)

            if False:
                for p in range(player_count):
                    c = cells[2 + p]
                    a = c.find('a')
                    race = a.attrib['class'][len('race-'):]
                    print race
                    url = a.attrib['href']
                    print 'url', repr(url)

            return dict(rank=int(cells[1].text[:-2]),
                        points=int(cells[2 + player_count].text),
                        wins=int(cells[3 + player_count].text),
                        losses=int(cells[4 + player_count].text))
        except Exception as e:
            _logger.exception("Can't get division information %r", e)

    _division_level = re.compile(r'badge-(?P<level>%s)' %
                                 '|'.join(d.lower() for d in divisions))
    _division_type = re.compile(r'[1-4][a-zA-Z][1-4]')

    def fetch_division(self, url):
        _logger.debug('Fetch division %r' % url)
        root = html_parse(url).getroot()

        result = dict()

        info = root.get_element_by_id('profile-right')

        # Find the level of the division
        d = info.cssselect('div.data-title > div.data-label')
        if d:
            x = self._division_level.search(d[0].attrib['class'])
            if x:
                result['level'] = x.group('level').title()

        # Get the type, & name of the division
        h3 = info.cssselect('div.data-label > h3')[0]
        t = self._division_type.search(h3.text)

        if t and t.group(0)[0] == t.group(0)[2]:
            result['type'] = t.group(0)[0] + 'v' + t.group(0)[0]
        else:
            _logger.error("Can't find division type")
        result['name'] = h3[0].tail.strip()

        p = info.cssselect('tr.data-header > th')
        players = int(p[1].attrib['colspan'])
        _logger.debug('%d players' % players)

        # Games with 1 player are 'random' team games
        if players < 2 and 'type' in result and result['type'] != '1v1':
            result['type'] += ' Random'

        try:
            cells = info.get_element_by_id('current-rank').findall('td')
            result.update(self._parse_ladder_row(cells, players))
        except Exception:
            _logger.exception('Unable to find "current-rank" in page')

        try:
            bp = info.get_element_by_id('bonus-pool')
            result['bonus_pool'] = int(bp.find('span').text)
        except Exception:
            _logger.exception("Can't find bonus pool")

        return result

    def fetch_divisions(self):
        urls = self.fetch_division_urls()

        self['divisions'] = list(self.fetch_division(self.url(u))
                                 for u in urls)

    def fetch_all(self):
        self.fetch_profile()
        self.fetch_divisions()


if __name__ == '__main__':
    from sys import argv
    from pprint import pprint
    logging.basicConfig(level=logging.DEBUG)

    for x in argv[1:]:
        p = Profile(x)
        p.fetch_all()
        pprint(dict(p))
