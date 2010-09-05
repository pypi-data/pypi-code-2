
import os, shutil
from os.path import abspath, dirname, basename, join as pathjoin
import re


TEST_ROOT = dirname(abspath(__file__))
TEST_DOCUMENT_ROOT = pathjoin(TEST_ROOT, 'documents')

TEST_DOCUMENTS = dict(
    (d, pathjoin(TEST_DOCUMENT_ROOT, d)) for d in os.listdir(TEST_DOCUMENT_ROOT)
    )

CTRL_CHAR_RX = '\x1b.*?m'
CTRL_CHAR_PATTERN = re.compile(CTRL_CHAR_RX)

def setup_sources(docroot, builder='html'):
    srcdir = docroot + '/source'
    confdir = srcdir
    outdir = docroot + '/build'
    doctreedir = docroot + '/doctrees'
    for dir in [outdir, doctreedir]:
        if os.path.exists(dir):
            shutil.rmtree(dir)
    staticdir = srcdir + '/_static'
    if not os.path.exists(staticdir):
        os.mkdir(staticdir)
    assert not os.path.exists(outdir)
    assert not os.path.exists(doctreedir)
    assert os.path.exists(staticdir)
    return srcdir, confdir, outdir, doctreedir, builder

def logfilter(s):
    for line in CTRL_CHAR_PATTERN.sub('', s).rstrip().splitlines():
        if line:
            print line


