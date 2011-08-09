from setuptools import setup, find_packages
import os

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('src/hurry/file/README.txt')
    + '\n' +
    read('src/hurry/file/browser/file.txt')
    + '\n' + 
    read('CHANGES.txt')
    )

setup(
    name="hurry.file",
    version="1.2.1",
    description="""\
hurry.file is an advanced Zope 3 file widget which tries its best to behave
like other widgets, even when the form is redisplayed due to a validation
error. It also has built-in support for fast Apache-based file uploads
and downloads through Tramline.
""",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Zope3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    keywords='zope zope3',
    author='Martijn Faassen, Infrae',
    author_email='faassen@startifact.com',
    url='',
    license='ZPL 2.1',
    packages=find_packages('src'),
    package_dir= {'':'src'},
    namespace_packages=['hurry'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
       'setuptools',
       'ZODB3',
       'zope.interface',
       'zope.schema',
       'zope.component',
       'zope.testing',
       'zope.publisher',
       'zope.app.form',
       'zope.session',
       'zope.app.testing',
       'zope.app.container',
       ],
    )
