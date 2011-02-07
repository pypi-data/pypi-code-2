#!/usr/bin/python -tt

setupArgs = {
	'name' : 'compactxml',
	'version' : '2.1.0',
	'author' : 'John Krukoff',
	'author_email' : 'python@cultist.org',
	'url' : 'http://code.google.com/p/compactxml/',
	'description' : 'Parser and converter for an alternate compact XML syntax.',
	'long_description' : '''
-----------
Compact XML
-----------

Summary
-------
Compact XML is an alternative syntax for representing XML files. It uses
indentation to indicate nesting to give a python like feel, XPath based
prefixes to identify nodes, and has a macro system to shorten common XML
constructs. It is intended for writing element based XML files, especially
those where the XML elements share a common structure such as XSLT files.

This package includes a parser and bidirectional converter for converting from
this compact XML syntax to XML, and from XML to this compact XML syntax.

Why Do I Want This?
-------------------
Unlike most projects to create a shorter XML, compact XML is not designed for
compressing XML on the wire. Instead, this syntax is designed to make editing
XML easier with common editors, and to provide a convenient, configurable
shorthand when authoring XML documents with a common syntax.

If you spend all day writing XSLT files or something similar, this will let
you work with source files that look like this::

	xsl:stylesheet
		xsl:output xml no

		xsl:template "@* | node( )"
			xsl:copy
				xsl:apply-templates "@* | node( )"

Instead of like this::

	<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="xml" indent="no"/>

	<xsl:template match="@* | node( )">
		<xsl:copy>
			<xsl:apply-templates select="@* | node( )"/>
		</xsl:copy>
	</xsl:template>

	</xsl:stylesheet>

If you're integrating with a python based program, the parser can be built in
and parse compact XML files to XML directly. Otherwise a simple command line
utility is included that can be used inside make or equivalent to convert to
XML as part of your build process.

Install
-------
compactxml is a pure python library, and should be platform independent. It
has been developed and tested on python 2.6 on linux, however. As
dependencies, it requires that lxml_ and pyparsing_ be installed to
function.

A normal ``python setup.py install`` command should work to install the library.

.. _lxml: http://codespeak.net/lxml/
.. _pyparsing: http://pyparsing.wikispaces.com/

Usage
-----
There is a ``compactxml.expand`` function for converting from compact XML
syntax to XML, and a ``compactxml.compact`` function for converting from XML
to compact XML syntax, with variations on both depending on the output format
desired. ``help( compactxml )`` will give better usage instructions, and the
included documentation in ``compactxml.rst`` provides a comprehensive overview
of the compact xml syntax.

Any errors in expansion or compaction are raised as
``compactxml.ParsingError``.

There is also a command line utility ``compactxml.py`` in the source
distribution which can be used for converting from/to compact xml syntax. See
``compactxml.py --help`` for usage information after installation.

Documentation
-------------
Detailed `documentation <http://packages.python.org/compactxml>`_ of the
compact XML format is available through the python package index, including a
tutorial for new users.

''',
	'download_url' : 'http://code.google.com/p/compactxml/downloads/list',
	'license' : 'GPL v2',
	'keywords' : 'xml compact shorter format',
	'packages' : [ 'compactxml' ],
	'scripts' : [ 'scripts/compactxml' ],
	}

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
else:
	setupArgs.update( {
		# setuptools extensions.
		'test_suite' : 'nose.collector',
		'install_requires' : [ 'lxml', 'pyparsing' ],
		'tests_require' : [ 'nose' ],
		} )

setup( **setupArgs )
