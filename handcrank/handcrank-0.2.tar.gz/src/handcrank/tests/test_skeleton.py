from os.path import join, isdir

from handcrank.tests.testcase import TestCase
from handcrank import parser
from handcrank.runner import Runner


class CreateSkeletonTest(TestCase):
    def test_requires_site_directory(self):
        options = parser.parse_args(['startsite'])
        runner = Runner(options)

        with self.assertRaises(SystemExit) as exc_context:
            runner.begin()
        try:
            self.assertEquals(1, exc_context.exception.code)
        except AttributeError:
            self.assertEquals(1, exc_context.exception)

    def test_creates_site_directory(self):
        working = join(self.fixtures, 'working')

        options = parser.parse_args(['--sitedir', working, 'startsite'])
        runner = Runner(options)

        with self.assertRaises(SystemExit) as exc_context:
            runner.begin()
        try:
            self.assertEquals(0, exc_context.exception.code)
        except AttributeError:
            self.assertEquals(0, exc_context.exception)
        self.assertTrue(isdir(working))
