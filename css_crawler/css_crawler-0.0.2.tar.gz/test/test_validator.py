import nose
import helpers
from css_crawler.lib.validator import UrlValidator


def test_port():
    """
    Capture a page with no stylesheet
    """
    url = "http://localhost:8080/path/"
    validator = UrlValidator(url)

    nose.tools.assert_equal(validator.is_url().value, url)


def test_no_port():
    """
    Capture a page with no stylesheet
    """
    url = "http://localhost/path/"
    validator = UrlValidator(url)

    nose.tools.assert_equal(validator.is_url().value, url)
