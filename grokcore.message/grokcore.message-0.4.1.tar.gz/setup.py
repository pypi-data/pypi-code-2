import os
from setuptools import setup, find_packages

version = '0.4.1'

readme = open(os.path.join('src', 'grokcore', 'message', 'README.txt')).read()
changes = open("CHANGES.txt").read()

long_description = "%s\n\n%s\n" % (readme, changes)

install_requires = [
    'setuptools',
    'z3c.flashmessage',
    'grokcore.component',
    'zope.component',
    ]

tests_require = [
    'zope.publisher',
    'zope.security',
    'zope.session',
    ]

setup(name='grokcore.message',
      version=version,
      description="Grok messaging machinery",
      long_description=long_description,
      keywords='Grok Messages',
      author='Grok Team',
      author_email='grok-dev@zope.org',
      url='http://pypi.python.org/pypi/grokcore.message',
      license='ZPL 2.1',
      namespace_packages=['grokcore'],
      packages=find_packages('src'),
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require = dict(test=tests_require),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Zope Public License',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: Zope3',
        ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
