import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

required = ['pyramid',
            'pyramid_jinja2',
            'Werkzeug',
            'SQLAlchemy',
            'repoze.tm2',
            'zope.sqlalchemy']

setup(name='Spitter',
      version='0.3',
      description='Spitter is a Twitter-like clone written using the pyramid web framework',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='Rocky Burt',
      author_email='rocky@serverzen.com',
      url='http://dist.serverzen.com/pypi/d/spitter/',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=required,
      tests_require=required,
      test_suite="spitter",
      entry_points = """\
      [paste.app_factory]
      app = spitter.main:make_app
      """
      )
