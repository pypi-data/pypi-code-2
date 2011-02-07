#!/usr/bin/python -tt

from __future__ import absolute_import

import copy, re

from lxml import etree

from .expression import Expression, NamedExpression
from .namespace import Namespaces
from .variable import Variables, UndefinedVariable
from .macro import Macros
from .error import CompactError

matchDoctype = re.compile( r'^<!DOCTYPE\s(?P<doctype>.*)>$', re.UNICODE )

def compact( xmlFile, namespaces = {}, variables = {}, macros = None, stripText = False ):
	aMacros = Macros( ) if macros is None else copy.copy( macros )
	aVariables = Variables( variables )
	aNamespaces = Namespaces( namespaces )

	cIndent = 0
	aNamespaceStack = []
	aaNewNamespaceDeclarations = []
	aPreviousNamespacePrefixes = set( )
	compactedHeader = ''
	compacted = ''

	def indent( ):
		return cIndent * '\t'

	def add_lines( aLines ):
		compacted = ''
		for eLine in aLines:
			compacted += indent( )
			compacted += eLine
			compacted += '\n'

		return compacted

	def stripped( value ):
		if value is None:
			return ''

		if stripText:
			return value.strip( )
		else:
			return value

	def prefixed_name( name ):
		qname = etree.QName( name )
		if qname.namespace:
			for prefix, namespace in aNamespaceStack[ : : -1 ]:
				if namespace == qname.namespace:
					break
			else:
				raise KeyError( 'Namespace not found.' )

			if prefix:
				return '%s:%s' % ( prefix, qname.localname )

		return qname.localname

	for eName, eValue in aVariables.items( ):
		# Don't let variable definitions get recursive, it just
		# confuses things.
		compactedHeader += add_lines( NamedExpression.build( '?variable ', eName, eValue, Variables( ) ) )

	isFirstElement = True
	events = ( 'start', 'end', 'start-ns', 'end-ns', 'comment', 'pi' )
	try:
		for action, element in etree.iterparse( xmlFile, events ):
			if action == 'start':
				# Special cases for doctype information, which must be
				# added before any other elements, and has no event
				# available.
				if isFirstElement:
					isFirstElement = False
					docinfo = element.getroottree( ).docinfo
					if docinfo.encoding:
						compactedHeader += add_lines( Expression.build( '?encoding ', docinfo.encoding, Variables( ) ) )
					if docinfo.doctype:
						doctype = matchDoctype.match( docinfo.doctype ).group( 'doctype' )
						compactedHeader += add_lines( Expression.build( '<!DOCTYPE ', doctype, aVariables ) )

				#TODO: Use default macros when possible.
				compacted += add_lines( Expression.build( '<', prefixed_name( element.tag ), aVariables ) )
				cIndent += 1
				for aNamespaceDeclaration in aaNewNamespaceDeclarations:
					compacted += add_lines( aNamespaceDeclaration )
				aaNewNamespaceDeclarations = []
				for name, value in element.attrib.items( ):
					compacted += add_lines( NamedExpression.build( '@', prefixed_name( name ), value, aVariables ) )
				if stripped( element.text ):
					compacted += add_lines( Expression.build( '"', stripped( element.text ), aVariables ) )
			elif action == 'end':
				cIndent -= 1
				if stripped( element.tail ):
					compacted += add_lines( Expression.build( '"', stripped( element.tail ), aVariables ) )
				# Memory optimization.
				element.clear( )
			elif action == 'start-ns':
				prefix, namespace = element

				namespaceDefined = aNamespaces.is_defined( prefix, namespace )
				prefixUsed = any( True for previousPrefix, previousNamespace in aNamespaceStack if previousPrefix == prefix )

				if prefixUsed or not namespaceDefined:
					if prefix:
						aaNewNamespaceDeclarations.append( NamedExpression.build( '#', prefix, namespace, aVariables ) )
					else:
						aaNewNamespaceDeclarations.append( Expression.build( '#', namespace, aVariables ) )

				aNamespaceStack.append( ( prefix, namespace ) )
			elif action == 'end-ns':
				aNamespaceStack.pop( )
			elif action == 'comment':
				compacted += add_lines( Expression.build( '!', element.text, aVariables ) )
			elif action == 'pi':
				compacted += add_lines( NamedExpression.build( '<?', element.target, element.text, aVariables ) )
			else:
				raise ValueError( 'Unknown parse action %s.' % action )
	except etree.ParseError, exception:
		raise CompactError( xmlFile, exception )

	return compactedHeader + compacted
