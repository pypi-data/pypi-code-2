from distutils.core import setup

setup( name = 'mivrhash',
       version = '1.0.1',
       author = 'Conbodien',
       author_email = 'duc@mi.ci.i.u-tokyo.ac.jp',
       url = 'http://pypi.python.org/pypi/mivrhash/',
       packages = [ 'mivrhash', 'mivrhash.testsuite' ],
       description = 'A hash table (Python dict compatible) that stores data in remote servers. Performance is optimized by using write-back cache.',
       long_description = open( 'README.txt' ).read(),
       classifiers = [
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Utilities',
          'Topic :: System :: Distributed Computing',
          'License :: OSI Approved :: Python Software Foundation License'
        ],
       keywords = 'remote hash, hash table',
       platforms = [ 'Any' ],
       )

