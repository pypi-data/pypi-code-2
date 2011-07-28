import unittest
import os

from mark3.markdown import markdown


class BasicTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_blank(self):
        self.assertEqual(markdown(''), '')
        self.assertEqual(markdown('\n \n  \n'), '')

    def test_prefixed_blank_lines(self):
        self.assertEqual(strip(markdown(' \n  \nhi')), strip('<p>hi</p>\n\n'))

def strip(s):
    # Get rid of newlines.
    # code blocks are the only place newlines actually matter. But it's causing
    # too much pain to test insignificant whitespace as significant elsewhere.
    return s.replace('\n', '').strip()

def build_test(fp):
    html_fp = fp.split('.')[0]+'.html'
    def test(self):
        if os.path.exists(html_fp):
            self.assertEqual(strip(markdown(open(fp).read())),
                    strip(open(html_fp).read()))
        else:
            print('SKIP')
    return test

for root, dirs, files in os.walk(os.path.join(os.path.dirname(__file__),
        'markdown')):
    for f in files:
        if f.endswith(".text"):
            setattr(BasicTest, 'test_'+f.split('.')[0],
                    build_test(os.path.join(root, f)))

def test_main():
    try:
        from test import support
        support.run_unittest(BasicTest)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
