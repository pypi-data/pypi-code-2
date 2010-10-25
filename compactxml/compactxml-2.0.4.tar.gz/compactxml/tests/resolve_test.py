#!/usr/bin/python -tt

from __future__ import absolute_import

import nose

from lxml import etree

import compactxml

def expand( compacted ):
	print '\nInput to expand:\n', compacted
	result = compactxml.expand( compacted )
	print '\nExpanded output:\n', etree.tostring( result )
	return result

def test_loaded( ):
	result = expand( '''
?attribute test
	@name=value
?element test
	<test
<load
''' )

def setup_custom_resolver( ):
	def resolve_static( location ):
		return '''
?attribute test
	@name=value
?element test
	<test
		@@test
<load
'''

	global old_resolver
	old_resolver = compactxml.resolve
	compactxml.resolve = resolve_static

def teardown_custom_resolver( ):
	global old_resolver
	compactxml.resolve = old_resolver

@nose.with_setup( setup_custom_resolver, teardown_custom_resolver )
def test_custom_resolver( ):
	result = expand( '''
?load fake
test
''' )

	assert result.getroot( ).tag == 'test'
	assert result.getroot( ).attrib[ 'name' ] == 'value'
