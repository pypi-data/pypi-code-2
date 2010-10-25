#!/usr/bin/python -tt

import copy

class UndefinedVariable( KeyError ):
	pass

class Variables( object ):
	def __init__( self, initialState = {} ):
		self.aGlobals = initialState.copy( )
		self.aGlobalDefaults = {}
		self.aLocals = {}

		# Additional parse state, not really variables, but a
		# convenient place to stick these.
		self.contents = []
		self.encoding = 'UTF-8'
		self.default = ''
		self.aSources = []

	def __str__( self ):
		return '<variable.Variables instance with %d globals, %d defaults and %d locals>' % ( len( self.aGlobals ), len( self.aGlobalDefaults ), len( self.aLocals ) )

	def __repr__( self ):
		return '<variable.Variables instance %r globals, %r defaults  and %r locals and %r default value>' % ( self.aGlobals, self.aGlobalDefaults, self.aLocals, self.default )

	def __copy__( self ):
		variables = Variables( )
		variables.aGlobals = self.aGlobals
		variables.aGlobalDefaults = self.aGlobalDefaults
		variables.default = self.default
		variables.aSources = copy.copy( self.aSources )
		return variables

	def __len__( self ):
		return len( self.aGlobals ) + len( self.aLocals )

	def set_global( self, name, value ):
		self.aGlobalDefaults[ name ] = value

	def set_local( self, name, value ):
		self.aLocals[ name ] = value

	def new_scope( self, localsToAdd, sourceForScope ):
		variables = copy.copy( self )
		variables.aLocals.update( localsToAdd )
		variables.aSources.append( sourceForScope )
		return variables

	@property
	def source( self ):
		return self.aSources[ -1 ]

	def __merged( self ):
		aInScope = self.aGlobalDefaults.copy( )
		aInScope.update( self.aGlobals )
		aInScope.update( self.aLocals )
		return aInScope

	def lookup( self, name ):
		try:
			return self.__merged( )[ name ]
		except KeyError:
			raise UndefinedVariable( name )

	def keys( self ):
		return self.__merged( ).keys( )

	def values( self ):
		return self.__merged( ).values( )

	def items( self ):
		return self.__merged( ).items( )

	def partition( self, value ):
		aMatched = []
		for eName, eVariable in self.items( ):
			if eVariable in value:
				aMatched.append( ( eName, eVariable ) )

		aaCurrentParts = [ [ '+', value ] ]
		aMatched.sort( key = lambda ( name, value ): -len( value ) )
		for eName, eMatched in aMatched:
			aaParts = []
			for eOperator, eValue in aaCurrentParts:
				if eOperator == '+':
					while eMatched in eValue:
						textPart, variablePart, eValue = eValue.partition( eMatched )
						if textPart:
							aaParts.append( ( '+', textPart ) )
						aaParts.append( ( '$', eName ) )

					if eValue:
						aaParts.append( ( '+', eValue ) )
				else:
					aaParts.append( ( eOperator, eValue ) )

			aaCurrentParts = aaParts

		return aaCurrentParts
