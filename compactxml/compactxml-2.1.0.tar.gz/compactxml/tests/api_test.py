#!/usr/bin/python -tt

from __future__ import absolute_import

import StringIO

from lxml import etree

import compactxml

def test_expand_string( ):
	result = compactxml.expand( '<a' )

	assert result.getroot( ).tag == 'a'

def test_expand_file( ):
	result = compactxml.expand( StringIO.StringIO( '<a' ) )

	assert result.getroot( ).tag == 'a'

def test_expand_to_string( ):
	result = compactxml.expand_to_string( '<a' )

	assert result == '<a/>'

	result = compactxml.expand_to_string( '<a\n\t<b', prettyPrint = True )

	assert result == '<a>\n  <b/>\n</a>\n'

def test_expand_to_file( ):
	result = StringIO.StringIO( )
	compactxml.expand_to_file( '<a', result )

	result.seek( 0 )
	assert result.read( ) == '<a/>'

	result = StringIO.StringIO( )
	compactxml.expand_to_file( '<a\n\t<b', result, prettyPrint = True )

	result.seek( 0 )
	assert result.read( ) == '<a>\n  <b/>\n</a>\n'

def test_compact_string( ):
	result = compactxml.compact( '<a/>' )

	assert result == '<a\n'

def test_compact_file( ):
	result = compactxml.compact( StringIO.StringIO( '<a/>' ) )

	assert result == '<a\n'

def test_compact_to_string( ):
	result = compactxml.compact_to_string( '<a/>' )

	assert result == '<a\n'

def test_compact_to_file( ):
	result = StringIO.StringIO( )
	compactxml.compact_to_file( '<a/>', result )

	result.seek( 0 )
	assert result.read( ) == '<a\n'

