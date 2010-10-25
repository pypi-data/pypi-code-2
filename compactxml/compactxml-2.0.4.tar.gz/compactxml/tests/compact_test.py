#!/usr/bin/python -tt

from __future__ import absolute_import

from lxml import etree

import compactxml

def compact( value, **kwargs ):
	print '\nInput to compact:\n', value
	result = compactxml.compact( value, **kwargs )
	print '\nCompacted output:\n', result
	return result

def test_element( ):
	result = compact( '<a/>' )
	assert result == '<a\n'

def test_nested( ):
	result = compact( '<a><b><c/></b></a>' )
	assert result == '<a\n\t<b\n\t\t<c\n'

def test_attribute( ):
	result = compact( '<a one="1"/>' )
	assert result == '<a\n\t@one=1\n'

def test_quoted_attribute( ):
	result = compact( '<a one="1 2"/>' )
	assert result == '<a\n\t@one="1 2"\n'

def test_attribute_with_quotes( ):
	result = compact( '<a one=\'"\'/>' )
	assert result == '<a\n\t@one=""""\n'

def test_attribute_with_newline( ):
	result = compact( '''<a one="
"/>''' )
	assert result == '<a\n\t@one=" "\n'

def test_comment( ):
	result = compact( '<a><!--Comment--></a>' )
	assert result == '<a\n\t!Comment\n'

def test_multiline_comment( ):
	result = compact( '''<a><!--line 1
line 2
line 3
--></a>''' )

	assert result == '<a\n\t!"line 1"\n\t\\"line 2"\n\t\\"line 3"\n\t\\\n'


def test_pi( ):
	result = compact( '<a><?target instruction?></a>' )

	assert result == '<a\n\t<?target=instruction\n'

def test_multiline_pi( ):
	result = compact( '''<a><?target line 1
line 2
line 3
?></a>''' )

	assert result == '<a\n\t<?target="line 1"\n\t\\"line 2"\n\t\\"line 3"\n\t\\\n'

def test_text( ):
	result = compact( '<a>text</a>' )
	assert result == '<a\n\t"text\n'

def test_multiline_text( ):
	result = compact( '''<a>line 1
line 2
line 3
</a>''' )

	assert result == '<a\n\t""line 1"\n\t\\"line 2"\n\t\\"line 3"\n\t\\\n'

def test_default_namespace( ):
	result = compact( '''<a xmlns="uri:test"/>''' )
	assert result == '<a\n\t#uri:test\n'

def test_redefined_namespace( ):
	result = compact( '''<test:a xmlns:test="uri:test"><test:b xmlns:test="uri:other"/></test:a>''' )
	assert result == '<test:a\n\t#test=uri:test\n\t<test:b\n\t\t#test=uri:other\n'

def test_prefixed_namespace( ):
	result = compact( '''<test:a xmlns:test="uri:test"/>''' )
	assert result == '<test:a\n\t#test=uri:test\n'

def test_external_namespace( ):
	result = compact( '''<test:a xmlns:test="uri:test"/>''', namespaces = { 'test' : 'uri:test' } )
	assert result == '<test:a\n'

def test_external_namespace_mismatched_prefix( ):
	result = compact( '''<test:a xmlns:test="uri:test"/>''', namespaces = { 'test' : 'uri:other' } )
	assert result == '<test:a\n\t#test=uri:test\n'

def test_variables( ):
	result = compact( '''<abcdef/>''', variables = { 'one' : 'abc' } )
	assert result == '?variable one=abc\n<\n$one\n+def\n'

def test_encoding( ):
	result = compact( '''<?xml version="1.0" encoding="iso8859-1"?><a/>''' )
	assert result == '?encoding iso8859-1\n<a\n'

def test_default_encoding( ):
	result = compact( '''<?xml version="1.0"?><a/>''' )
	assert result == '<a\n'

def test_doctype( ):
	result = compact( '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html/>''' )
	assert result == '<!DOCTYPE "html PUBLIC ""-//W3C//DTD XHTML 1.0 Transitional//EN"" ""http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"""\n<html\n'

def test_whitespace( ):
	result = compact( '<a>\n\t<ina/>\n</a>' )
	assert result == '<a\n\t"\n\t\\"\t"\n\t<ina\n\t"\n\t\\\n'

def test_strip_text( ):
	result = compact( '<a>\n\t<ina/>\n</a>', stripText = True )
	assert result == '<a\n\t<ina\n'

def test_parse_error( ):
	try:
		compact( '<a><b/><whoooops</a>' )
	except compactxml.ParsingError, exception:
		assert exception.line == 1
		assert exception.sourceLine == '<a><b/><whoooops</a>'

def test_multiline_parse_error( ):
	try:
		compact( '<a>\n<b/>\n<whoooops\n</a>' )
	except compactxml.ParsingError, exception:
		assert exception.line == 4
		assert exception.sourceLine == '</a>'
