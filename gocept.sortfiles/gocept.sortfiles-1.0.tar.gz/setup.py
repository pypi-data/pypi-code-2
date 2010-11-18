# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

from setuptools import setup, find_packages


setup(
    name='gocept.sortfiles',
    version='1.0',
    author='gocept',
    author_email='mail@gocept.com',
    url='http://pypi.python.org/pypi/gocept.sortfiles',
    description="""\
A small utility that sorts all files in a directory into subdirectories
(YYY/MM/DD) according to their creation time (ctime).
""",
    long_description=(
        open('README.txt').read()
        + '\n\n'
        + open('CHANGES.txt').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['gocept'],
    install_requires=[
        'setuptools',
    ],
    entry_points=dict(console_scripts=[
        'date-sort = gocept.sortfiles.main:sort_files',
    ]),
)
