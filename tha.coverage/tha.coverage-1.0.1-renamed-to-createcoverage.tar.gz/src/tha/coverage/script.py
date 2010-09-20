import os
import subprocess
import sys
import shutil
import webbrowser

from z3c.coverage import coveragereport


def main():
    """Create coverage reports

    Assumption: we're called inside a buildout directory.
    """
    curdir = os.getcwd()
    coveragedir = os.path.join(curdir, 'coverage')
    testbinary = os.path.join(curdir, 'bin', 'test')
    if not os.path.exists(testbinary):
        raise RuntimeError("Test command doesn't exist: %s" % testbinary)
    
    if len(sys.argv) > 1:
        # Output dir, so buildbot mode.  Create reports in the output dir and
        # that's it.
        outputdir = sys.argv[1]
        buildbot_mode = True
        print "Buildbot mode, output will be placed in %s" % outputdir
    else:
        # No output dir, so developer machine mode.  Create reports and open
        # them in the browser.
        outputdir = os.path.join(coveragedir, 'reports')
        buildbot_mode = False

    if os.path.exists(coveragedir):
        print "Removing old coverage dir"
        shutil.rmtree(coveragedir)

    print "Running tests in coverage mode (can take a long time)"
    subprocess.call([testbinary, '--coverage=%s' % coveragedir])

    if not os.path.exists(outputdir):
        os.mkdir(outputdir)
    print "Creating coverage reports..."
    coveragereport.main((coveragedir, outputdir))
    print "Done."

    if not buildbot_mode:
        webbrowser.open(os.path.join(outputdir, 'all.html'))
