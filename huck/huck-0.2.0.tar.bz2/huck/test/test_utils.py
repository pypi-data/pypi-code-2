import unittest
import huck.utils

class UtilsTestCase(unittest.TestCase):

    def test_objectify(self):
        data = huck.utils.objectify({
            'number': 1,
            'alpha': 'abc',
            'one': {'two': {'three': 'four'}},
        })
        self.assertEqual(data.number, 1)
        self.assertEqual(data.alpha, 'abc')
        self.assertEqual(data.one.two.three, 'four')

    def test_json(self):
        data = huck.utils.json.decode('{"hello":1,"world":2.5}')
        self.assertEqual(data['hello'], 1)
        self.assertEqual(data['world'], 2.5)
        data = huck.utils.json.encode(data)
        self.assertTrue('"hello"' in data)

    def test_linkify(self):
        data = [
            # (input, linkify_kwargs, expected_output)
            (
                "hello http://world.com/!",
                {},
                u'hello <a href="http://world.com/">http://world.com/</a>!',
            ),
            (
                "hello http://world.com/with?param=true&stuff=yes",
                {},
                u'hello <a href="http://world.com/with?param=true&amp;stuff=yes">http://world.com/with?param=true&amp;stuff=yes</a>',
            ),
            # an opened paren followed by many chars killed Gruber's regex
            (
                "http://url.com/w(aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                {},
                u'<a href="http://url.com/w">http://url.com/w</a>(aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
            ),
            # as did too many dots at the end
            (
                "http://url.com/withmany.......................................",
                {},
                u'<a href="http://url.com/withmany">http://url.com/withmany</a>.......................................',
            ),
            (
                "http://url.com/withmany((((((((((((((((((((((((((((((((((a)",
                {},
                u'<a href="http://url.com/withmany">http://url.com/withmany</a>((((((((((((((((((((((((((((((((((a)',
            ),
            # some examples from http://daringfireball.net/2009/11/liberal_regex_for_matching_urls
            # plus a fex extras (such as multiple parentheses).
            (
                "http://foo.com/blah_blah",
                {},
                u'<a href="http://foo.com/blah_blah">http://foo.com/blah_blah</a>',
            ),
            (
                "http://foo.com/blah_blah/",
                {},
                u'<a href="http://foo.com/blah_blah/">http://foo.com/blah_blah/</a>',
            ),
            (
                "(Something like http://foo.com/blah_blah)",
                {},
                u'(Something like <a href="http://foo.com/blah_blah">http://foo.com/blah_blah</a>)',
            ),
            (
                "http://foo.com/blah_blah_(wikipedia)",
                {},
                u'<a href="http://foo.com/blah_blah_(wikipedia)">http://foo.com/blah_blah_(wikipedia)</a>',
            ),
            (
                "http://foo.com/blah_(blah)_(wikipedia)_blah",
                {},
                u'<a href="http://foo.com/blah_(blah)_(wikipedia)_blah">http://foo.com/blah_(blah)_(wikipedia)_blah</a>',
            ),
            (
                "(Something like http://foo.com/blah_blah_(wikipedia))",
                {},
                u'(Something like <a href="http://foo.com/blah_blah_(wikipedia)">http://foo.com/blah_blah_(wikipedia)</a>)',
            ),
            (
                "http://foo.com/blah_blah.",
                {},
                u'<a href="http://foo.com/blah_blah">http://foo.com/blah_blah</a>.',
            ),
            (
                "http://foo.com/blah_blah/.",
                {},
                u'<a href="http://foo.com/blah_blah/">http://foo.com/blah_blah/</a>.',
            ),
            (
                "<http://foo.com/blah_blah>",
                {},
                u'&lt;<a href="http://foo.com/blah_blah">http://foo.com/blah_blah</a>&gt;',
            ),
            (
                "<http://foo.com/blah_blah/>",
                {},
                u'&lt;<a href="http://foo.com/blah_blah/">http://foo.com/blah_blah/</a>&gt;',
            ),
            (
                "http://foo.com/blah_blah,",
                {},
                u'<a href="http://foo.com/blah_blah">http://foo.com/blah_blah</a>,',
            ),
            (
                "http://www.example.com/wpstyle/?p=364.",
                {},
                u'<a href="http://www.example.com/wpstyle/?p=364">http://www.example.com/wpstyle/?p=364</a>.',
            ),
            (
                "rdar://1234",
                {"permitted_protocols": ["http", "rdar"]},
                u'<a href="rdar://1234">rdar://1234</a>',
            ),
            (
                "rdar:/1234",
                {"permitted_protocols": ["rdar"]},
                u'<a href="rdar:/1234">rdar:/1234</a>',
            ),
            (
                "http://userid:password@example.com:8080",
                {},
                u'<a href="http://userid:password@example.com:8080">http://userid:password@example.com:8080</a>',
            ),
            (
                "http://userid@example.com",
                {},
                u'<a href="http://userid@example.com">http://userid@example.com</a>',
            ),
            (
                "http://userid@example.com:8080",
                {},
                u'<a href="http://userid@example.com:8080">http://userid@example.com:8080</a>',
            ),
            (
                "http://userid:password@example.com",
                {},
                u'<a href="http://userid:password@example.com">http://userid:password@example.com</a>',
            ),
            (
                "message://%3c330e7f8409726r6a4ba78dkf1fd71420c1bf6ff@mail.gmail.com%3e",
                {"permitted_protocols": ["http", "message"]},
                u'<a href="message://%3c330e7f8409726r6a4ba78dkf1fd71420c1bf6ff@mail.gmail.com%3e">message://%3c330e7f8409726r6a4ba78dkf1fd71420c1bf6ff@mail.gmail.com%3e</a>',
            ),
            (
                u"http://\u27a1.ws/\u4a39",
                {},
                u'<a href="http://\u27a1.ws/\u4a39">http://\u27a1.ws/\u4a39</a>',
            ),
            (
                "<tag>http://example.com</tag>",
                {},
                u'&lt;tag&gt;<a href="http://example.com">http://example.com</a>&lt;/tag&gt;',
            ),
            (
                "Just a www.example.com link.",
                {},
                u'Just a <a href="http://www.example.com">www.example.com</a> link.',
            ),
            (
                "Just a www.example.com link.",
                {"require_protocol": True},
                u'Just a www.example.com link.',
            ),
            (
                "A http://reallylong.com/link/that/exceedsthelenglimit.html",
                {"require_protocol": True, "shorten": True},
                u'A <a href="http://reallylong.com/link/that/exceedsthelenglimit.html" title="http://reallylong.com/link/that/exceedsthelenglimit.html">http://reallylong.com/link...</a>',
            ),
            (
                "A http://reallylongdomainnamethatwillbetoolong.com/hi!",
                 {"shorten": True},
                 u'A <a href="http://reallylongdomainnamethatwillbetoolong.com/hi" title="http://reallylongdomainnamethatwillbetoolong.com/hi">http://reallylongdomainnametha...</a>!',
            ),
            (
                "A file:///passwords.txt and http://web.com link",
                {},
                u'A file:///passwords.txt and <a href="http://web.com">http://web.com</a> link',
            ),
            (
                "A file:///passwords.txt and http://web.com link",
                {"permitted_protocols": ["file"]},
                u'A <a href="file:///passwords.txt">file:///passwords.txt</a> and http://web.com link',
            ),
            (
                "www.external-link.com",
                {"extra_params": 'rel="nofollow" class="external"'},
                u'<a href="http://www.external-link.com" rel="nofollow" class="external">www.external-link.com</a>',
            ),
        ]
        for text, kwargs, html in data:
            linked = huck.utils.linkify(text, **kwargs)
            self.assertEqual(linked, html)

    def test_plus_url(self):
        self.assertEqual(huck.utils.plus_url.escape('hello world'), 'hello+world')
        self.assertEqual(huck.utils.plus_url.unescape('hello+world'), 'hello world')

    def test_query(self):
        data = {'a': 'hello world', 'b': 2.5}
        data = huck.utils.query.encode(data)
        self.assertTrue('a=hello+world' in data)
        self.assertTrue('b=2.5' in data)
        data = huck.utils.query.decode(data)
        self.assertEqual(data['a'][0], 'hello world')
        self.assertEqual(data['b'][0], '2.5')

    def test_squeeze(self):
        self.assertEqual(huck.utils.squeeze('\thi jane,  nice\n\nday outside\n\n\n'), 'hi jane, nice day outside')

    def test_url(self):
        data = huck.utils.url.escape(' hello world ')
        self.assertEqual(data, '%20hello%20world%20')
        data = huck.utils.url.unescape(data)
        self.assertEqual(data, ' hello world ')

    def test_xhtml(self):
        unescaped_text = '<smile>I like "smiley" faces</smile>'
        escaped_text = '&lt;smile&gt;I like &quot;smiley&quot; faces&lt;/smile&gt;'
        self.assertEqual(huck.utils.xhtml.escape(unescaped_text), escaped_text)
        self.assertEqual(huck.utils.xhtml.unescape(escaped_text), unescaped_text)
