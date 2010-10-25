#!/usr/bin/python -tt

import copy

class RestrictedNamespace( ValueError ):
	pass

class RestrictedPrefix( RestrictedNamespace ):
	pass

class UndefinedPrefix( KeyError ):
	def __init__( self, prefix ):
		self.prefix = prefix
		KeyError.__init__( self, unicode( self ) )

	def __unicode__( self ):
		return u'No namespace defined for prefix "%s".' % self.prefix

# Some common namespaces.
XML = 'http://www.w3.org/XML/1998/namespace'
XML_NAMESPACE = 'http://www.w3.org/2000/xmlns'
TRANSFORM = 'http://www.w3.org/1999/XSL/Transform'
SCHEMA = 'http://www.w3.org/2001/XMLSchema'
SCHEMA_INSTANCE = 'http://www.w3.org/2001/XMLSchema-instance'
RELAXNG = 'http://relaxng.org/ns/structure/1.0'
XHTML = 'http://www.w3.org/1999/xhtml'

class Namespaces( object ):

	XML_RESTRICTED = {
		'xml' : XML,
		'xmlns' : XML_NAMESPACE,
		}
	XML_RESTRICTED_PREFIXES = set( XML_RESTRICTED.keys( ) )
	XML_RESTRICTED_NAMESPACES = set( XML_RESTRICTED.values( ) )

	def __init__( self, *args, **kwargs ):
		self.__aNamespaces = dict( *args, **kwargs )
		for ePrefix, eNamespace in self.__aNamespaces.items( ):
			self.check_valid( ePrefix, eNamespace )

	def __copy__( self ):
		copied = Namespaces( )
		# Avoid rechecking for validity on copy.
		copied.__aNamespaces = self.__aNamespaces.copy( )
		return copied

	@classmethod
	def check_valid( cls, prefix, namespace ):
		if prefix in cls.XML_RESTRICTED_PREFIXES:
			raise RestrictedPrefix( u'Prefix %s restricted by XML.' % prefix )

		if namespace in cls.XML_RESTRICTED_NAMESPACES:
			raise RestrictedNamespace( u'Namespace %s restricted by XML.' % namespace )

	@staticmethod
	def is_namespace_prefix( namespace ):
		return namespace == XML_NAMESPACE

	def __setitem__( self, prefix, namespace ):
		self.check_valid( prefix, namespace )
		self.__aNamespaces[ prefix ] = namespace

	def __getitem__( self, prefix ):
		try:
			return self.XML_RESTRICTED[ prefix ]
		except KeyError:
			try:
				return self.__aNamespaces[ prefix ]
			except KeyError:
				raise UndefinedPrefix( prefix )

	def is_defined( self, prefix, namespace ):
		try:
			return self.__aNamespaces[ prefix ] == namespace
		except KeyError:
			return False

	def nsmap( self ):
		return self.__aNamespaces
