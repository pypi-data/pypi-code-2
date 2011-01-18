# vim:fileencoding=utf-8
import urllib
import urllib2
import json
import types
from BeautifulSoup import BeautifulSoup, NavigableString, Declaration, Comment
import re
from jcconv import hira2kata

__version__ = 0.3

API_URL = 'http://ja.wikipedia.org/w/api.php'

# 偽装する User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; ja; rv:1.9.1) Gecko/20090624 Firefox/3.5 (.NET CLR 3.5.30729)'

__all__ = (
        'USER_AGENT',
        'WikiArticle',
        'open_article',
        )


class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated.
    """
    def __init__(self, func):
        self.func = func
        self.cache = {}
    def __call__(self, *args):
        try:
            return self.cache[args]
        except KeyError:
            self.cache[args] = value = self.func(*args)
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)
    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__


class WikiArticle(object):

    def __init__(self, soup):
        self.soup = soup
        self.disambiguation = soup.find('a', title=u'Category:曖昧さ回避') is not None

    @property
    @memoized
    def title(self):
        """
        この Wikipedia エントリーのタイトルを返します。
        """
        return self.soup.find('h1', id='firstHeading').string

    @property
    @memoized
    def name(self):
        """
        この Wikipedia エントリー名。
        タイトルと異なり、例えば同姓同名がいる人物でも括弧書きは含ませないことが一般的。
        """
        p = self._get_first_paragraph()
        return p.find('b').string
        
    @property
    @memoized
    def ruby(self):
        """
        この Wikipedia エントリー名のふりがな。
        人名などで姓と名の間にスペースが空いている場合、そのスペースは除去されます。

        ふりがなを解析できなかった場合は None。
        """
        p = self._get_first_paragraph()
        text = p.find('b').nextSibling
        m = re.search(ur'[\(（](.+?)[、）\)].*', text)
        if m:
            furigana = m.group(1)
            return hira2kata(furigana)
        return None

    @property
    @memoized
    def summary(self):
        """
        概要
        """
        p = self._get_first_paragraph()
        return self._append_summary(p)
        
    def _append_summary(self, p, text=''):
        text += self._get_text(p)
        p = p.nextSibling
        while isinstance(p, NavigableString):
            p = p.nextSibling
        if p.name == u'p':
            return self._append_summary(p, text + "\n")
        return text

    def _get_first_paragraph(self):
        div = self.soup.find('div', id='bodyContent')
        if not div:
            div = self.soup
        p = div.find('p', recursive=False)
        return p

    @property
    @memoized
    def url(self):
        """
        この Wikipedia エントリーの URL
        """
        return 'http://ja.wikipedia.org/wiki/%s' % urllib.quote(self.title.encode('utf-8'))

    @property
    @memoized
    def aliases(self):
        """
        この Wikipedia エントリーの別名、愛称のリスト。
        別名や愛称の定義がない場合は空のリスト。
        """
        key = u'別名'
        results = []
        for key, value in self.info.items():
            if key in (u'別名', u'愛称'):
                aliases = re.split(ur'[\n、]+', value)
                results += aliases
        return results

    @property
    @memoized
    def info(self):
        """
        基本情報の各項目と値の dict。
        基本情報が設定されていない場合は空の dict。
        """
        results = {}
        infobox = self.soup.find('table', 'infobox')
        if infobox:
            rows = infobox.findAll('tr')
            for r in rows:
                columns = r.findAll(['th', 'td'])
                if len(columns) == 2:
                    results[self._get_text(columns[0])] = self._get_text(columns[1])
        return results
 
    def _get_text(self, soup):
        """
        BeautifulSoup のタグ内のテキストをすべて結合して返します。

        http://python.g.hatena.ne.jp/y_yanbe/20081025/1224910392
        """
        text = ''.join(self._getNavigableStrings(soup))           
        return text

    def _getNavigableStrings(self, soup):
        if isinstance(soup, NavigableString):
            if type(soup) not in (Comment, Declaration) and soup.strip():
                yield soup
        elif soup.name not in ('script', 'style'):
            for c in soup.contents:
                for g in self._getNavigableStrings(c):
                    yield g


def get_article(url):
    """
    指定された Wikipedia ページの URL または単語から、Wikipedia ページの
    WikiArticle オブジェクトを返します。

    @param url: Wikipedia ページの URL または単語
    @type url: str, unicode
    @raise HTTPError: 指定された URL や単語の Wikipedia ページが存在しない、読み込めない場合
    @raise URLError: Wikipedia に接続できなかった場合
    """
    if not url.startswith('http://ja.wikipedia.org/wiki/'):
        url = 'http://ja.wikipedia.org/wiki/%s' % urllib.quote(isinstance(url, types.UnicodeType) and url.encode('utf-8') or url)
    req = urllib2.Request(url)
    req.add_header('User-Agent', USER_AGENT) # UserAgent を偽装しないとアクセスできない
    soup = BeautifulSoup(urllib2.urlopen(req).read())
    return WikiArticle(soup)


def _get_artile_using_api(page):
    """
    XXX: 実装途中。
    """
    params = {
        'action': 'parse',
        'page': page,
        'prop': 'text|categories',
        'redirects': '',
        'format': 'json',
        }
    params = urllib.urlencode(params)
    url = API_URL + '?' + params
    res = urllib.urlopen(url).read()
    results = json.loads(res)
    soup = BeautifulSoup(results['parse']['text']['*'])
    return WikiArticle(soup)

