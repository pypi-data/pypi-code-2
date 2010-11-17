from os.path import join
from setuptools import setup, find_packages

name = 'dolmen.file'
version = '0.6'
readme = open(join('src', 'dolmen', 'file', "README.txt")).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'ZODB3',
    'grokcore.component',
    'grokcore.view',
    'setuptools',
    'zope.component',
    'zope.contenttype',
    'zope.interface',
    'zope.publisher',
    'zope.schema',
    'zope.security',
    'zope.size',
    'zope.traversing',
    ]

tests_require = [
    'zope.container',
    'zope.principalregistry',
    'zope.securitypolicy',
    'zope.site',
    ]

setup(name=name,
      version=version,
      description="A Zope3/Grok File Representation package.",
      long_description = readme + '\n\n' + history,
      keywords='Grok Zope3 file download',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['dolmen'],
      include_package_data=True,
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.file",
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Zope3',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
    )
