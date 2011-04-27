from setuptools import setup, find_packages

version = '1.5'

readme = open('README.txt').read()
changes = open('CHANGES.txt').read()
todo = open('TODO.txt').read()

long_description = '\n\n'.join([readme, todo, changes, ''])

setup(name='createzopecoverage',
      version=version,
      description="Provides single script to create coverage reports",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout@vanrees.org',
      url='http://pypi.python.org/pypi/createzopecoverage',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'z3c.coverage',
                        # Add extra requirements here
                        ],
      extras_require = {
          'test': [
              'z3c.testsetup>=0.3',
              'zc.buildout',
              ],
          },
      entry_points={
          'console_scripts': [
              'createzopecoverage = createzopecoverage.script:main',
              ],
          'zc.buildout': [
              'default = createzopecoverage.recipe:Recipe',
              ]
          },
      )
