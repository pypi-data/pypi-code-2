import nose
import helpers
from css_crawler.lib.css.capture import CSSCapture


def test_no_stylesheet():
    """
    Capture a page with no stylesheet
    """
    url = "NO_URL"
    capture = CSSCapture(fetcher=helpers.no_stylesheet_fetcher)
    res = capture.capture(url)
    nose.tools.assert_equal(res, [])


def test_no_stylesheet():
    """
    Capture a page with a test stylesheet
    """
    url = "NO_URL"
    capture = CSSCapture(fetcher=helpers.base_stylesheet_fetcher)
    url, res = capture.capture(url)
    nose.tools.assert_equal(len(res), 1)
