from setuptools import setup, find_packages

long_description = (open('README.txt').read()
                    + '\n\n' +
                    open('CHANGES.txt').read())

setup(name='z3c.autoinclude',
      version='0.3.4',
      description="Automatically include ZCML",
      long_description=long_description,
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ethan Jucovy, Robert Marianski, Martijn Faassen',
      author_email='zope-dev@zope.org',
      url='',
      license='ZPL',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zope.dottedname',
          'zope.interface',
          'zope.configuration',
          'zope.schema',
          'zc.buildout',
      ],
      extras_require={'test': ['zc.buildout','zope.testing']},
      entry_points="""
      [console_scripts]
      autoinclude-test = z3c.autoinclude.tests.tests:interactive_testing_env
      """,
      )
