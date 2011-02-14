from os.path import join
from setuptools import setup, find_packages

version = '0.3'

readme = open(join("src", "menhir", "contenttype", "file", "README.txt")).read()
change = open(join("docs", "HISTORY.txt")).read()

tests_require = [
    'zope.publisher',
    ]

setup(name='menhir.contenttype.file',
      version=version,
      description="File content type for Grok and Dolmen applications.",
      long_description=readme + '\n' + change,
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Grok Dolmen File Content',
      author='Souheil Chelfouh',
      author_email='trollfot@gmail.com',
      url='http://pypi.python.org/pypi/menhir.contenttype.file',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['menhir', 'menhir.contenttype'],
      include_package_data=True,
      zip_safe=False,
      tests_require = tests_require,
      extras_require = {'test': tests_require},
      install_requires=[
          'dolmen.app.content >= 1.0b1',
          'dolmen.app.security',
          'dolmen.blob',
          'dolmen.content >= 0.7',
          'dolmen.file',
          'setuptools',
          'zope.i18n',
          'zope.component',
          'zope.i18nmessageid',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
