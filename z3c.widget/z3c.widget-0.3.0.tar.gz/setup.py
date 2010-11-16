#!python
from setuptools import setup, find_packages
import os.path

def read(*path_elements):
    return "\n\n" + file(os.path.join(*path_elements)).read()


setup(name='z3c.widget',
      version='0.3.0',
      author = "Zope Community",
      author_email = "zope-dev@zope.org",
      description = "Additional zope.formlib Widgets",
      license = "ZPL 2.1",
      keywords = "zope zope3 form formlib",
      url='http://svn.zope.org/z3c.widget',
      long_description=(
          '.. contents::\n\n' +
          read('CHANGES.txt') +
          read('src', 'z3c', 'widget', 'autocomplete', 'README.txt') +
          read('src', 'z3c', 'widget', 'autocomplete', 'demo', 'README.txt') +
          read('src', 'z3c', 'widget', 'country', 'README.txt') +
          read('src', 'z3c', 'widget', 'dateselect', 'README.txt') +
          read('src', 'z3c', 'widget', 'dropdowndatewidget', 'README.txt') +
          read('src', 'z3c', 'widget', 'flashupload', 'README.txt') +
          read('src', 'z3c', 'widget', 'image', 'README.txt') +
          read('src', 'z3c', 'widget', 'namespace', 'README.txt') +
          read('src', 'z3c', 'widget', 'optdropdown', 'README.txt') +
          read('src', 'z3c', 'widget', 'sequence', 'README.txt') +
          read('src', 'z3c', 'widget', 'ssn', 'README.txt') +
          read('src', 'z3c', 'widget', 'tiny', 'README.txt') +
          read('src', 'z3c', 'widget', 'usphone', 'README.txt')
          ),
      zip_safe=False,
      packages=find_packages('src'),
      include_package_data=True,
      package_dir = {'':'src'},
      namespace_packages=['z3c',],
      extras_require = dict(test=['zope.app.testing',
                                  'zope.testing',
                                  'zope.app.securitypolicy',
                                  'zope.app.zcmlfiles',
                                  'zope.testbrowser',
                                  ]),
      install_requires = ['setuptools',
                          'ZODB3',
                          'z3c.i18n',
                          'z3c.javascript',
                          'z3c.schema',
                          'zc.resourcelibrary',
                          'zope.app.cache',
                          'zope.app.container',
                          'zope.app.file',
                          'zope.app.i18n',
                          'zope.app.pagetemplate',
                          'zope.component',
                          'zope.event',
                          'zope.filerepresentation',
                          'zope.formlib >= 4.0',
                          'zope.i18n',
                          'zope.i18nmessageid',
                          'zope.interface',
                          'zope.lifecycleevent',
                          'zope.publisher',
                          'zope.schema >= 3.6',
                          'zope.security',
                          'zope.traversing',
                          ],
      classifiers = ['Development Status :: 4 - Beta',
                     'Environment :: Web Environment',
                     'Framework :: Zope3',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: Zope Public License',
                     'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     ],
      )

