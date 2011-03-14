import os
from setuptools import setup, find_packages

version = '1.0.0'

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

readme = read_file('README.txt')
sequence_doc = read_file(os.path.join('src', 'cykooz', 'sequence', 'sequence.txt'))
changes = read_file('CHANGES.txt')

setup(name='cykooz.sequence',
      version=version,
      description='Generates a persistent sequence',
      long_description='\n\n'.join([readme, sequence_doc, changes]),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Framework :: Zope3',
        'License :: OSI Approved :: Zope Public License',
        'Programming Language :: Python',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP'
        ],
      keywords='',
      author='Cykooz',
      author_email='saikuz@mail.ru',
      url='https://bitbucket.org/cykooz/cykooz.sequence',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['cykooz'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(test=[
          'zope.app.testing',
          'zope.app.zcmlfiles',
      ]),
      install_requires=[
          'distribute',
          'ZODB3',
          'zope.component',
          'zope.interface',
          'zope.annotation'
          ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
