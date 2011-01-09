"""
This setup.py packages `upload.py` script from rietveld project
as `review.py` for PyPI, so that it could be called as::

  python -m review

To update PyPI package, issue::
   python refresh.py
   python setup.py sdist upload
"""

from distutils.core import setup

setup(
    name='review',
    version='r640',
    author='Google Inc. & Co.',
    author_email='codereview-discuss@googlegroups.com',
    url='http://codereview.appspot.com/',

    description='upload script for "Rietveld" code review tool',
    long_description="""
Usage::

    python -m review [options]

Changes::

  r640 - Add perforce support, by Alex McCarthy (2635043)
  r632 - Support for Rietveld instances moved by HTTP 301 (3227041)
  r590 - Look at the old filename only for add with Mercurial (2951041)

  r588 - Support "http://" prefix when detecting localhost usage (2736045)
  r585 - Fix wrong base revision for Python repository (issue #239, 2442042)

  r579 - No depth restriction on 'hg diff' by default (issue #234, 2292041)
  r566 - Remove "default" from help text for --verbose (2048041)
  r561 - Locate subversion config on Windows (1983049)

  r554 - Fix --rev option (git backend) when argument has a colon (issue #211)
  r552 - Fix exception while trying to output an error (3109015)
  r546 - Add application/x-sh to whitelist of uploadable files, by Derek Schuff
  r541 - Fix variable usage when getting/setting keyring password (1900041)
  r538 - Fetch base file from SVN url if local history is missing (issue #208)
  r537 - Optionally use the 'keyring' module to avoid password prompts
  r535 - Improve captcha message for Google Apps accounts (1690047)
  r534 - Convert Unicode values to ASCII (1590044)
  r531 - Add account type flag to upload.py (issue #195)

* Home Page:   http://codereview.appspot.com/
* Development: http://code.google.com/p/rietveld/
* Discussions: http://groups.google.com/group/codereview-discuss/
* PyPI Code:   http://bitbucket.org/techtonik/pypi-rietveld/
""",
    license='Apache 2.0',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],

    py_modules=['review'],
)
