import unittest
import huck.template
import assets

class TemplateTestCase(unittest.TestCase):

    def encode(self, template, **kwargs):
        t = huck.template.Template(template)
        return t.generate(**kwargs)

    def test_block(self):
        self.assertEqual(
            self.encode('{% block test %}' + assets.UNICODE_TEXT + '{% end %}'),
            assets.UNICODE_TEXT,
        )

    def test_default_namespace(self):
        self.assertEqual(
            self.encode('{{ json.encode(value) }}', value={'one': 'two'}),
            '{"one": "two"}',
        )
        self.assertEqual(
            self.encode('{{ query.encode(value) }}', value={'a': assets.UNICODE_TEXT}),
            'a=%s' % assets.URL_ESCAPED_UNICODE_TEXT,
        )
        self.assertEqual(
            self.encode('{{ escape(value) }}', value='>&<'),
            '&gt;&amp;&lt;',
        )
        self.assertEqual(
            self.encode('{{ plus_url.escape(value) }}', value='> <'),
            '%3E+%3C',
        )
        self.assertEqual(
            self.encode('{{ url.escape(value) }}', value='> <'),
            '%3E%20%3C',
        )

    def test_if(self):
        template = '{% if value == 1 or value == 2 %}just{% elif value == 3 %}a{% else %}' + assets.UNICODE_TEXT + '{% end %}'
        self.assertEqual(
            self.encode(template, value=1),
            'just',
        )
        self.assertEqual(
            self.encode(template, value=2),
            'just',
        )
        self.assertEqual(
            self.encode(template, value=3),
            'a',
        )
        self.assertEqual(
            self.encode(template, value=4),
            assets.UNICODE_TEXT,
        )

    def test_for(self):
        template = '{% for value in value_list %}<p>{{ value }}</p>{% end %}'
        self.assertEqual(
            '<p>%s</p><p>%s</p>' % (
                assets.UTF8_UNICODE_TEXT,
                assets.UTF8_UNICODE_TEXT,
            ),
            self.encode(
                template,
                value_list=[
                    assets.UNICODE_TEXT,
                    assets.UNICODE_TEXT,
                ],
            ),
        )

    def test_set(self):
        self.assertEqual(
            self.encode('{% set value="test" %}{{ value }}'),
            'test',
        )

    def test_try(self):
        template = '{% try %}{% if value() %}ok{% end %}{% except %}except{% end %}'
        self.assertEqual(
            self.encode(template, value=lambda: True),
            'ok',
        )
        self.assertEqual(
            self.encode(template, value=lambda: x),
            'except',
        )
        self.assertEqual(
            self.encode(
                '{% try %}{{ value }}{% finally %}finally{% end %}',
                value='ok',
            ),
            'okfinally',
        )

    def test_variable(self):
        self.assertEqual(
            self.encode(
                '<h1>{{ value }}</h1>',
                value=assets.UNICODE_TEXT,
            ),
            '<h1>%s</h1>' % assets.UTF8_UNICODE_TEXT,
        )

if __name__ == '__main__':
    unittest.main()
