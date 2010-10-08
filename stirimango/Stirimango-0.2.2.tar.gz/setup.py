from distutils.core import setup


classifiers = [ 'Development Status :: 4 - Beta'
              , 'Intended Audience :: Developers'
              , 'License :: OSI Approved :: BSD License'
              , 'Operating System :: MacOS :: MacOS X'
              , 'Operating System :: POSIX :: Linux'
              , 'Operating System :: Unix'
              , 'Programming Language :: Python :: 3'
              ]

setup(name='Stirimango',
      version='0.2.2',
      author='Robert Escriva (rescrv)',
      author_email='stirimango@mail.robescriva.com',
      packages=['stirimango'
               ],
      scripts=['bin/stirimango'],
      license='3-clause BSD',
      url='http://robescriva.com/',
      description='Database migrations for Postgresql.',
      long_description=open('README.rst').read(),
      classifiers=classifiers,
      )
