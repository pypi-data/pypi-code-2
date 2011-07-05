"""
MathJax package
"""

from os.path import join, dirname

try:
    from xstatic.main import XStatic
except ImportError:
    class XStatic(object):
        """
        just a dummy for the time when setup.py is running and
        for the case that xstatic is not already installed.
        """

class MathJax(XStatic):
    name = 'mathjax' # short, all lowercase name
    display_name = 'MathJax' # official name, upper/lowercase allowed
    version = '1.1'     # for simplicity, use same version x.y.z as bundled files
                          # additionally we append .b for our build number, so we
                          # can release new builds with fixes for xstatic stuff.

    base_dir = join(dirname(__file__), 'data')
    # linux package maintainers just can point to their file locations like this:
    # base_dir = '/usr/share/java/twikidraw-moin'

    description = "%s (XStatic packaging standard)" % display_name

    platforms = 'any'
    classifiers = []
    keywords = '%s xstatic' % name

    # this all refers to the XStatic-* package:
    author = 'Reimar Bauer'
    author_email = 'rb.proj@googlemail.com'
    # XXX shall we have another bunch of entries for the bundled files?
    # like upstream_author/homepage/download/...?
    # note: distutils/register can't handle author and maintainer at once.

    # this refers to the project homepage of the stuff we packaged:
    homepage = 'http://www.mathjax.org'

    # this refers to all files:
    license = '(same as %s)' % display_name

    locations = {
        # if value is a string, it is a base location, just append relative
        # path/filename. if value is a dict, do another lookup using the
        # relative path/filename you want.
        # your relative path/filenames should usually be without version
        # information, because either the base dir/url is exactly for this
        # version or the mapping will care for accessing this version.
        ('mathjax', 'http'): 'http://cdn.mathjax.org/mathjax/%s-latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML' % version,
        ('mathjax', 'https'): 'https://d3eoax9i5htok0.cloudfront.net/mathjax/%s-latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML' % version,
    }


