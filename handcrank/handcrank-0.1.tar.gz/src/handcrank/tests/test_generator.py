from os.path import join

from nose.plugins.attrib import attr

from handcrank.tests.testcase import TestCase
from handcrank import generator
from handcrank import parser
from handcrank.runner import Runner
from handcrank.roles import escape


class BasicGeneratorTest(TestCase):
    def setUp(self):
        super(BasicGeneratorTest, self).setUp()

        self.site_normal = join(self.fixtures, 'site_normal')

    def test_checks_for_arguments(self):
        with self.assertRaises(generator.GeneratorError):
            gen = generator.OnePageGenerator()

        with self.assertRaises(generator.GeneratorError):
            gen = generator.OnePageGenerator(from_dir='.', out_dir='.')

        with self.assertRaises(generator.GeneratorError):
            gen = generator.OnePageGenerator(out_dir='.', tmp_dir='.')

        with self.assertRaises(generator.GeneratorError):
            gen = generator.OnePageGenerator(from_dir='.', tmp_dir='.')

        gen = generator.OnePageGenerator(from_dir='.', tmp_dir='.', out_dir='.')

    def _generate_site_normal(self, ):
        options = parser.parse_args(['--sitedir', self.site_normal, 'generate'])

        runner = Runner(options)
        runner.begin()

    def test_will_create_output_directory(self):
        options = parser.parse_args(['--sitedir', self.site_normal, 'generate'])

        runner = Runner(options)
        runner.begin()

        index = open(join(self.working, 'index.html')).read()

        self.assertIn('Monty Python', index)
        self.assertIn('The quest', index)

    def test_will_render_code_blocks(self):
        options = parser.parse_args(['--sitedir', self.site_normal, 'generate'])

        runner = Runner(options)
        runner.begin()

        index = open(join(self.working, 'index.html')).read()

        self.assertIn('<div class="highlight"><pre><span class="kn">from', index)

    def test_delegate_items_place_first(self):
        delegate = generator.DelegateBase()

        to_test = {'a': 1, 'b': 2, 'c': 3}

        od = delegate.items_place_first(to_test.items(), 'c')

        first = iter(od).next()

        self.assertEquals(('c', 3), first)

    def test_delegate_items_place_first_missing_key(self):
        delegate = generator.DelegateBase()

        to_test = {'a': 1, 'b': 2, 'c': 3}

        with self.assertRaises(generator.GeneratorError) as context:
            od = delegate.items_place_first(to_test.items(), 'd')

            self.assertEqual(str(context.exception),
                'Item d not found, available are: a, b, c')

    def test_delegate_items_sort_alpha(self):
        delegate = generator.DelegateBase()

        to_test = {'moommoo': 1, 'babba': 2, 'abba': 3, 'zeta': 4}

        od = delegate.items_sort_alpha(to_test.items())

        self.assertListEqual(
            [('abba', 3), ('babba', 2), ('moommoo', 1), ('zeta', 4)],
            od)

    def test_delegate_renders_expected(self):
        options = parser.parse_args(['--sitedir', self.site_normal, 'generate'])

        runner = Runner(options)
        runner.begin()

        index = open(join(self.working, 'index.html')).read()

        self.assertIn('Provide extra context', index)

    def test_will_create_doc_link(self):
        options = parser.parse_args(['--sitedir', self.site_normal, 'generate'])

        runner = Runner(options)
        runner.begin()

        index = open(join(self.working, 'index.html')).read()

        self.assertIn(
            '<a href="the_quest.rst" rel="doc-link">you can read that here</a>',
            index)

    def test_html_entity_escape(self):
        self.assertEqual('&amp;&lt;&gt;&quot;&#39;', escape('&<>"\''))
