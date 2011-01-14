import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'SQLAlchemy',
    'WebError',
    'MySQL-python',
    'rfc3339',
    'Flup',
    ]

setup(name='JoCommentAtom',
      version='0.1.3',
      description='Atom feed generator for JoComment.',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Jakub Warmuz',
      author_email='jakub.warmuz@gmail.com',
      url='http://pypi.python.org/pypi/JoCommentAtom',
      keywords='joomla php joomlacomment comment atom feed rss web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='jocommentatom',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = jocommentatom:main

      [paste.app_install]
      main = jocommentatom.lib.installer:PyramidInstaller
      """,
      paster_plugins=['pyramid'],
      )
