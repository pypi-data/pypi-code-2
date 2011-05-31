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
    version='r749',
    author='Google Inc. & Co.',
    author_email='codereview-discuss@googlegroups.com',
    url='http://codereview.appspot.com/',

    description='upload script for "Rietveld" code review tool',
    long_description="""
Usage::

    python -m review [options]

Changes::

  | r749_ - Fix Ruby and PHP types upload, by Saket Kumar Choudhary (issue #307)
  | r745_ - Better handling of login errors, patch by proppy@goog (#289, 4547067)
  | r730_ - Accept 'cvs diff' return1 either 0 or 1, by Matthew Dempsky (4435076)
  | r703_ - Make RealMain() suitable for API calls (4439056)
  | r700_ - -r N:M failure on new directories, by Arkadi Shishlov (#187, 4368045)
  | r687_ - Fix upload.py typos, by leeight (#286, 4277081)
  | r680_ - Add CVS backend, by Matthew Dempsky 4280044)
  | r663_ - MIMETYPE changes for svn, by Chad Killingsworth (4170042)
  | r660_ - Fix JSON files mimetypes to be text, by levin1 (4133046)
  | r654_ - Preserve username in Base URL until server upload (#266, 4071042)

  | r640_ - Add perforce support, by Alex McCarthy (2635043)
  | r632_ - Support for Rietveld instances moved by HTTP 301 (3227041)
  | r590_ - Look at the old filename only for add with Mercurial (2951041)

  | r588_ - Support "http://" prefix when detecting localhost usage (2736045)
  | r585_ - Fix wrong base revision for Python repository (issue #239, 2442042)

  | r579_ - No depth restriction on 'hg diff' by default (issue #234, 2292041)
  | r566_ - Remove "default" from help text for --verbose (2048041)
  | r561_ - Locate subversion config on Windows (1983049)

  | r554_ - Fix --rev option (git backend) when argument has a colon (issue #211)
  | r552_ - Fix exception while trying to output an error (3109015)
  | r546_ - Add application/x-sh to whitelist of uploadable files, by Derek Schuff
  | r541_ - Fix variable usage when getting/setting keyring password (1900041)
  | r538_ - Fetch base file from SVN url if local history is missing (issue #208)
  | r537_ - Optionally use the 'keyring' module to avoid password prompts
  | r535_ - Improve captcha message for Google Apps accounts (1690047)
  | r534_ - Convert Unicode values to ASCII (1590044)
  | r531_ - Add account type flag to upload.py (issue #195)

.. _r749: http://code.google.com/p/rietveld/source/detail?r=749
.. _r745: http://code.google.com/p/rietveld/source/detail?r=745
.. _r730: http://code.google.com/p/rietveld/source/detail?r=730
.. _r703: http://code.google.com/p/rietveld/source/detail?r=703
.. _r700: http://code.google.com/p/rietveld/source/detail?r=700
.. _r687: http://code.google.com/p/rietveld/source/detail?r=687
.. _r680: http://code.google.com/p/rietveld/source/detail?r=680
.. _r663: http://code.google.com/p/rietveld/source/detail?r=663
.. _r660: http://code.google.com/p/rietveld/source/detail?r=660
.. _r654: http://code.google.com/p/rietveld/source/detail?r=654
.. _r640: http://code.google.com/p/rietveld/source/detail?r=640
.. _r632: http://code.google.com/p/rietveld/source/detail?r=632
.. _r590: http://code.google.com/p/rietveld/source/detail?r=590
.. _r588: http://code.google.com/p/rietveld/source/detail?r=588
.. _r585: http://code.google.com/p/rietveld/source/detail?r=585
.. _r579: http://code.google.com/p/rietveld/source/detail?r=579
.. _r566: http://code.google.com/p/rietveld/source/detail?r=566
.. _r561: http://code.google.com/p/rietveld/source/detail?r=561
.. _r554: http://code.google.com/p/rietveld/source/detail?r=554
.. _r552: http://code.google.com/p/rietveld/source/detail?r=552
.. _r546: http://code.google.com/p/rietveld/source/detail?r=546
.. _r541: http://code.google.com/p/rietveld/source/detail?r=541
.. _r538: http://code.google.com/p/rietveld/source/detail?r=538
.. _r537: http://code.google.com/p/rietveld/source/detail?r=537
.. _r535: http://code.google.com/p/rietveld/source/detail?r=535
.. _r534: http://code.google.com/p/rietveld/source/detail?r=534
.. _r531: http://code.google.com/p/rietveld/source/detail?r=531

* Home Page:   http://codereview.appspot.com/
* Development: http://code.google.com/p/rietveld/
* Discussions: http://groups.google.com/group/codereview-discuss/
* PyPI Code:   http://bitbucket.org/techtonik/python-review/
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
