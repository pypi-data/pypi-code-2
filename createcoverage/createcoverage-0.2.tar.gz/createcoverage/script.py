import os
import shutil
import subprocess
import sys
import webbrowser

MUST_CLOSE_FDS = not sys.platform.startswith('win')


def system(command, input=None):
    """commands.getoutput() replacement that also works on windows.

    Code mostly copied from zc.buildout.

    """
    p = subprocess.Popen(command,
                         shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         close_fds=MUST_CLOSE_FDS)
    stdoutdata, stderrdata = p.communicate(input=input)
    result = stdoutdata + stderrdata
    if p.returncode:
        print "Something went wrong when executing"
        print "    ", command
        print "Returncode:"
        print "    ", p.returncode
        print "Output:"
        print result
        sys.exit(1)
    print result


def main():
    """Create coverage reports and open them in the browser."""
    curdir = os.getcwd()
    coveragedir = os.path.join(curdir, 'htmlcov')
    testbinary = os.path.join(curdir, 'bin', 'test')
    if not os.path.exists(testbinary):
        raise RuntimeError("Test command doesn't exist: %s" % testbinary)

    coveragebinary = os.path.join(curdir, 'bin', 'coverage')
    if not os.path.exists(coveragebinary):
        raise RuntimeError(
            "Coverage command doesn't exist: %s" % coveragebinary)

    print "Running tests in coverage mode (can take a long time)"
    system("%s run %s" % (coveragebinary, testbinary))
    print "Creating coverage reports..."
    system("%s html" % coveragebinary)
    webbrowser.open(os.path.join(coveragedir, 'index.html'))
    print "Opened reports in your browser."
