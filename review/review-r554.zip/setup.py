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
    version='r554',
    author='Google Inc. & Co.',
    url='http://codereview.appspot.com/',

    description='rietveld code review upload script',
    long_description="""
Usage::

    python -m review [options]

Changes::

  r537 - Optionally use the 'keyring' module to avoid password prompts
  r535 - Improve captcha message for Google Apps accounts (Issue 1690047)
  r534 - Convert Unicode values to ASCII (issue 1590044)
  r531 - Add account type flag to upload.py (issue195)

* Home Page:   http://codereview.appspot.com/
* Development: http://code.google.com/p/rietveld/
* Discussions: http://groups.google.com/group/codereview-discuss/
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
