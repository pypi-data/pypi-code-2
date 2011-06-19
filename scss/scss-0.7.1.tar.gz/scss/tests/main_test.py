import unittest

from scss.parser import Stylecheet

SRC = """
@mixin firefox-message($selector) {
  body.firefox #{$selector}:before {
    content: "Hi, Firefox users!"; } }

@include firefox-message(".header");
"""

class TestSCSS( unittest.TestCase ):

    parser = Stylecheet()

    def test_main(self):
        src = self.parser.loads(SRC)
        print src
