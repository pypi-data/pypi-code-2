#!/usr/bin/python -tt

from __future__ import absolute_import

from lxml import etree

import compactxml

def expand( compacted, **kwargs ):
	print '\nInput to expand:\n', compacted
	result = compactxml.expand( compacted, **kwargs )
	print '\nExpanded output:\n', etree.tostring( result )
	return result

def test_name_expression( ):
	result = expand( '''
?variable test=x
< a 
+ b 
+c 
+ d
+e
+ -_. 
$ test 
$test 
$ test
$test
''' )

	assert result.getroot( ).tag == 'abcde-_.xxxx'

def test_unquoted_value_expression( ):
	result = expand( '''
?variable test=x
<a
	" a 
	+ b 
	+c 
	+ d
	+e
	\\ f 
	\\g 
	\\ h
	\\i
	$ test 
	$test 
	$ test
	$test
''' )

	assert result.getroot( ).text == ' a  b c  de\n f \ng \n h\nixxxx'

def test_single_quoted_value_expression( ):
	result = expand( """
?variable test=x
<a
	" 'a' 
	+ 'b' 
	+'c' 
	+ 'd'
	+'e'
	+''''
	+'"'
	+'""'
	\\ 'f' 
	\\'g' 
	\\ 'h'
	\\'i'
	\\''''
	\\'"'
	\\'""'
	$ test 
	$test 
	$ test
	$test
""" )

	assert result.getroot( ).text == " 'a'  'b' c 'd'e'\"\"\"\n 'f' \ng\n 'h'\ni\n'\n\"\n\"\"xxxx"

def test_double_quoted_value_expression( ):
	result = expand( '''
?variable test=x
<a
	" "a" 
	+ "b" 
	+"c" 
	+ "d"
	+"e"
	+""""
	+"'"
	+"''"
	\\ "f" 
	\\"g" 
	\\ "h"
	\\"i"
	\\""""
	\\"'"
	\\"''"
	$ test 
	$test 
	$ test
	$test
''' )

	assert result.getroot( ).text == ' "a"  "b" c "d"e"\'\'\'\n "f" \ng\n "h"\ni\n"\n\'\n\'\'xxxx'

def test_named_expression( ):
	result = expand( '''
?variable test=x
<a
	@ a 
	+ b 
	+c 
	+ d
	+e
	+ -_. 
	$ test 
	$test 
	$ test
	$test = a 
	+ b 
	+c 
	+ d
	+e
	\\ f 
	\\g 
	\\ h
	\\i
	$ test 
	$test 
	$ test
	$test
''' )

	assert result.getroot( ).attrib[ 'abcde-_.xxxx' ] == 'a  b c  de\n f \ng \n h\nixxxx'

def test_single_quoted_named_expression( ):
	result = expand( """
?variable test=x
<a
	@ a 
	+ b 
	+c 
	+ d
	+e
	+ -_. 
	$ test 
	$test 
	$ test
	$test = 'a' 
	+ 'b' 
	+'c' 
	+ 'd'
	+'e'
	+''''
	+'"'
	+'""'
	\\ 'f' 
	\\'g' 
	\\ 'h'
	\\'i'
	\\''''
	\\'"'
	\\'""'
	$ test 
	$test 
	$ test
	$test
""" )

	assert result.getroot( ).attrib[ 'abcde-_.xxxx' ] == "a 'b' c 'd'e'\"\"\"\n 'f' \ng\n 'h'\ni\n'\n\"\n\"\"xxxx"

def test_double_quoted_named_expression( ):
	result = expand( '''
?variable test=x
<a
	@ a 
	+ b 
	+c 
	+ d
	+e
	+ -_. 
	$ test 
	$test 
	$ test
	$test = "a" 
	+ "b" 
	+"c" 
	+ "d"
	+"e"
	+""""
	+"'"
	+"''"
	\\ "f" 
	\\"g" 
	\\ "h"
	\\"i"
	\\""""
	\\"'"
	\\"''"
	$ test 
	$test 
	$ test
	$test
''' )

	assert result.getroot( ).attrib[ 'abcde-_.xxxx' ] == 'a "b" c "d"e"\'\'\'\n "f" \ng\n "h"\ni\n"\n\'\n\'\'xxxx'

def test_element( ):
	result = expand( '<a' )
	assert result.getroot( ).tag == 'a'

def test_empty_element( ):
	try:
		expand( '<' )
	except compactxml.ParsingError, exception:
		assert exception.line == 1
		assert exception.sourceLine == '<'
	else:
		assert False

def test_element_expression( ):
	result = expand( '''
?variable test=value
<first
+next
$test
+last''' )

	assert result.getroot( ).tag == 'firstnextvaluelast'

def test_nested_element( ):
	result = expand( '''
<a
	<b
	<c
	<d
		<ind
	<e''' )

	assert result.find( 'b' ) is not None
	assert result.find( 'd/ind' ) is not None
	assert result.find( 'e' ) is not None

def test_invalid_nested_element( ):
	try:
		expand( '''
<a
		<b
	<c''' )
	except compactxml.ParsingError, exception:
		assert exception.line == 4
		assert exception.sourceLine == '\t<c'
	else:
		assert False

def test_multiple_nested_element( ):
	result = expand( '''
<a
	<b
		<c
			<d
				<e
	<b2
		<c2
	<b3
''' )

	assert result.find( 'b' ) is not None
	assert result.find( 'b/c' ) is not None
	assert result.find( 'b/c/d' ) is not None
	assert result.find( 'b/c/d/e' ) is not None
	assert result.find( 'b2' ) is not None
	assert result.find( 'b2/c2' ) is not None
	assert result.find( 'b3' ) is not None

def test_element_following_multiline_text( ):
	result = expand( '''
<a
	"
	\\
	<b
		"In b.
''' )

	assert result.find( '/b' ).text == 'In b.'

def test_leading_whitespace( ):
	result = expand( '''


<a''')

	assert result.getroot( ).tag == 'a'

def test_trailing_whitespace( ):
	result = expand( '''<a


''')

	assert result.getroot( ).tag == 'a'

def test_both_whitespace( ):
	result = expand( '''


<a


''' )

	assert result.getroot( ).tag == 'a'

def test_element_whitespace( ):
	result = expand( '''

<a


	<b


''')

	assert result.find( 'b' ) is not None

def test_incorrect_indent_whitespace( ):
	result = expand( '''

<a
			
	
	<b

			
		
	

''')

	assert result.find( 'b' ) is not None

def test_tabs_roundtrip( ):
	result = expand( '''
<a
	"
	\\	
	<b
	"
	\\
''')

	assert result.getroot( ).text == '\n\t'
	assert result.find( 'b' ).tail == '\n'

def test_inline_attribute( ):
	result = expand( '''
<a @one=1
''' )

	assert result.getroot( ).attrib[ 'one' ] == '1'

def test_attribute( ):
	result = expand( '''
<a
	@one=1
''' )

	assert result.getroot( ).attrib[ 'one' ] == '1'

def test_attribute_expression( ):
	result = expand( '''
?variable test=value
<a
	@name
	+first
	$test
	+last = value
	+first
	$test
	\\newline
	+last
''' )

	assert result.getroot( ).attrib[ 'namefirstvaluelast' ] == 'valuefirstvalue\nnewlinelast'

def test_interleaved_attribute( ):
	result = expand( '''
<a
	@one=1
	<b
		<inb
	@two=2
''' )

	assert result.getroot( ).attrib[ 'one' ] == '1'
	assert result.getroot( ).attrib[ 'two' ] == '2'

def test_quoted_attribute( ):
	result = expand( '''
<a @double="double" @single='single' @with_spaces="with spaces"
''' )

	assert result.getroot( ).attrib[ 'double' ] == 'double'
	assert result.getroot( ).attrib[ 'single' ] == 'single'
	assert result.getroot( ).attrib[ 'with_spaces' ] == 'with spaces'

def test_attribute_whitespace( ):
	result = expand( '''
<a @ inline = inline 
	@ standalone = standalone 
	@ quoted = 'quoted' 
''' )

	assert result.getroot( ).attrib[ 'inline' ] == 'inline'
	assert result.getroot( ).attrib[ 'standalone' ] == 'standalone '
	assert result.getroot( ).attrib[ 'quoted' ] == 'quoted'

def test_default_attribute( ):
	result = expand( '''
<a @default @alsodefault @value=value
''' )

	assert result.getroot( ).attrib[ 'default' ] == ''
	assert result.getroot( ).attrib[ 'alsodefault' ] == ''
	assert result.getroot( ).attrib[ 'value' ] == 'value'

def test_set_default_attribute( ):
	result = expand( '''
?default true
<a @default
''' )

	assert result.getroot( ).attrib[ 'default' ] == 'true'

def test_variable( ):
	result = expand( '''
?variable test=value
<
$test
''' )

	assert result.getroot( ).tag == 'value'

def test_variable_precendence( ):
	result = expand( '''
?variable test=overwritten
?variable test=value
<
$test
''' )

	assert result.getroot( ).tag == 'value'

def test_variable_reuse( ):
	result = expand( '''
<a
	?variable test=first
	<
	$test
	?variable test=second
	<
	$test
''' )

	assert result.getroot( )[ 0 ].tag == 'first'
	assert result.getroot( )[ 1 ].tag == 'second'

def test_nested_variable( ):
	result = expand( '''
?variable test=value
?variable
$test =
$test
<
$value
''' )

	assert result.getroot( ).tag == 'value'

def test_external_variable( ):
	result = expand( '''
?variable test=value
<
$test
''', variables = { 'test' : 'external' } )

	assert result.getroot( ).tag == 'external'

def test_omitted_variable( ):
	result = expand( '''
<a
	<
	$test
''' )

	assert len( result.getroot( ) ) == 0

def test_variable_precendence( ):
	result = expand( '''
?encoding UTF8
<a
''' )

	assert result.getroot( ).tag == 'a'

def test_xmlns_attribute_namespace( ):
	result = expand( '''
<a
	@xmlns:test="namespace"
	<test:in-namespace
''' )

	assert result.find( '{namespace}in-namespace' ) is not None

def test_xmlns_attribute_namespace_default( ):
	result = expand( '''
<a
	@xmlns="namespace"
	<in-namespace
		<no-namespace
			@xmlns=""
''' )

	assert result.getroot( ).tag == '{namespace}a'
	assert result.find( '{namespace}in-namespace' ) is not None
	assert result.find( '{namespace}in-namespace/no-namespace' ) is not None

def test_namespace( ):
	result = expand( '''
<a
	#default
	#one=one
	#two=two
	<b
	<one:b
	<two:b
''' )

	assert result.getroot( ).tag == '{default}a'
	assert result.find( '{default}b' ) is not None
	assert result.find( '{one}b' ) is not None
	assert result.find( '{two}b' ) is not None

def test_namespace_default( ):
	result = expand( '''
<a
	#default
	<b
		#
		<c
''' )

	assert result.getroot( ).tag == '{default}a'
	assert result.find( 'b' ) is not None
	assert result.find( 'b/c' ) is not None

def test_namespace_expression( ):
	result = expand( '''
?variable test=value
<a
	#default
	+first
	$test
	+last
	#one
	+first
	$test
	+last = one
	+first
	$test
	+last

	<b
	<one
	+first
	$test
	+last:b
	<onefirstvaluelast:c''' )

	assert result.getroot( ).tag == '{defaultfirstvaluelast}a'
	assert result.find( '{defaultfirstvaluelast}b' ) is not None
	assert result.find( '{onefirstvaluelast}b' ) is not None
	assert result.find( '{onefirstvaluelast}c' ) is not None

def test_inline_namespace( ):
	result = expand( '''
<a #default #one=one #two=two
	<b
	<one:b
	<two:b
''' )

	assert result.getroot( ).tag == '{default}a'
	assert result.find( '{default}b' ) is not None
	assert result.find( '{one}b' ) is not None
	assert result.find( '{two}b' ) is not None

def test_override_namespace( ):
	result = expand( '''
<a #default #one=one
	<b
		#otherdefault
	<one:b
		#one=otherone
''' )

	assert result.getroot( ).tag == '{default}a'
	assert result.find( '{otherdefault}b' ) is not None
	assert result.find( '{otherone}b' ) is not None

def test_attribute_namespace( ):
	result = expand( '''
<a #default #one=one @first=1 @one:first=one
''' )

	assert result.getroot( ).attrib[ 'first' ] == '1'
	assert result.getroot( ).attrib[ '{one}first' ] == 'one'

def test_attribute_namespace_order( ):
	result = expand( '''
<a @one:first=one #one=one
''' )

	assert result.getroot( ).attrib[ '{one}first' ] == 'one'

def test_namespace_scope( ):
	result = expand( '''
<a
	<b
		<c
			#uri:test
	<d
''' )

	assert result.find( 'b/{uri:test}c' ) is not None
	assert result.find( 'd' ) is not None

def test_prefixed_namespace_scope( ):
	try:
		result = expand( '''
<a
	<b
		<testns:c
			#testns=uri:test
	<testns:d
''' )
	except compactxml.ParsingError, exception:
		print exception
		assert 'no namespace defined for prefix' in exception.message.lower( )
		assert exception.line == 6
		assert exception.sourceLine == '\t<testns:d'

def test_default_declared_namespace( ):
	result = expand( '''
<a
	@xml:id=value
''' )

	assert result.getroot( ).attrib[ '{http://www.w3.org/XML/1998/namespace}id' ] == 'value'

def test_declared_namespace( ):
	result = expand( '''
<test:a
''', namespaces = { 'test' : 'namespace' } )

	assert result.getroot( ).tag == '{namespace}a'

def test_fail_to_redefine_default_declared_namespace( ):
	try:
		result = expand( '''
<a
''', namespaces = { 'xmlns' : 'fake' } )
	except ValueError:
		pass

def test_text( ):
	result = expand( '''
<a
	"Hello, 
	"world.
	<b
		"inb
	"afterb
''' )

	assert result.getroot( ).text == 'Hello, world.'
	assert result.find( 'b' ).text == 'inb'
	assert result.find( 'b' ).tail == 'afterb'

def test_text_expression( ):
	result = expand( '''
?variable test=value
<a
	"text
	+ first
	$test
	\\ newline
	+ last
''' )

	assert result.getroot( ).text == 'text firstvalue\n newline last'

def test_multiline_text( ):
	result = expand( '''
<a
	"One
	\Two
	\Three
''' )

	assert result.getroot( ).text == 'One\nTwo\nThree'

def test_text_whitespace( ):
	result = expand( '''
<a
	" One 
	\ Two 
	\ Three 
''' )

	assert result.getroot( ).text == ' One \n Two \n Three '

def test_blank_text( ):
	result = expand( '''
<a
	"
''' )

	assert result.getroot( ).text == ''

def test_comment( ):
	result = expand( '''
<a
	!comment
''' )

	assert str( result.getroot( )[ 0 ] ) == '<!--comment-->'

def test_comment_expression( ):
	result = expand( '''
?variable test=value
<a
	!comment
	+ first
	$test
	\\ newline
	+ last
''' )

	assert str( result.getroot( )[ 0 ] ) == '<!--comment firstvalue\n newline last-->'

def test_comment_whitespace( ):
	result = expand( '''
<a
	! comment 
	\ and space 
''' )

	assert str( result.getroot( )[ 0 ] ) == '<!-- comment \n and space -->'

def test_blank_comment( ):
	result = expand( '''
<a
	!
''' )

	assert str( result.getroot( )[ 0 ] ) == '<!---->'

def test_processing_instruction( ):
	result = expand( '''
<a
	<?target=instruction
''' )

	assert str( result.getroot( )[ 0 ] ) == '<?target instruction?>'

def test_processing_instruction_expression( ):
	result = expand( '''
?variable test=value
<a
	<?target
	+first
	$test
	+last = instruction
	+ first
	$test
	\\ newline
	+ last
''' )

	assert str( result.getroot( )[ 0 ] ) == '<?targetfirstvaluelast instruction firstvalue\n newline last?>'

def test_processing_instruction_whitespace( ):
	result = expand( '''
<a
	<?target=instruction
	\ followed by 
	\ spaces.
''' )

	assert str( result.getroot( )[ 0 ] ) == '<?target instruction\n followed by \n spaces.?>'

def test_internal_comment( ):
	result = expand( '''
?comment
<a
''' )

	assert etree.tostring( result ) == '<a/>'

def test_internal_comment_content( ):
	result = expand( '''
?comment Hello, world.
<a
''' )

	assert etree.tostring( result ) == '<a/>'

def test_internal_comment_nested( ):
	result = expand( '''
?comment
?comment ignored
<a
	?comment in a
	<b
		?comment in b
		<c
			?comment in c
		?comment after c
	?comment after b
?comment
?comment ignored
''' )

	assert etree.tostring( result ) == '<a><b><c/></b></a>'

def test_indentation( ):
	result = expand( '''
<a
	?indent restart
<b
	?indent restart
<c
	?indent resume
	?indent resume
''' )

	assert result.find( 'b' ) is not None
	assert result.find( 'b/c' ) is not None

def test_unindentation_first_column_resume( ):
	result = expand( '''
<a
	<b
		<c
			?indent restart
<d
	<e
?indent resume
			@inc
			<inc
		@inb
		<inb
	@ina
	<ina
''' )

	assert result.find( 'b/c/d/e' ) is not None
	assert result.getroot( ).attrib.get( 'ina' ) is not None
	assert result.find( 'b' ).attrib.get( 'inb' ) is not None
	assert result.find( 'b/c' ).attrib.get( 'inc' ) is not None
	assert result.find( 'ina' ) is not None
	assert result.find( 'b/inb' ) is not None
	assert result.find( 'b/c/inc' ) is not None

def test_unindentation_dedented_resume( ):
	result = expand( '''
<a
	<b
		<c
			?indent restart
<d
	<e
		<f
	?indent resume
			<ind
		<inc
	<inb
''' )

	assert result.find( 'b/c/d/e/f' ) is not None
	assert result.find( 'b/inb' ) is not None
	assert result.find( 'b/c/inc' ) is not None
	assert result.find( 'b/c/d/ind' ) is not None

def test_unindentation_previous_column_resume( ):
	result = expand( '''
<a
	<b
		<c
			?indent restart
<d
	<e
			?indent resume
			<ine
		<ind
	<inc
''' )

	assert result.find( 'b/c/d/e' ) is not None
	assert result.find( 'b/c/inc' ) is not None
	assert result.find( 'b/c/d/ind' ) is not None
	assert result.find( 'b/c/d/e/ine' ) is not None

def test_unindentation_indented_resume( ):
	result = expand( '''
<a
	<b
		<c
			?indent restart
<d
	<e
		?indent resume
			<ine
		<ind
	<inc
''' )

	assert result.find( 'b/c/d/e' ) is not None
	assert result.find( 'b/c/inc' ) is not None
	assert result.find( 'b/c/d/ind' ) is not None
	assert result.find( 'b/c/d/e/ine' ) is not None

def test_doctype( ):
	result = expand( '''
<!DOCTYPE a SYSTEM "id"
<a
''' )

	assert result.docinfo.doctype == '<!DOCTYPE a SYSTEM "id">', 'DOCTYPE was %r' % result.docinfo.doctype

def test_doctype_expression( ):
	result = expand( '''
?variable test=SYSTEM
<!DOCTYPE 
+a 
$test
+' "id"'
<a
''' )

	assert result.docinfo.doctype == '<!DOCTYPE a SYSTEM "id">', 'DOCTYPE was %r' % result.docinfo.doctype

def test_toplevel( ):
	result = expand( '''
?default "default"
!one
<?pi=target first
<a
!two
<?pi=target second
''' )

	assert 'one' in etree.tostring( result )
	assert 'two' in etree.tostring( result )
	assert 'first' in etree.tostring( result )
	assert 'second' in etree.tostring( result )

def test_toplevel_with_doctype( ):
	result = expand( '''
?default "default"
<!DOCTYPE a SYSTEM "id"
!one
<?pi=target first
<a
!two
<?pi=target second
''' )

	assert result.docinfo.doctype == '<!DOCTYPE a SYSTEM "id">'
	assert 'one' in etree.tostring( result )
	assert 'two' in etree.tostring( result )
	assert 'first' in etree.tostring( result )
	assert 'second' in etree.tostring( result )

# Attribute group tests.

def test_group( ):
	result = expand( '''
?attribute test
	#
	#default
	#prefix=testns
	@default
	@name=value
<root
	@@test
	<prefix:element
''' )

	assert result.getroot( ).attrib[ 'default' ] == ''
	assert result.getroot( ).attrib[ 'name' ] == 'value'
	assert result.getroot( ).tag == '{default}root'
	assert result.find( '{testns}element' ) is not None

def test_group_expression( ):
	result = expand( '''
?variable test=value
?attribute test
+first
$test
+last
	@name=value
<root
	@@testfirstvaluelast
''' )

	assert result.getroot( ).attrib[ 'name' ] == 'value'

def test_group_override( ):
	result = expand( '''
?attribute test
	@first=one
	@second=two
<root
	@first=1
	@@test
	@second=2
''' )

	assert result.getroot( ).attrib[ 'first' ] == 'one', 'Should be overridden by group.'
	assert result.getroot( ).attrib[ 'second' ] == '2', 'Should override group.'

def test_group_default( ):
	result = expand( '''
?default before
?attribute test
	@default
?default after
<root
	@@test
''' )

	assert result.getroot( ).attrib[ 'default' ] == 'after'

def test_group_macro( ):
	result = expand( '''
?attribute test
	@name=value
?element test
	<test
		@@test
test
''' )

	assert result.getroot( ).attrib[ 'name' ] == 'value'

def test_group_namespaced( ):
	result = expand( '''
?attribute namespace:test
	@name=value
<root
	@@namespace:test
''' )

	assert result.getroot( ).attrib[ 'name' ] == 'value'

# Macro tests.

def test_macro( ):
	result = expand( '''
?element test
	<test
test
''' )

	assert result.getroot( ).tag == 'test'

def test_macro_expression( ):
	result = expand( '''
?variable test=value
?element test
+first
$test
+last
	<test
testfirstvaluelast
''' )

	assert result.getroot( ).tag == 'test'

def test_macro_toplevel( ):
	result = expand( '''
?element simple
	<simple
?element nested
	<nested
?element macro
	nested
?element variable @one
	<
	$one
<root
	simple
	macro
	variable @one=variable
''' )

	assert result.find( 'simple' ) is not None
	assert result.find( 'nested' ) is not None
	assert result.find( 'variable' ) is not None


def test_macro_parameters( ):
	result = expand( '''
?element test @one @two=value
	<test
test
''' )

	assert result.getroot( ).tag == 'test'

def test_macro_positional( ):
	result = expand( '''
?element test @one @two
	<test
		@first =
		$one
		@second =
		$two
test 1 2
''' )

	assert result.getroot( ).tag == 'test'
	assert result.getroot( ).attrib[ 'first' ] == '1'
	assert result.getroot( ).attrib[ 'second' ] == '2'

def test_macro_positional_extra_error( ):
	try:
		expand( '''
?element test @one @two
	<test
		@first =
		$one
		@second =
		$two
test 1 2 3
''' )
	except compactxml.ParsingError, exception:
		assert 'more positional parameters given than' in exception.message.lower( )
		assert exception.line == 8
		assert exception.sourceLine == 'test 1 2 3'
	else:
		assert False

def test_macro_named( ):
	result = expand( '''
?element test @one @two
	<test
		@first =
		$one
		@second =
		$two
test @two=2 @one=1
''' )

	assert result.getroot( ).tag == 'test'
	assert result.getroot( ).attrib[ 'first' ] == '1'
	assert result.getroot( ).attrib[ 'second' ] == '2'

def test_macro_parameter_defaults( ):
	result = expand( '''
?element test @one @two=default
	<test
		@first =
		$one
		@second =
		$two
test
''' )

	assert result.getroot( ).tag == 'test'
	assert result.getroot( ).attrib[ 'second' ] == 'default'

	try:
		result.getroot( ).attrib[ 'first' ]
	except KeyError:
		pass
	else:
		assert False, 'one attribute should not exist.'

def test_macro_parameter_extra( ):
	result = expand( '''
?element test
	<test
		?contents
test @third="3"
''' )

	assert result.getroot( ).attrib[ 'third' ] == '3'

def test_macro_filtered_attribute( ):
	result = expand( '''
?element test
	<test
		?contents @
test @third="3"
	<extra
''' )

	assert result.getroot( ).attrib[ 'third' ] == '3'
	assert len( result.getroot( ) ) == 0

def test_macro_filtered_attribute_group( ):
	result = expand( '''
?attribute third
	@third=3
?element test
	<test
		?contents @
test @@third
	<extra
''' )

	assert result.getroot( ).attrib[ 'third' ] == '3'
	assert len( result.getroot( ) ) == 0

def test_macro_filtered_element( ):
	result = expand( '''
?element test
	<test
		?contents <
test @third="3"
	<extra
''' )

	try:
		result.getroot( ).attrib[ 'third' ]
	except KeyError:
		pass
	else:
		assert False, 'third attribute must not exist.'

	assert result.getroot( )[ 0 ].tag == 'extra'

def test_macro_filtered_element_alias( ):
	result = expand( '''
?element extra
	<extra
?element test
	<test
		?contents <
test @third="3"
	extra
''' )

	try:
		result.getroot( ).attrib[ 'third' ]
	except KeyError:
		pass
	else:
		assert False, 'third attribute must not exist.'

	assert result.getroot( )[ 0 ].tag == 'extra'

def test_macro_parameter_evaluate( ):
	result = expand( '''
?element test @one
	<test
		"before
		$one
		+after
		$one
		$one
		+repeated
test 1
''' )

	assert result.getroot( ).text == 'before1after11repeated'

def test_macro_statements( ):
	result = expand( '''
?element test @name @value
	<tests
		@
		$name =
		$value
		#
		$name =
		$value
		"
		$value
		!
		$value
		<?
		$name =
		$value
		<
		$name
			<child
test name value
''' )

	assert len( result.getroot( ) ) == 3
	assert result.getroot( ).attrib[ 'name' ] == 'value'
	assert result.find( 'name' ) is not None
	assert result.find( 'name/child' ) is not None
	assert result.getroot( ).text == 'value'
	assert str( result.getroot( )[ 0 ] ) == '<!--value-->'
	assert str( result.getroot( )[ 1 ] ) == '<?name value?>'

def test_nested_macro_expansion( ):
	result = expand( '''
?element two
	<two
?element one
	two
one
''' )

	assert result.getroot( ).tag == 'two'

def test_macro_namespaced( ):
	result = expand( '''
?element namespace:test
	<test
namespace:test
''' )

	assert result.getroot( ).tag == 'test'

def test_macro_undefined( ):
	try:
		expand( '''test''' )
	except compactxml.ParsingError, exception:
		assert 'macro defined' in exception.message.lower( )
		assert exception.line == 1
		assert exception.sourceLine == 'test'
	else:
		assert False

def test_nested_macro_error( ):
	try:
		expand( '''
?variable invalid=*
?element two
	<
	$invalid
?element one
	two
one
''' )
	except compactxml.ParsingError, exception:
		# Stack trace should identify all parts.
		assert 'line 8' in unicode( exception ).lower( )
		assert 'two' in unicode( exception ).lower( )
		assert 'line 7' in unicode( exception ).lower( )
		assert 'one' in unicode( exception ).lower( )
		assert 'line 4' in unicode( exception ).lower( )
		assert 'document' in unicode( exception ).lower( )
		assert exception.line == 4
		assert exception.sourceLine == '\t<'
	else:
		assert False

def test_nested_child_parser_error_lineno( ):
	try:
		expand( '''
<one
	<two
		<three
			<four
				<five "message"
''' )
	except compactxml.ParsingError, exception:
		# Stack trace should identify five line.
		assert 'line 6' in unicode( exception ).lower( ), exception
	else:
		assert False, exception
