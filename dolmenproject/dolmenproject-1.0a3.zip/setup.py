from setuptools import setup, find_packages

_description = (
    "Script that creates a Dolmen project directory, installs Grok, the Grok "
    "Toolkit and the Zope Toolkit and sets up a complete skeleton for "
    "a new Dolmen application."
    )

long_description = (
    "=============\n"
    "Dolmenproject\n"
    "=============\n"
    "\n"
    "%s\n"
    "\n"
    ".. contents::\n"
    "\n"
    "Description\n"
    "===========\n"
    "\n" +
    open('README.txt').read() +
    '\n' +
    open('CHANGES.txt').read()
    ) % _description

setup(
    name='dolmenproject',
    version = '1.0a3',
    author='Dolmen Team',
    author_email='vincent.fretin@gmail.com',
    url='http://www.dolmen-project.org',
    description=_description,
    long_description=long_description,
    license='ZPL',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['grokproject >= 2.5, < 2.6'],
    test_suite='tests.test_suite',
    entry_points={
    'console_scripts': ['dolmenproject = dolmenproject:main'],
    'paste.paster_create_template': ['dolmen = dolmenproject:DolmenProject']},
    )
