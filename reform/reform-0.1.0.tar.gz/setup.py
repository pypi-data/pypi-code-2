try:
    from distribute import setup
except ImportError:
    try:
        from setuptools import setup
    except ImportError:
        from distutils.core import setup

from email.utils import parseaddr

from reform import __version__, __author__, __license__

name, email = parseaddr(__author__)

setup(version=__version__,
      name='reform',
      packages=['reform'],
      author=name,
      author_email=email,
      description='Validate and convert forms',
      license=__license__,
      keyword='form html http web',
      install_requires=['MarkupSafe>=0.11'],
      test_suite='tests',
      classifiers=[
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: ISC License (ISCL)',
          'Programming Language :: Python :: 2.6',
      ])
