"""
svgweb package
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

class SVGWeb(XStatic):
    name = 'svgweb' # short, all lowercase name
    display_name = 'svgweb' # official name, upper/lowercase allowed
    version = '2011.2.3.1' # for simplicity, use same version x.y.z as bundled files
                        # additionally we append .b for our build number, so we
                        # can release new builds with fixes for xstatic stuff.

    base_dir = join(dirname(__file__), 'data')
    # linux package maintainers just can point to their file locations like this:
    # base_dir = '/usr/share/javascript/jquery'

    description = "%s (XStatic packaging standard)" % display_name

    platforms = 'any'
    classifiers = []
    keywords = '%s xstatic' % name

    # this all refers to the XStatic-* package:
    author = 'Thomas Waldmann'
    author_email = 'tw@waldmann-edv.de'
    # XXX shall we have another bunch of entries for the bundled files?
    # like upstream_author/homepage/download/...?
    # note: distutils/register can't handle author and maintainer at once.

    # this refers to the project homepage of the stuff we packaged:
    homepage = 'http://code.google.com/p/svgweb/'

    # this refers to all files:
    license = '(same as %s)' % display_name

    locations = {
    }

