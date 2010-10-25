#!/usr/bin/python -tt

from __future__ import absolute_import

from lxml import etree
import pyparsing

from . import pyparsingaddons as addons

class ParsingError( Exception ):
	def __init__( self, message, rawException = None ):
		Exception.__init__( self, message )
		self.message = message
		self.raw = rawException

	def __unicode__( self ):
		return u'Parsing error: %s' % self.message

	def __str__( self ):
		return unicode( self ).encode( 'UTF-8' )

class ExpandError( ParsingError ):
	def __init__( self, message, rawException = None ):
		ParsingError.__init__( self, message, rawException )

		self.aStack = []
		self.scopeLocation = None
		self.scopeName = None

	def bind_name( self, name ):
		if self.scopeName is None:
			self.scopeName = name

	def bind_location( self, location ):
		if self.scopeLocation is None:
			self.scopeLocation = location

	def bind_source( self, source ):
		assert self.scopeLocation is not None
		self.aStack.append( ( source, self.scopeName, self.scopeLocation ) )

		self.scopeName = None
		self.scopeLocation = None

	@property
	def source( self ):
		return self.aStack[ 0 ][ 0 ]

	@property
	def name( self ):
		return self.aStack[ 0 ][ 1 ]

	@property
	def location( self ):
		return self.aStack[ 0 ][ 2 ]

	@property
	def line( self ):
		return pyparsing.lineno( self.location, self.source )

	@property
	def sourceLine( self ):
		return addons.line( self.location, self.source )

	def __unicode__( self ):
		error = u'Error parsing compact XML for expansion:\n'
		for eTrace in self.aStack[ : : -1 ]:
			source, name, location = eTrace
			line = pyparsing.lineno( location, source )
			sourceLine = addons.line( location, source )
			if name:
				error += u'  Line %d (char:%d), from %r:\n' % ( line, location, name )
			else:
				error += u'  Line %d (char:%d), from document:\n' % ( line, location )
			error += u'    %s\n' % sourceLine.lstrip( )
		error += self.message
		return error

	def __str__( self ):
		return unicode( self ).encode( 'UTF-8' )

class CompactError( ParsingError ):
	def __init__( self, sourceFile, rawException ):
		assert isinstance( rawException, etree.ParseError )
		message = rawException.msg
		ParsingError.__init__( self, message, rawException )
		self.name = rawException.filename
		self.location = rawException.position
		self.line = rawException.position[ 0 ]

		sourceFile.seek( 0 )
		self.source = sourceFile.read( )

	@property
	def sourceLine( self ):
		return self.source.splitlines( )[ self.line - 1 ]

	def __unicode__( self ):
		error = u'Error parsing XML for compaction:\n'
		if self.name:
			error += u'  Line %d, from %r:\n' % ( self.line, self.name )
		else:
			error += u'  Line %d, from document:\n' % ( self.line )
		error += u'    %s\n' % self.sourceLine.lstrip( )
		error += self.message
		return error

	def __str__( self ):
		return unicode( self ).encode( 'UTF-8' )
