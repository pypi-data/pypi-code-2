from setuptools import setup, find_packages
from os.path import join

name = 'dolmen.widget.file'
version = '1.0b2'
readme = open(join('src', 'dolmen', 'widget', 'file', 'README.txt')).read()
history = open(join('docs', 'HISTORY.txt')).read()

install_requires = [
    'dolmen.file >= 0.5.1',
    'grokcore.component',
    'grokcore.view',
    'setuptools',
    'zope.interface',
    'zope.size',
    'zope.i18n',
    'zope.location',
    'zope.traversing',
    'zeam.form.base >= 1.0',
    'zeam.form.ztk >= 1.0',
    'zope.i18nmessageid',
    ]

tests_require = [
    'zope.site',
    'zope.testing',
    'zope.app.testing', # needed for zeam
    'zope.container',
    'zope.component',
    'zope.publisher',
    'zope.schema',
    'zope.security',
    'zope.i18n',
    ]

setup(name = name,
      version = version,
      description = 'File widget for `zeam.form` and `Dolmen`',
      long_description = readme + '\n\n' + history,
      keywords = 'Grok Zope3 Zeam Dolmen Widget File',
      author = 'Souheil Chelfouh',
      author_email = 'trollfot@gmail.com',
      url = '',
      license = 'GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages = ['dolmen', 'dolmen.widget'],
      include_package_data = True,
      platforms = 'Any',
      zip_safe = False,
      tests_require = tests_require,
      install_requires = install_requires,
      extras_require = {'test': tests_require},
      test_suite="dolmen.widget.file",
      classifiers = [
          'Environment :: Web Environment',
          'Framework :: Zope3',
          'Intended Audience :: Other Audience',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      entry_points="""
      # -*- Entry points: -*-
      [zeam.form.components]
      file = dolmen.widget.file.widget:register
      """,
)
