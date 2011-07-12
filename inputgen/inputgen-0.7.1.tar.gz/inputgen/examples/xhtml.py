"""
An example involving the construction of a valid XHTML document.
This example requires installation of the lxml library:
http://codespeak.net/lxml/
"""

import os

from lxml import etree

import inputgen


parent_dir = os.path.dirname(__file__)
dtd = etree.DTD(open(os.path.join(parent_dir, 'xhtml1-strict.dtd')))


template = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title></title>
  </head>
  <body>
    %s
  </body>
</html>
"""


class Document(object):

    def output(self):
        content = ''.join(getattr(self, 'pos%s' % i) for i in xrange(self.size))
        return template % content

    def repOK(self):
        """Validate using lxml."""
        output = self.output()
        try:
            root = etree.XML(output)
        except etree.XMLSyntaxError:
            return False
        return dtd.validate(root)



class XHTMLExample(inputgen.TestCase):

    @staticmethod
    def repOK(factory):
        return factory.doc.repOK()

    @staticmethod
    def fin(size=5):
        f = inputgen.Factory(enable_iso_breaking=False)
        doc = f.create(Document)
        f.set('doc', doc)

        tags = ['<p>', '</p>', '<b>', '</b>']
        content = ['text1', 'text2', 'text3']

        doc.set('size', [size])
        for i in xrange(size):
            doc.set('pos%s' % i, tags + content)
        return f

    def run_method(self, factory):
        pass


if __name__ == "__main__":
    import unittest
    unittest.main()
