from distutils.core import setup

VERSION = '0.1.3'


setup(
    name='django-crossdb',
    version=VERSION,
    packages=['crossdb'],
    author='Eric Shull',
    author_email='eric.shull@gmail.com',
    description='Tools for enabling Django models to relate to each other across databases.',
    long_description='''''',
    license='BSD',
    keywords='django',
    url='http://bitbucket.org/gazetteer/django-crossdb',
)
