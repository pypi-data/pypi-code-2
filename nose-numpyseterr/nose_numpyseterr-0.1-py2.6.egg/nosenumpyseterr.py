"""
This nose plugin set how floating-point errors are handled by numpy

Ever wondered why you get 'Warning: divide by zero encountered in divide'
when running nosetest with numpy? Just run nosetest with ``--npe-all=raise``
option and you will see why.

See the document of `numpy.seterr` for the other valid arguments.
"""

from nose.plugins.base import Plugin


class NumpySeterr(Plugin):
    """
    Set `numpy.seterr` before running any test
    """
    argnames = ['all', 'divide', 'over', 'under', 'invalid']

    def options(self, parser, env):
        for arg in self.argnames:
            parser.add_option(
                "--npe-%s" % arg, type=str, default=None, metavar="HANDLE",
                help="handler for `numpy.seterr(%s=HANDLE)`" % arg)

    def configure(self, options, conf):
        keyval = ((a, getattr(options, 'npe_%s' % a)) for a in self.argnames)
        kwds = dict(filter(lambda x: x[1] is not None, keyval))
        if kwds:
            # import numpy here so that you dont have import error even if you
            # don't have numpy, provided that you didn't specify --npe-* option
            import numpy
            numpy.seterr(**kwds)
