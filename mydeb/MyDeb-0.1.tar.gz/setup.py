 #!/usr/bin/env python

from distutils.core import setup

setup(name='MyDeb',
      version='0.1',
      description='Debian GNU/Linux backup manager',
      author='Behnam Ahmad Khan Beigi',
      author_email='b3hnam@gnu.org',
      url='https://gitorious.org/mydeb/',
      license='GPL v2',
      scripts=["mydeb", ],
      packages=['Mydeb', ],

      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities',
          ]
     )
