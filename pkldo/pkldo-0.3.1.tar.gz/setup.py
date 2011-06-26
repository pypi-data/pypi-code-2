#
# Filename: SETUP.PY
#

from distutils.core import setup

setup(
    name='pkldo',
    version='0.3.1',
    description='Pickled Data Object: Python data persistence for apps with simple needs.',
    author='Andrew Pirus',
    author_email='andrew@pzland.com',
    url='http://pypi.python.org/pypi/pkldo',
    download_url='http://pypi.python.org/pypi/pkldo',
    packages=['pkldo'],
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords='persistence pickle',
    long_description="""\
Description
-----------

Pickled Data Object (pkldo) is method #470 for saving Python data to a file.  It provides
functionality for create, retrieve, update, and delete operations and uses Python's built-in
Pickle routines.  It also performs operations atomically and offers file integrity.  Its
best fit is for applications with basic data persistence needs.

Development Status
------------------

* Tested on BSD and Linux.
* Windows compatibility will be next.
* Documentation in progress.

Quick Example
-------------

Here's a brief example of how to use a Pickled Data Object::

    >>> import pkldo
    >>> class Test(pkldo.Pdo):
    ...     pass
    ... 
    >>> a = Test()
    >>> a.some_data = "howdy"
    >>> a.create_pdo('/tmp/some_file')
    >>> b = Test()
    >>> b.load_pdo('/tmp/some_file')
    >>> b.some_data
    'howdy'
    >>> b.some_data = "hmmmm"
    >>> b.save_pdo()
    >>> c = Test()
    >>> c.load_pdo('/tmp/some_file')
    >>> c.some_data
    'hmmmm'
    >>> c.delete_pdo()
    >>> 

"""
)


#
# EOF
#
