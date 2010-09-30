import sys
sys.path.insert(0, '')

from twp.wikklytextrender import render
from tiddlyweb.model.tiddler import Tiddler


def test_unicode_render():
    tiddler = Tiddler('bar')
    tiddler.text = u'[[Foo\u2603Bar]]'
    tiddler.bag = 'zoo'

    html = render(tiddler, {})
    assert 'href="/bags/zoo/tiddlers/Foo%E2%98%83Bar"' in html


