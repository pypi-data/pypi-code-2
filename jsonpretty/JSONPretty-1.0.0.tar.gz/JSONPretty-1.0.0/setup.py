from setuptools import setup, find_packages

setup(
    name='JSONPretty',
    version='1.0.0',
    description='Prettify JSON',
    author='Chris Soyars',
    author_email='ctso@ctso.me',
    url='https://github.com/ctso/JSONPretty',

    packages=find_packages('src'),
    package_dir={'': 'src'},

    install_requires=[
        'simplejson',
    ],

    entry_points={
        'console_scripts': ['jsonpretty = jsonpretty:main'],
    }
)
