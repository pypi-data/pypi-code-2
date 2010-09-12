from distutils.core import setup

classifiers = [ 'Development Status :: 4 - Beta'
              , 'Intended Audience :: Developers'
              , 'License :: OSI Approved :: BSD License'
              , 'Operating System :: MacOS :: MacOS X'
              , 'Operating System :: POSIX :: Linux'
              , 'Operating System :: Unix'
              , 'Programming Language :: Python :: 2.6'
              , 'Topic :: Software Development :: Libraries :: Python Modules'
              ]

setup(name='PySettings',
      version='0.1.90',
      author='Robert Escriva (rescrv)',
      author_email='pysettings@mail.robescriva.com',
      packages=['pysettings'
               ],
      package_dir={'firmant': 'firmant'},
      license='3-clause BSD',
      description='A small package for handling application settings similar.',
      long_description=open('README.rst').read(),
      classifiers=classifiers,
      )
