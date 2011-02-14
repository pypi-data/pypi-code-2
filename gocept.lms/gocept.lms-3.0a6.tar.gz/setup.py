import os.path
from setuptools import setup, find_packages


def read(*names):
    return open(
        os.path.join(os.path.dirname(__file__), *names)).read()


setup(name='gocept.lms',
      version='3.0a6',
      description="gocept Link Monitoring Server",
      long_description=(
          read('src', 'gocept', 'lms', 'README.txt')
          + '\n\n'
          + read('CHANGES.txt')
      ),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: No Input/Output (Daemon)',
          'Framework :: Zope3',
          'Framework :: ZODB',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Zope Public License',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Site Management :: Link Checking',
          'Topic :: System :: Monitoring',
      ],
      keywords="zope lms link checking",
      author="gocept",
      author_email="mail@gocept.com",
      url="http://pypi.python.org/pypi/gocept.lms",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['gocept'],
      install_requires=[
          'decorator',
          'gocept.reference>=0.4dev',
          'gocept.runner',
          'grok',
          'hurry.query',
          'pytz',
          'setuptools',
          'z3c.schema',
          'z3c.testsetup',
          'zc.catalog',
          'zc.queue',
          'zc.relation',
          'zc.sourcefactory',
          'zope.app.wsgi',
          'zope.sendmail',
          'zope.testing',
      ],
      entry_points = dict(
        console_scripts =
          ['runscheduler = gocept.lms.runner:scheduler',
           'runchecker = gocept.lms.runner:checker',
           'runsyncer = gocept.lms.runner:syncer',
           'runnotifier = gocept.lms.runner:notifier'])
     )
