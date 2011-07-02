from setuptools import setup
setup(
    name='camlistore-client',
    version='1.0dev',
    author='Brett Slatkin',
    author_email='bslatkin@gmail.com',
    url='http://camlistore.org',
    license='Apache v2',
    long_description="Client library for Camlistore.",
    packages=['camli'],
    install_requires=['simplejson'],
    classifiers=['Environment :: Console', 'Topic :: Internet :: WWW/HTTP']
)