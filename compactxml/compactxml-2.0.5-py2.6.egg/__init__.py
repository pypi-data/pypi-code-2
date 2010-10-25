#!/usr/bin/python -tt
'''
compactxml is a module for converting from and to a python like dialect of XML.

Use the expand* functions to convert from compactxml to XML, and the compact* functions to convert from XML to compactxml.
'''

from __future__ import absolute_import

from lxml import etree

import cStringIO as StringIO

from .expand import expand as expand_string
from .expand import load_macros as expand_load_macros
from .compact import compact as compact_file
from .resolve import resolve_filename
from .error import ParsingError

__version__ = '2.0.5'

def resolve( location ):
	'''
	A global function used in expand calls to lookup files specified by
	?load preprocessor directives in compactxml files. Override this
	function to change how file names are looked up. By default, loads as
	local file name.

	Arguments:
	location -- The path to resolve.

	Returns: An open file object.
	'''
	return resolve_filename( location )

def load_macros( document, variables = {}, macros = None ):
	'''
	Loads macros from a given compactxml document. Accepts strings or file
	objects. Used to load macros to be used in expanding other compactxml
	files.

	Arguments:
	document -- Document to load macros from.
	variables -- Optional dictionary of variable names and values to use during the expand.
	macros -- Already loaded macros to combine with those loaded.

	Returns: An opaque macro object.
	'''
	if isinstance( document, basestring ):
		return expand_load_macros( document, {}, variables, macros )
	else:
		return expand_load_macros( document.read( ), {}, variables, macros )

def __expand( document, namespaces, variables, macros ):
	if isinstance( document, basestring ):
		return expand_string( document, namespaces, variables, macros )
	else:
		return expand_string( document.read( ),  namespaces, variables, macros )

def expand( document, namespaces = {}, variables = {}, macros = None ):
	'''
	Expands a compactxml document into a parsed lxml ElementTree. Accepts
	strings or file objects.

	Arguments:
	document -- Document to expand.
	namespaces -- Optional dictionary of default prefixes and namespaces to use during the expand.
	variables -- Optional dictionary of variable names and values to use during the expand.
	macros -- Optional default macros to use during the expand, as loaded by load_macros.

	Returns: An lxml ElementTree object.
	'''
	encoding, tree = __expand( document, namespaces, variables, macros )
	return tree

def expand_to_string( document, namespaces = {}, variables = {}, macros = None, prettyPrint = False ):
	'''
	Expands a compactxml document as expand, however returns a serialized
	string of the expanded XML. Accepts strings or file objects.

	Arguments:
	document -- Document to expand.
	namespaces -- Optional dictionary of default prefixes and namespaces to use during the expand.
	variables -- Optional dictionary of variable names and values to use during the expand.
	macros -- Optional default macros to use during the expand, as loaded by load_macros.
	prettyPrint -- Optional flag for pretty printing the resulting XML. Defaults to false.

	Returns: A string.
	'''
	encoding, tree = __expand( document, namespaces, variables, macros )
	return etree.tostring( tree, encoding = encoding, pretty_print = prettyPrint )

def expand_to_file( document, outputFile, namespaces = {}, variables = {}, macros = None, prettyPrint = False ):
	'''
	Expands a compactxml document as expand, however writes a serialized
	string of the expanded XML to the given open file object. Accepts
	strings or file objects.

	Arguments:
	document -- Document to expand.
	outputFile -- Open file object to write output to.
	namespaces -- Optional dictionary of default prefixes and namespaces to use during the expand.
	variables -- Optional dictionary of variable names and values to use during the expand.
	macros -- Optional default macros to use during the expand, as loaded by load_macros.
	prettyPrint -- Optional flag for pretty printing the resulting XML. Defaults to false.

	Returns: Nothing.
	'''
	outputFile.write( expand_to_string( document, namespaces, variables, macros, prettyPrint ) )

def compact( document, namespaces = {}, variables = {}, macros = None, stripText = False ):
	'''
	Compacts a serialized XML string or file to compactxml form.

	Arguments:
	document -- Document to compact.
	namespaces -- Dictionary of namespaces to expect as defaults, thus
		ignore when creating namespace declarations.
	variables -- Dictionary of variables to substitute when found in
		values.
	macros -- Currently unused.
	stripText -- Optional flag for stripping all text before compacting to
		remove extraneous whitespace. Defaults to false.

	Returns: A string
	'''
	if isinstance( document, basestring ):
		document = StringIO.StringIO( document )

	return compact_file( document, namespaces, variables, macros, stripText )

compact_to_string = compact

def compact_to_file( document, outputFile, namespaces = {}, variables = {}, macros = None, stripText = False ):
	'''
	Compacts a serialized XML string or file to compactxml form, writing
	the resulting string to an open file.

	Arguments:
	document -- Document to compact.
	outputFile -- Open file object to write output to.
	namespaces -- Dictionary of namespaces to expect as defaults, thus
		ignore when creating namespace declarations.
	variables -- Dictionary of variables to substitute when found in
		values.
	macros -- Currently unused.
	stripText -- Optional flag for stripping all text before compacting to
		remove extraneous whitespace. Defaults to false.

	Returns: Nothing.
	'''
	outputFile.write( compact_to_string( document, namespaces, variables, macros, stripText ) )
