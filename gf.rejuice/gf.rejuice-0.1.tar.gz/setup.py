
__version__ = '0.1'

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'docs/README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(
    name = 'gf.rejuice',
    version = __version__,
    description = '`gf.rejuice` provides additional tools for developers to use `Juicer` '
                  'for the compression of Javascript and CSS resources, '
                  'in the context of python web applications that run via WSGI.',
    long_description = README + '\n\n' + CHANGES,
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
    keywords = 'web middleware wsgi css js juicer merging minifying development',
    author = "Balazs Ree",
    author_email = "ree@greenfinity.hu",
    url = "http://www.repoze.org",
    license = "GPL",
    packages = find_packages(),
    include_package_data = True,
    namespace_packages = ['gf'],
    zip_safe = False,
    install_requires=[
          'setuptools',
          'lxml >= 2.1.1',
          'WebOb',
        ],
    test_suite = "gf.rejuice",
    tests_require=[
            'BeautifulSoup',
            'setuptools',
            'lxml >= 2.1.1',
            'WebOb',
            ],

    entry_points = """\
      [paste.filter_app_factory]
      develjuice = gf.rejuice.develjuice:make_middleware
      [console_scripts]
      rejuice = gf.rejuice.rejuice_script:main
      """
      )

