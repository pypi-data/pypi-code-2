#!/usr/bin/python -tt

from __future__ import absolute_import

import re

import pyparsing

from . import pyparsingaddons as addons

def create_grammar( ):
	# Global values for grammar. Use function scope to create thread
	# safety.
	aIndentations = [ 1 ]
	aIndentationStack = []

	def push_indent( s, loc, toks ):
		aIndentationStack.append( aIndentations[ : ] )
		aIndentations[ : ] = [ 1 ]
		return toks

	def pop_indent( s, loc, toks ):
		aIndentations[ : ] = aIndentationStack.pop( )
		return toks

	# Avoid setting default, as causes problems for other pyparsing
	# modules.
	#pyparsing.ParserElement.setDefaultWhitespaceChars( ' \t' )

	def continuation( delimiter ):
		return ( pyparsing.LineEnd( ).suppress( ) + 
			pyparsing.FollowedBy( delimiter ) + 
			addons.checkIndent( aIndentations ) + 
			pyparsing.Literal( delimiter ) )

	def insert_token( token ):
		def add_token( s, loc, toks ):
			toks.insert( 0, token )
			return toks

		return add_token

	name = pyparsing.Regex( r'[-_.\w:]+', re.U )
	startName = pyparsing.Optional( name, default = '' ).setParseAction( insert_token( '+' ) )
	variableNameContinuation = continuation( '$' ) - name
	concatenateNameContinuation = continuation( '+' ) - name
	nameContinuation = pyparsing.ZeroOrMore( variableNameContinuation | concatenateNameContinuation )
	nameExpression = pyparsing.Group( startName + nameContinuation )

	unquotedLiteral = pyparsing.CharsNotIn( '\r\n' ).leaveWhitespace( )
	singleQuotedLiteral = pyparsing.QuotedString( quoteChar = "'", escQuote = "''" )
	doubleQuotedLiteral = pyparsing.QuotedString( quoteChar = '"', escQuote = '""' )
	literal = ( singleQuotedLiteral | doubleQuotedLiteral | unquotedLiteral ).leaveWhitespace( )
	startLiteral = pyparsing.Optional( literal, default = '' ).setParseAction( insert_token( '+' ) )
	variableContinuation = continuation( '$' ) - name
	concatenateContinuation = continuation( '+' ) - literal
	lineContinuation = continuation( '\\' ) - pyparsing.Optional( literal, default = '' )
	literalContinuation = pyparsing.ZeroOrMore( variableContinuation | concatenateContinuation | lineContinuation )
	expression = pyparsing.Group( startLiteral + literalContinuation )
	namedExpression = nameExpression + '=' + pyparsing.Empty( ) - expression

	inlineName = name.copy( ).setParseAction( insert_token( '+' ) )
	inlineNameExpression = pyparsing.Group( inlineName )
	unquotedInlineLiteral = pyparsing.Empty( ) + pyparsing.CharsNotIn( ' \t\r\n' )
	inlineLiteral = singleQuotedLiteral | doubleQuotedLiteral | unquotedInlineLiteral
	inlineLiteral.setParseAction( insert_token( '+' ) )
	inlineExpression = pyparsing.Group( inlineLiteral )
	namedInlineExpression = inlineNameExpression + '=' - inlineExpression

	inlineNamespace = '#' - ( namedInlineExpression | inlineNameExpression )
	inlineNamespace.setName( 'inlineNamespace' ).setDebug( )
	inlineAttributeExpansion = '@@' - inlineNameExpression
	inlineAttribute = ( namedInlineExpression | inlineNameExpression )
	inlineAttribute.setName( 'inlineAttribute' ).setDebug( )
	inlineAttributeLoose = pyparsing.Optional( '@', default = '@' ) + inlineAttribute
	inlineAttributeLoose.setName( 'inlineAttributeLoose' ).setDebug( )
	inlineAttributeStrict = '@' + inlineAttribute
	inlineAttributePositional = inlineExpression.copy( ).setParseAction( insert_token( '@positional' ) )

	startStatement = pyparsing.Empty( ).setParseAction( lambda s, loc, toks: loc )
	endStatement = pyparsing.OneOrMore( pyparsing.LineEnd( ).suppress( ) )

	def statement( body ):
		return startStatement + body + endStatement

	def inline_statements( body ):
		statement = startStatement + body
		return pyparsing.Group( statement ) + pyparsing.ZeroOrMore( pyparsing.Group( statement ) )

	definitionInline = inlineAttributeExpansion | inlineAttributeLoose
	definitionInline.setName( 'definitionInline' ).setDebug( )
	definitionInlines = inline_statements( definitionInline )
	definitionInlines.setName( 'definitionInlines' ).setDebug( )
	elementInline = inlineNamespace | definitionInline
	elementInline.setName( 'elementInline' ).setDebug( )
	elementInlines = inline_statements( elementInline )
	elementInlines.setName( 'elementInlines' ).setDebug( )
	expansionInline = inlineNamespace | inlineAttributeExpansion | inlineAttributeStrict | inlineAttributePositional
	expansionInlines = inline_statements( expansionInline )

	doctype = '<!' - pyparsing.Literal( 'DOCTYPE' ) - expression
	comment = '!' - expression
	processing = '<?' - ( namedExpression | nameExpression )
	namespace = '#' - pyparsing.Optional( namedExpression | expression )
	attributeExpansion = '@@' - nameExpression
	attribute = '@' - ( namedExpression | nameExpression )
	text = '"' - expression
	elementWithInline = inlineNameExpression + elementInlines
	elementWithInline.setName( 'elementWithInline' ).setDebug( )
	elementWithExpression = nameExpression
	elementWithExpression.setName( 'elementWithExpression' ).setDebug( )
	element = '<' + ( elementWithInline | elementWithExpression )
	element.setName( 'element' ).setDebug( )
	elementExpansionWithExpression = nameExpression
	elementExpansionWithInline = inlineNameExpression + expansionInlines
	elementExpansion = elementExpansionWithInline | elementExpansionWithExpression 
	elementExpansion.setParseAction( insert_token( '<<' ) )

	def start_command( command ):
		return ( pyparsing.Literal( '?' ) +
			command +
			pyparsing.Empty( ) )

	restartIndentation = start_command( 'indent' ) + pyparsing.Literal( 'restart' ).setParseAction( push_indent )
	resumeIndentation = start_command( 'indent' ) + pyparsing.Literal( 'resume' ).setParseAction( pop_indent )
	load = start_command( 'load' ) - expression
	encoding = start_command( 'encoding' ) - expression
	default = start_command( 'default' ) - expression
	variable = start_command( 'variable' ) - ( namedExpression | nameExpression )
	contents = start_command( 'contents' ) - pyparsing.Optional( pyparsing.Literal( '!' ) | '<?' | '@' | '#' | '"' | '<' | '?', default = 'all' )
	attributeDefinition = start_command( 'attribute' ) - nameExpression
	elementDefinitionWithInline = inlineNameExpression + definitionInlines
	elementDefinitionWithExpression = nameExpression
	elementDefinition = start_command( 'element' ) - ( elementDefinitionWithInline | elementDefinitionWithExpression )

	def create_single_block( simpleStatements, compound ):
		block = addons.indentedBlock( simpleStatements, aIndentations )
		block.setName( 'single-block' ).setDebug( )
		block.setParseAction( lambda s, loc, toks: toks[ 0 ] )
		compoundStatement = statement( compound ) + pyparsing.Optional( block )
		return compoundStatement

	def create_block( simpleStatements, compound ):
		block = pyparsing.Forward( )
		block.setName( 'block' ).setDebug( )
		compoundStatement = statement( compound ) + pyparsing.Optional( block )
		contentStatement = compoundStatement | simpleStatements
		block << addons.indentedBlock( contentStatement, aIndentations )
		block.setParseAction( lambda s, loc, toks: toks[ 0 ] )
		return compoundStatement

	simple = statement( comment | processing | namespace | attributeExpansion | attribute | text | restartIndentation | resumeIndentation | default | variable | contents )
	simple.setName( 'simple' ).setDebug( )
	compound = element | elementExpansion
	compound.setName( 'compound' ).setDebug( )
	elementStatement = create_block( simple, compound )
	elementStatement.setName( 'elementStatement' ).setDebug( )

	simple = statement( namespace | attributeExpansion | attribute )
	attributeDefinitionStatement = create_single_block( simple, attributeDefinition )

	simple = statement( attribute  ) | elementStatement
	elementDefinitionStatement = create_single_block( simple, elementDefinition )

	commandStatements = pyparsing.Group( statement( load | encoding | default | variable ) | attributeDefinitionStatement | elementDefinitionStatement )
	commandStatements.setName( 'commandStatement' ).setDebug( )
	doctypeStatements = pyparsing.Group( statement( doctype ) )
	doctypeStatements.setName( 'doctypeStatement' ).setDebug( )
	rootStatements = pyparsing.Group( statement( processing | comment ) | elementStatement )
	rootStatements.setName( 'rootStatement' ).setDebug( )

	grammar = (
		pyparsing.Optional( endStatement ) + 
		pyparsing.ZeroOrMore( addons.checkIndent( aIndentations ) + commandStatements ) + 
		pyparsing.Optional( addons.checkIndent( aIndentations ) + doctypeStatements ) + 
		pyparsing.OneOrMore( addons.checkIndent( aIndentations ) + rootStatements ) + 
		pyparsing.StringEnd( )
		)

	addons.set_whitespace( grammar, ' \t' )
	grammar.parseWithTabs( )

	return grammar
