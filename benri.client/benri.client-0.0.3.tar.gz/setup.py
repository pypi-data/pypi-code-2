try:
    from setuptools import setup, find_packages
except ImportError, e:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(name='benri.client',
    version='0.0.3', 
    author='Mikael Hoegqvist',
    author_email='hoegqvist@zib.de',
    url='http://pypi.python.org/pypi/benri.client/',
    download_url='',
    description='A client package for benri-based services.',
    license='Apache 2.0',
    long_description="""Client package for benri-based services.""",
    include_package_data = True,
    namespace_packages = ['benri'],
    packages = find_packages(),
    install_requires = [
        "httplib2 == 0.6.0",
        "simplejson >= 1.7.3"
    ],    
     classifiers=[
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Programming Language :: Python',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Software Development :: Libraries',
    ],
    zip_safe = False,
    )

