"""
sqlwitch is a Python 2.5+ library that offers idiomatic SQL generation on top 
of MySQLdb. BSD-licensed.

Usage
`````

::

    with db.insert(into='foobars') as obj:
        obj.foo = 1
    with db.select('foo, bar', from_='foobars'):
        db.where('foo = 1')    
    with db.update('foobars') as changeset:
        changeset.foo = 2
        db.where('foo = 1')
    with db.delete(from_='foobars'):
        db.where('foo = 2')

Setup
`````

::

    $ pip install sqlwitch # or
    $ easy_install sqlwitch # or
    $ cd sqlwitch-0.2; python setup.py install

Links
`````

* `Full documentation <http://jonasgalvez.com.br/Software/SQLWitch.html>`_
* `Development repository <http://github.com/galvez/sqlwitch/>`_
* `Author's website <http://jonasgalvez.com.br/>`_

"""

from distutils.core import setup

setup(
    name = 'sqlwitch',
    version = '0.2',
    url = 'http://jonasgalvez.com.br/Software/SQLWitch.html',
    license = 'BSD',
    author = "Jonas Galvez",
    author_email = "jonasgalvez@gmail.com",
    description = "sqlwitch offers idiomatic SQL generation on top of MySQLdb.",
    long_description = __doc__,
    py_modules = ['sqlwitch'],
    platforms = 'Python 2.5 and later',
    classifiers = [
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Database :: Front-Ends',
        'Topic :: Database'
    ]
)