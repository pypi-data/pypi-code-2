from distutils.core import setup
import demain
description, long_description = demain.__doc__.split('\n', 1)
setup(name='demain',
      version='0.9',
      description=description,
      long_description=long_description,
      license = 'MIT',
      author='Brandon Craig Rhodes',
      author_email='brandon@rhodesmill.org',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries',
        ],
      url='http://bitbucket.org/brandon/demain',
      packages=['demain'],
      package_data={'demain': ['test_situations/*/*.py',
                               'test_situations/*/*/*.py']}
      )
