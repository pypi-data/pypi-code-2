import textwrap
from distutils.core import setup

import email6

setup(name='email',
      version=email6.__version__,
      description="testing release of email6",
      long_description=textwrap.dedent("""\
        This is a standalone version of the version of email package that will
        ship with Python 3.3.  This version can be installed and run under
        Python3.2.  It is intended as a platform for testing the new code, but
        its final release should also be useable to get the features of the new
        package under Python 3.2."""),
      author="EMail SIG",
      author_email="email-sig@python.org",
      url="http://www.python.org/sigs/email-sig",
      keywords='email',
      license="Python Software Foundation",
      packages=['email6', 'email6/mime', 'email6/test_email'],
      package_data={'email6/test_email': ['data/*']},
      classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Communications :: Email",
        ],
      )
