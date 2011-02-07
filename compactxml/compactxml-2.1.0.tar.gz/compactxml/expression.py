#!/usr/bin/python -tt

from __future__ import absolute_import

import re, copy

from lxml import etree
import pyparsing

from .error import ExpandError

xmlName = pyparsing.Regex( r'[_\w][-_.\w]*', re.U )( 'name' )
prefix = xmlName( 'prefix' )
prefixedName = pyparsing.Optional( prefix + pyparsing.Literal( ':' ).suppress( ) ) + xmlName

aDefaultNamespaces = {
	'xml' : 'http://www.w3.org/XML/1998/namespace',
	'xmlns' : 'http://www.w3.org/2000/xmlns',
	}

class Expression( object ):
	def __init__( self, aParts, aNamespaces, aVariables ):
		assert len( aParts ) % 2 == 0, 'All expression parts must have an operator and value.'
		self.aParts = aParts
		self.aNamespaces = aNamespaces
		self.aVariables = aVariables

	def __iter__( self ):
		aParts = copy.copy( self.aParts.asList( ) )
		aParts.reverse( )
		while True:
			try:
				operator = aParts.pop( )
				value = aParts.pop( )
			except IndexError:
				break

			yield operator, value

	def value( self ):
		combined = ''
		for operator, value in self:
			if operator == '+':
				combined += value
			elif operator == '\\':
				combined += '\n'
				combined += value
			elif operator == '$':
				combined += self.aVariables.lookup( value )

		return combined

	def parse_prefixed_name( self, unparsed ):
		try:
			return prefixedName.parseString( unparsed, True )
		except pyparsing.ParseException, exception:
			error = ExpandError( 'Error parsing name in expression: ' + exception.msg )
			raise error

	def parse_prefix( self, unparsed ):
		try:
			return prefix.parseString( unparsed, True )
		except pyparsing.ParseException, exception:
			error = ExpandError( 'Error parsing prefix in expression: ' + exception.msg )
			raise error

	def name( self ):
		parsed = self.parse_prefixed_name( self.value( ) )

		name = parsed[ 'name' ]
		try:
			prefix = parsed[ 'prefix' ]
		except KeyError:
			return name
		else:
			return prefix + ':' + name

	def qname( self ):
		global aDefaultNamespaces

		parsed = self.parse_prefixed_name( self.value( ) )
		name = parsed[ 'name' ]
		try:
			prefix = parsed[ 'prefix' ]
		except KeyError:
			try:
				namespace = self.aNamespaces[ None ]
			except KeyError:
				return etree.QName( name )
		else:
			try:
				namespace = aDefaultNamespaces[ prefix ]
			except KeyError:
				namespace = self.aNamespaces[ prefix ]

		if namespace:
			return etree.QName( namespace, name )
		else:
			return etree.QName( name )

	def prefix( self ):
		parsed = self.parse_prefix( self.value( ) )
		parsedPrefix = parsed[ 'prefix' ]
		return parsedPrefix

	def attribute( self ):
		global aDefaultNamespaces

		parsed = self.parse_prefixed_name( self.value( ) )
		name = parsed[ 'name' ]
		try:
			prefix = parsed[ 'prefix' ]
		except KeyError:
			# Attributes ignore default namespace.
			return etree.QName( name )
		else:
			try:
				namespace = aDefaultNamespaces[ prefix ]
			except KeyError:
				namespace = self.aNamespaces[ prefix ]

			if namespace:
				return etree.QName( namespace, name )
			else:
				return etree.QName( name )

	@staticmethod
	def build( command, value, aVariables ):
		# Split on newlines. Name values should never contain any, so
		# safe to always do.
		aaParts = []
		for eOperator, eValue in aVariables.partition( value ):
			if eOperator == '+':
				for ePart in eValue.split( '\n' ):
					aaParts.append( ( eOperator, ePart ) )
					eOperator = '\\'
			else:
				aaParts.append( ( eOperator, eValue ) )

		# Insert command at beginning of parts.
		if aaParts[ 0 ][ 0 ] == '+':
			aaParts[ 0 ] = ( command, aaParts[ 0 ][ 1 ] )
		else:
			aaParts.insert( 0, ( command, u'' ) )

		# Quote parts with whitespace. Also should never appear in
		# names.
		def quote( value ):
			if ' ' in value or '\t' in value or '"' in value:
				return '"%s"' % value.replace( '"', '""' )
			else:
				return value

		aaParts = map( lambda ( eOperator, eValue ): ( eOperator, quote( eValue ) ), aaParts )

		# Join commands and values into lines.
		aLines = map( lambda aParts: ''.join( aParts ), aaParts )

		return aLines

class NamedExpression( object ):
	def __init__( self, aParts, aNamespaces, aVariables ):
		if len( aParts ) == 0:
			self.nameExpression = None
			self.valueExpression = None
		elif len( aParts ) == 1:
			self.nameExpression = Expression( aParts[ 0 ], aNamespaces, aVariables )
			self.valueExpression = None
		elif len( aParts ) == 3:
			self.nameExpression = Expression( aParts[ 0 ], aNamespaces, aVariables )
			assert aParts[ 1 ] == '=', 'Named expression must contain equal sign.'
			self.valueExpression = Expression( aParts[ 2 ], aNamespaces, aVariables )
		else:
			assert False, 'Wrong number of parts (%d) for named expression.' % len( aParts )

	def value( self ):
		if self.valueExpression is None:
			return None
		else:
			return self.valueExpression.value( )

	def __parse_name( self, method ):
		if self.nameExpression is None:
			return None
		else:
			return getattr( self.nameExpression, method )( )

	def name( self ):
		return self.__parse_name( 'name' )

	def qname( self ):
		return self.__parse_name( 'qname' )

	def prefix( self ):
		return self.__parse_name( 'prefix' )

	def attribute( self ):
		return self.__parse_name( 'attribute' )

	@staticmethod
	def build( command, name, value, aVariables ):
		aNameLines = Expression.build( command, name, aVariables )
		aValueLines = Expression.build( '=', value, aVariables )

		aNameLines[ -1 ] = aNameLines[ -1 ] + aValueLines[ 0 ]
		aNameLines.extend( aValueLines[ 1 : ] )
		return aNameLines
