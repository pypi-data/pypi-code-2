#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2010 David Larlet. All rights reserved.

from setuptools import setup

setup(name='redis_triplestore',
      version = '0.1',
      author="David Larlet",
      author_email="david@larlet.fr",
      url="http://code.welldev.org/redis_triplestore/",
      download_url="http://code.welldev.org/redis_triplestore/downloads/",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      packages=['redis_triplestore'],
      platforms=["Any"],
      license="BSD",
      keywords='redis triplestore',
      include_package_data = True,
      description="Implements a triplestore using Redis to store relations, in Python.",
      long_description="""\
redis_triplestore
-----------------

Implements a triplestore using Redis to store relations, in Python.

Requires Redis 2.0+, newest version of redis-py and redis_wrap.

redis-py can be downloaded from here:
* http://github.com/andymccurdy/redis-py

Note that you can use the requirements.txt file to install dependencies with pip.

Examples
--------

Atribution::

    FOAF = Namespace('http://xmlns.com/foaf/0.1/')

    frodo = Resource('http://example.com/comte/frodo', **{
        FOAF.name: 'Frodo',
        FOAF.familyName: 'Baggins',
    })
    assert frodo[FOAF.name] == 'Frodo'
    
Persistence::

    frodo = Resource('http://example.com/comte/frodo')
    assert frodo[FOAF.name] == 'Frodo'
    
    gandalf = Resource('http://example.com/wizards/gandalf', **{
        FOAF.name: 'Gandalf',
        FOAF.familyName: 'the White',
    })
    saruman = Resource('http://example.com/wizards/saruman', **{
        FOAF.name: 'Saruman',
        FOAF.familyName: 'of Many Colors',
    })
    
Relations::

    frodo.add_relation(FOAF.knows, gandalf)
    assert frodo.relations(FOAF.knows) == [gandalf]
    gandalf.add_relation(FOAF.knows, saruman)
    assert gandalf.relations(FOAF.knows) == [saruman]
    assert gandalf.reversed_relations(FOAF.knows) == [frodo]
    frodo.add_relation(FOAF.knows, saruman)
    assert frodo.relations(FOAF.knows) == [gandalf, saruman]
    
Clean up::

    frodo.delete_relation(FOAF.knows, saruman)
    assert frodo.relations(FOAF.knows) == [gandalf]
    frodo.delete_relation(FOAF.knows, gandalf)
    gandalf.delete_relation(FOAF.knows, saruman)
    assert gandalf.relations(FOAF.knows) == []
    assert gandalf.reversed_relations(FOAF.knows) == []
    frodo.remove()
    gandalf.remove()
    saruman.remove()
    assert frodo[FOAF.name] == None

Copyright: 2010 by David Larlet
License: BSD.""")
