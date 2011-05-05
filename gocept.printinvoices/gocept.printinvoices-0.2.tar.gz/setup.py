# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import os.path
from setuptools import setup, find_packages


def read(*path):
    return open(os.path.join(*path)).read() + '\n\n'


setup(
    name='gocept.printinvoices',
    version='0.2',
    author='gocept',
    author_email='mail@gocept.com',
    description=(
        'Print a batch of invoices from Collmex on paper from two trays.'
        ),
    long_description=(
        read('README.txt') +
        read('CHANGES.txt')
        ),
    url='http://pypi.python.org/pypi/gocept.printinvoices',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    namespace_packages=['gocept'],
    install_requires=[
        'setuptools',
        ],
    entry_points="""\
    [console_scripts]
    process-pdf = gocept.printinvoices.main:process_pdf
    process-ps = gocept.printinvoices.main:process_ps
    """,
)
