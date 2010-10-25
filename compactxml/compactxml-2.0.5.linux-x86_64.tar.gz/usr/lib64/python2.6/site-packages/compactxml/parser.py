#!/usr/bin/python -tt

from __future__ import absolute_import

import pyparsing

from .expression import Expression, NamedExpression
from .variable import UndefinedVariable
from .macro import UndefinedMacro
from .namespace import UndefinedPrefix
from .error import ExpandError

class Parser( object ):
	class UnknownStatement( ExpandError ):
		pass

	class UnknownCommand( ExpandError ):
		pass

	def default( self, *args ):
		pass

	def __getattr__( self, name ):
		return self.default

	def parse( self, scope, aNamespaces, aVariables, aMacros, *args ):
		parseArguments = [ aNamespaces, aVariables, aMacros ] + list( args )
		for statement in scope:
			location = statement[ 0 ]
			type = statement[ 1 ]
			try:
				if type == '<!':
					assert len( statement ) == 4
					assert statement[ 2 ] == 'DOCTYPE'
					self.doctype( statement, *parseArguments )
				elif type == '<':
					assert len( statement ) >= 3
					self.element( statement, *parseArguments )
				elif type == '<<':
					assert len( statement ) >= 3
					self.element_expansion( statement, *parseArguments )
				elif type == '"':
					assert len( statement ) == 3
					self.text( statement, *parseArguments )
				elif type == '!':
					assert len( statement ) == 3
					self.comment( statement, *parseArguments )
				elif type == '<?':
					assert len( statement ) in ( 3, 5 )
					self.processing_instruction( statement, *parseArguments )
				elif type == '#':
					assert len( statement ) in ( 2, 3, 5 )
					self.namespace( statement, *parseArguments )
				elif type == '@':
					assert len( statement ) in ( 3, 5 )
					self.attribute( statement, *parseArguments )
				elif type == '@positional':
					assert len( statement ) == 3
					self.positional( statement, *parseArguments )
				elif type == '@@':
					assert len( statement ) == 3
					name = Expression( statement[ 2 ], aNamespaces, aVariables ).name( )
					expansion, expansionSource = aMacros.attribute( name )
					try:
						Parser.parse( self, expansion, *parseArguments )
					except ExpandError, exception:
						exception.bind_name( name )
						exception.bind_source( expansionSource )
						raise
				elif type == '?':
					assert len( statement ) >= 3

					command = statement[ 2 ]
					if command == 'indent':
						assert len( statement ) == 4
						action = statement[ 3 ]
						if action == 'restart':
							self.restart_indentation( statement, *parseArguments )
						elif action == 'resume':
							self.resume_indentation( statement, *parseArguments )
						else:
							assert False
					elif command == 'load':
						assert len( statement ) == 4
						self.load( statement, *parseArguments )
					elif command == 'encoding':
						assert len( statement ) == 4
						self.encoding( statement, *parseArguments )
					elif command == 'default':
						assert len( statement ) == 4
						self.attribute_default( statement, *parseArguments )
					elif command == 'variable':
						assert len( statement ) in ( 4, 6 )
						self.variable( statement, *parseArguments )
					elif command == 'contents':
						assert len( statement ) == 4
						expansion = aVariables.contents
						filter = statement[ 3 ]
						if filter <> 'all':
							expansion = FilterLookahead( filter ).parse( expansion, aNamespaces, aVariables, aMacros )
						Parser.parse( self, expansion, *parseArguments )
					elif command == 'attribute':
						assert len( statement ) >= 4
						self.attribute_definition( statement, *parseArguments )
					elif command == 'element':
						assert len( statement ) >= 4
						self.element_definition( statement, *parseArguments )
					else:
						raise self.UnknownCommand( 'Unknown command %r.' % command, location )
				else:
					raise self.UnknownStatement( 'Unknown statement type %r.' % type, location )
			except UndefinedVariable:
				pass
			except ExpandError, exception:
				exception.bind_location( location )
				raise
			except UndefinedMacro, exception:
				error = ExpandError( unicode( exception ), exception )
				error.bind_location( location )
				raise error
			except UndefinedPrefix, exception:
				error = ExpandError( unicode( exception ), exception )
				error.bind_location( location )
				raise error
			except pyparsing.ParseException, exception:
				error = ExpandError( exception.msg )
				error.bind_location( exception.loc )
				raise error

	def parse_attribute( self, statement, aNamespaces, aVariables, aMacros ):
		expression = NamedExpression( statement[ 2 : ], aNamespaces, aVariables )
		name = expression.attribute( )
		value = expression.value( )
		return name, value

	def parse_namespace( self, statement, aNamespaces, aVariables, aMacros ):
		if len( statement ) == 2:
			prefix = None
			value = u''
		elif len( statement ) == 3:
			prefix = None
			value = Expression( statement[ 2 ], aNamespaces, aVariables ).value( )
		elif len( statement ) == 5:
			expression = NamedExpression( statement[ 2 : ], aNamespaces, aVariables )
			prefix = expression.prefix( )
			value = expression.value( )

		return prefix, value

class FilterLookahead( Parser ):
	def __init__( self, filter ):
		self.filter = filter
		self.aAliases = {
			'<<' : '<'
			}

	def parse( self, scope, aNamespaces, aVariables, aMacros ):
		self.aContents = []
		Parser.parse( self, scope, aNamespaces, aVariables, aMacros )
		return self.aContents

	def default( self, statement, aNamespaces, aVariables, aMacros ):
		type = statement[ 1 ]
		type = self.aAliases.get( type, type )
		if type == self.filter:
			self.aContents.append( statement )
