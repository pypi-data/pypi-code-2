from setuptools import setup, find_packages

setup(
    name="python-rest-client",
    version = '0.3',
    description="A REST Client for use in python, using httplib2 and urllib2.",
    package_dir = {'': 'src'},
    packages=find_packages('src'),
    py_modules = [
        'gae_restful_lib',
        'microblog_exceptions',
        'mimeTypes',
        'restful_lib',
        'talis',
        'tinyurl',
        'twitter',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
    ],
    author="Benjamin O'Steen",
    license="GPLv3",
    url='http://code.google.com/p/python-rest-client/',
)
