from datetime import datetime

HAS_CPROFILE = True
try:
    import cProfile
except ImportError:
    HAS_CPROFILE = False

import logging
import os

import tempfile
from nose.plugins import Plugin

log = logging.getLogger('nose.plugins.talisker')


class Talisker(Plugin):
    """
    Outputs a profile for each test into a profile directory
    using Python's standard profile modules.
    """
    name = 'talisker'
    enabled = True

    @classmethod
    def available(cls):
        return cProfile is not None

    def options(self, parser, env):
        Plugin.options(self, parser, env)
        parser.add_option('--prof-path', action='store', dest='prof_path',
                          help="The directory to write profile files too.")

    def configure(self, options, conf):
        if not HAS_CPROFILE:
            self.enabled = False
            return

        path = options.prof_path
        if not path:
            self.prof_path = tempfile.mkdtemp()
            print "No directory specified, creating a temporary one."
            print self.prof_path
        else:
            assert os.path.exists(path)
            assert os.path.isdir(path)
            self.prof_path = path

    def prepareTestCase(self, test):
        def run_and_profile(result, test=test):
            prof = cProfile.Profile()
            start = datetime.now()
            prof.runcall(test.test, result)
            elap = datetime.now() - start
            elapms = elap.seconds * 1000.0 + elap.microseconds / 1000.0
            dest = '%s.%s.%s.%06dms.%s.prof' % (test.test.__class__.__module__,
                                             test.test.__class__.__name__,
                                             test.test._testMethodName,
                                             elapms,
                                             datetime.now().isoformat())
            dest = os.path.join(self.prof_path, dest)
            prof.dump_stats(dest)
        return run_and_profile
