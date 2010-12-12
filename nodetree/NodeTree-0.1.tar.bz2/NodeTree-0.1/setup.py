#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''NodeTree - Python XML stream parsing

    Most XML libraries fit into one of two categories; they either parse XML
    streams with callbacks for each event encountered but leave it to the user
    to store and organize these events (such as expat or SAX), or they parse
    the entire XML document into memory in one batch and return a handle to
    the document's root element only after its finished (DOM and ElementTree).

    While the latter is much easier to work with, it also requires that the
    entire XML stream be available before any of it can be processed and must
    load the entire stream into memory, even when only a piece of it needs to
    be evaluated at a time.

    With NodeTree we seek a hybrid of these two techniques.  Callbacks can be
    set for virtually every stage of processing, but what is returned is the
    (possibly incomplete) object being processed.  Nodes which have been fully
    processed can be removed from the tree in processing to save memory and
    the user can even specify an alternative class to create child nodes of an
    element.  The goal is a clean, Pythonic API usable for the most basic
    to the most advanced XML processing.

    NodeTree is similar to the familiar ElementTree API with a few notable
    differences:

      * Element.tag has been renamed to Element.name

      * Element attributes are a dictionary at Element.attributes

      * Elements are sequences of their children

      * Text inside an element is a child node, not Element.text property,
        so the order of text and child elements is preserved and available.
        Text nodes are simply strings, so you can just Element.append('text').

      * Nodes work by duck typing and can be freely mixed from other XML
        libraries including (with very little work) ElementTree or DOM

      * All nodes can be converted to XML strings with their __str__ method
'''

__credits__ = '''Copyright (C) 2010 Arc Riley

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program; if not, see http://www.gnu.org/licenses
'''

__author__  = '\n'.join((
    'Arc Riley <arcriley@gmail.com>',
))

__version__ = '0.1'

import sys
from distutils.core import setup
from distutils.extension import Extension


if __name__ == '__main__' : setup(
    #
    ###########################################################################
    #
    # PyPI settings (for pypi.python.org)
    #
    name             = 'NodeTree',
    version          = __version__,
    description      = __doc__.splitlines()[0],
    long_description = '\n'.join(__doc__.splitlines()[2:]),
    maintainer       = 'Arc Riley',
    maintainer_email = 'arcriley@gmail.org',
    url              = 'http://pypi.python.org/pypi/NodeTree',
    download_url     = 'http://pypi.python.org/packages/source/N/NodeTree/NodeTree-%s.tar.bz2' % __version__,
    license          = 'GNU Lesser General Public License version 3 (LGPLv3)',
    classifiers      = [
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    #
    ###########################################################################
    #
    # Extension settings
    #
    ext_modules = [Extension(
        name = 'nodetree',
        sources = [
            'src/module.c',
        ],
        define_macros = [
            ('NODETREE_VERSION', '"%s"' % __version__),
        ],
    )]
    #
    ###########################################################################
)

