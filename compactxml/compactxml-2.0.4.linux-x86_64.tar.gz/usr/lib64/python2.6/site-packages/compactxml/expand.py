#!/usr/bin/python -tt

from __future__ import absolute_import

import re, copy

from lxml import etree
import pyparsing

from .namespace import Namespaces, UndefinedPrefix
from .variable import Variables
from .macro import Macros
from .expression import Expression, NamedExpression
from .error import ExpandError
from .grammar import create_grammar
from .parser import Parser

class NamespaceLookahead( Parser ):
	def parse( self, scope, aNamespaces, aVariables, aMacros ):
		self.aNamespaces = copy.copy( aNamespaces )
		Parser.parse( self, scope, self.aNamespaces, aVariables, aMacros )
		return self.aNamespaces

	def attribute( self, statement, aNamespaces, aVariables, aMacros ):
		try:
			name, value = self.parse_attribute( statement, aNamespaces, aVariables, aMacros )
		except UndefinedPrefix:
			# Ignore the attribute if it's in an unknown
			# namespace, it can't possibly be a namespace
			# declaration.
			pass
		else:
			# Recognize literal namespace declarations.
			if aNamespaces.is_namespace_prefix( name.namespace ):
				if value is None:
					value = aVariables.default

				self.aNamespaces[ name.localname ] = value

	def namespace( self, statement, aNamespaces, aVariables, aMacros ):
		prefix, value = self.parse_namespace( statement, aNamespaces, aVariables, aMacros )

		self.aNamespaces[ prefix ] = value

class AttributeLookahead( Parser ):
	def parse( self, scope, aNamespaces, aVariables, aMacros ):
		self.aAttributes = {}
		Parser.parse( self, scope, aNamespaces, aVariables, aMacros )
		return self.aAttributes

	def attribute( self, statement, aNamespaces, aVariables, aMacros ):
		name, value = self.parse_attribute( statement, aNamespaces, aVariables, aMacros )
		if value is None:
			value = aVariables.default

		self.aAttributes[ name ] = value

class DefinitionLookahead( Parser ):
	def parse( self, scope, aNamespaces, aVariables, aMacros ):
		self.aParameters = []
		self.aElements = []
		Parser.parse( self, scope, aNamespaces, aVariables, aMacros )
		return self.aParameters, self.aElements

	def attribute( self, statement, aNamespaces, aVariables, aMacros ):
		name, value = self.parse_attribute( statement, aNamespaces, aVariables, aMacros )
		# value will be None if no default value is specified.
		self.aParameters.append( ( name, value ) )

	def default( self, statement, aNamespaces, aVariables, aMacros ):
		self.aElements.append( statement )

class ExpansionLookahead( Parser ):
	class UndefinedPositionalParameter( IndexError ):
		def __init__( self, cPositional ):
			self.cPositional = cPositional
			IndexError.__init__( self, str( self ) )

		def __str__( self ):
			return 'More positional parameters given than the %d defined.' % self.cPositional

	def parse( self, scope, aNamespaces, aVariables, aMacros, aParameters, expansionSource ):
		self.aParametersLookup = dict( ( name, value ) for name, value in aParameters )
		self.aPositional = []
		self.aNamed = {}
		self.aContents = []

		Parser.parse( self, scope, aNamespaces, aVariables, aMacros )

		# Assign remaining names to positional values.
		aPositionalNames = [ name for name, value in aParameters if name not in self.aNamed ]
		cPositional = len( aPositionalNames )
		for ePositional in self.aPositional:
			try:
				name = aPositionalNames.pop( 0 )
			except IndexError:
				raise self.UndefinedPositionalParameter( cPositional )
			self.aNamed[ name ] = ePositional

		# Assign defaults to unspecified names.
		for name in aPositionalNames:
			value = self.aParametersLookup[ name ]
			# But, don't include name if no default was defined.
			if value is not None:
				self.aNamed[ name ] = value

		aVariables = aVariables.new_scope( self.aNamed, expansionSource )
		aVariables.contents = self.aContents
		return aVariables

	def attribute( self, statement, aNamespaces, aVariables, aMacros ):
		expression = NamedExpression( statement[ 2 : ], aNamespaces, aVariables )
		name = expression.name( )
		value = expression.value( )

		if name in self.aParametersLookup:
			if value is None:
				value = self.aParametersLookup[ name ]
				if value is None:
					value = aVariables.default

			self.aNamed[ name ] = value
		else:
			self.aContents.append( statement )

	def positional( self, statement, aNamespaces, aVariables, aMacros ):
		value = Expression( statement[ 2 ], aNamespaces, aVariables ).value( )
		self.aPositional.append( value )

	def default( self, statement, aNamespaces, aVariables, aMacros ):
		self.aContents.append( statement )

class BodyParser( Parser ):
	def parse( self, scope, aNamespaces, aVariables, aMacros, tree ):
		self.aCreated = []
		Parser.parse( self, scope, aNamespaces, aVariables, aMacros, tree )
		return self.aCreated

	def element( self, statement, aNamespaces, aVariables, aMacros, tree ):
		# Namespaces and attributes must be evaluated out of order in
		# order to create XML element before iterating into deeper
		# scopes.
		aElementNamespaces = NamespaceLookahead( ).parse( statement[ 3 : ], aNamespaces, aVariables, aMacros )
		aAttributes = AttributeLookahead( ).parse( statement[ 3 : ], aElementNamespaces, aVariables, aMacros )
		name = Expression( statement[ 2 ], aElementNamespaces, aVariables ).qname( )

		tree.start( name, aAttributes, nsmap = aElementNamespaces.nsmap( ) )
		BodyParser( ).parse( statement[ 3 : ], aElementNamespaces, aVariables, aMacros, tree )
		self.aCreated.append( tree.end( name ) )

	def element_expansion( self, statement, aNamespaces, aVariables, aMacros, tree ):
		name = Expression( statement[ 2 ], aNamespaces, aVariables ).name( )
		aDefinedParameters, aElements, expansionSource = aMacros.element( name )
		try:
			aExpansionVariables = ExpansionLookahead( ).parse( statement[ 3 : ], aNamespaces, aVariables, aMacros, aDefinedParameters, expansionSource )
			aCreatedInNestedScope = BodyParser( ).parse( aElements, aNamespaces, aExpansionVariables, aMacros, tree )
		except ExpansionLookahead.UndefinedPositionalParameter, exception:
			raise ExpandError( unicode( exception ), exception )
		except ExpandError, exception:
			exception.bind_name( name )
			exception.bind_source( expansionSource )
			raise
		self.aCreated.extend( aCreatedInNestedScope )

	def text( self, statement, aNamespaces, aVariables, aMacros, tree ):
		value = Expression( statement[ 2 ], aNamespaces, aVariables ).value( )
		tree.data( value )

	def comment( self, statement, aNamespaces, aVariables, aMacros, tree ):
		value = Expression( statement[ 2 ], aNamespaces, aVariables ).value( )
		self.aCreated.append( tree.comment( value ) )

	def processing_instruction( self, statement, aNamespaces, aVariables, aMacros, tree ):
		namedExpression = NamedExpression( statement[ 2 : ], aNamespaces, aVariables )
		# Colons are illegal in PI names, so restrict using
		# the same rules as for namespace prefixes.
		name = namedExpression.prefix( )
		value = namedExpression.value( )
		self.aCreated.append( tree.pi( name, value ) )

	def attribute_default( self, statement, aNamespaces, aVariables, aMacros, tree ):
		default = Expression( statement[ 3 ], aNamespaces, aVariables ).value( )
		aVariables.default = default

	def variable( self, statement, aNamespaces, aVariables, aMacros, tree ):
		variableExpression = NamedExpression( statement[ 3 : ], aNamespaces, aVariables )
		name = variableExpression.name( )
		value = variableExpression.value( )
		if value is None:
			value = u''
		aVariables.set_global( name, value )

class TopParser( BodyParser ):
	def parse( self, scope, aNamespaces, aVariables, aMacros, tree ):
		self.documentType = None
		aCreated = BodyParser.parse( self, scope, aNamespaces, aVariables, aMacros, tree )
		return self.documentType, aCreated

	def doctype( self, statement, aNamespaces, aVariables, aMacros, tree ):
		self.documentType = Expression( statement[ 3 ], aNamespaces, aVariables ).value( )

	def load( self, statement, aNamespaces, aVariables, aMacros, tree ):
		location = Expression( statement[ 3 ], aNamespaces, aVariables ).value( )
		from . import resolve
		resolved = resolve( location )
		assert isinstance( resolved, basestring )
		aNewMacros = load_macros( resolved, aNamespaces.nsmap( ), aVariables.aGlobals, aMacros )
		aMacros.update( aNewMacros )

	def encoding( self, statement, aNamespaces, aVariables, aMacros, tree ):
		encoding = Expression( statement[ 3 ], aNamespaces, aVariables ).value( )
		aVariables.encoding = encoding

	def attribute_definition( self, statement, aNamespaces, aVariables, aMacros, tree ):
		name = Expression( statement[ 3 ], aNamespaces, aVariables ).name( )
		aMacros.add_attribute( name, statement[ 4 : ], aVariables.source )

	def element_definition( self, statement, aNamespaces, aVariables, aMacros, tree ):
		name = Expression( statement[ 3 ], aNamespaces, aVariables ).name( )

		aParameters, aElements = DefinitionLookahead( ).parse( statement[ 4 : ], aNamespaces, aVariables, aMacros )
		aMacros.add_element( name, aParameters, aElements, aVariables.source )

	def default( self, statement, aNamespaces, aVariables, aMacros, tree ):
		raise NotImplementedError( statement )

class LoadParser( Parser ):
	def variable( self, statement, aNamespaces, aVariables, aMacros ):
		variableExpression = NamedExpression( statement[ 3 : ], aNamespaces, aVariables )
		name = variableExpression.name( )
		value = variableExpression.value( )
		if value is None:
			value = u''
		aVariables.set_global( name, value )

	def attribute_definition( self, statement, aNamespaces, aVariables, aMacros ):
		name = Expression( statement[ 3 ], aNamespaces, aVariables ).name( )
		aMacros.add_attribute( name, statement[ 4 : ], aVariables.source )

	def element_definition( self, statement, aNamespaces, aVariables, aMacros ):
		name = Expression( statement[ 3 ], aNamespaces, aVariables ).name( )

		aParameters, aElements = DefinitionLookahead( ).parse( statement[ 4 : ], aNamespaces, aVariables, aMacros )
		aMacros.add_element( name, aParameters, aElements, aVariables.source )

def setup( compacted, namespaces, variables, macros ):
	# Create per call for thread safety.
	grammar = create_grammar( )
	try:
		parsed = grammar.parseString( compacted, True )
	except pyparsing.ParseException, exception:
		error = ExpandError( exception.msg, exception )
		error.bind_location( exception.loc )
		error.bind_source( compacted )
		raise error
	#print 'Parsed:', parsed

	aMacros = Macros( ) if macros is None else copy.copy( macros )
	aVariables = Variables( variables ).new_scope( {}, compacted )
	aNamespaces = Namespaces( namespaces )
	return parsed, aMacros, aVariables, aNamespaces

def load_macros( compacted, namespaces = {}, variables = {}, macros = None ):
	parsed, aMacros, aVariables, aNamespaces = setup( compacted, namespaces, variables, macros )
	try:
		LoadParser( ).parse( parsed, aNamespaces, aVariables, aMacros )
	except ExpandError, exception:
		exception.bind_source( compacted )
		raise
	return aMacros

def expand( compacted, namespaces = {}, variables = {}, macros = None ):
	parsed, aMacros, aVariables, aNamespaces = setup( compacted, namespaces, variables, macros )
	tree = etree.TreeBuilder( )
	try:
		documentType, aCreated = TopParser( ).parse( parsed, aNamespaces, aVariables, aMacros, tree )
	except ExpandError, exception:
		exception.bind_source( compacted )
		raise
	lastElement = tree.close( )

	if len( aCreated ) == 1 and not documentType:
		tree = lastElement.getroottree( )
	elif not documentType:
		aBefore = []
		rootElement = None
		aAfter = []
		for ePart in aCreated:
			if isinstance( ePart, etree._Comment ) or isinstance( ePart, etree._ProcessingInstruction ):
				if rootElement is None:
					aBefore.append( ePart )
				else:
					aAfter.append( ePart )
			else:
				assert isinstance( ePart, etree._Element )
				if rootElement is None:
					rootElement = ePart
				else:
					raise ValueError( 'XML document must have exactly one root element.' )

		if rootElement is None:
			raise ValueError( 'XML document must have exactly one root element.' )

		while aBefore:
			rootElement.addprevious( aBefore.pop( ) )

		aAfter.reverse( )
		while aAfter:
			rootElement.addnext( aAfter.pop( ) )

		tree = rootElement.getroottree( )
	else:
		aCreatedParts = [ etree.tostring( ePart ) for ePart in aCreated ]
		if documentType:
			doctypePart = '<!DOCTYPE %s>' % documentType
			aCreatedParts = [ doctypePart ] + aCreatedParts
		tree = etree.fromstring( ''.join( aCreatedParts ) ).getroottree( )

	return aVariables.encoding, tree
