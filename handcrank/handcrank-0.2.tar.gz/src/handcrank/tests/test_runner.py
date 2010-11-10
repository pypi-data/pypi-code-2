from os.path import join

from handcrank.tests.testcase import TestCase
from handcrank import parser
from handcrank.runner import Runner


class RunnerTest(TestCase):
    def test_will_retrieve_delegate(self):
        options = parser.parse_args(['generate'])

        runner = Runner(options)
        delegate = runner.get_delegate_class('Delegate',
           join(self.fixtures, 'site_normal'))

        self.assertEqual('Delegate', delegate.__name__)
