#!/usr/bin/python -tt

from __future__ import absolute_import

from pyparsing import *

def indentedBlock(blockStatementExpr, indentStack, indent=True):
	"""Helper method for defining space-delimited indentation blocks, such as
	   those used to define block statements in Python source code.

	   Parameters:
		- blockStatementExpr - expression defining syntax of statement that
			is repeated within the indented block
		- indentStack - list created by caller to manage indentation stack
			(multiple statementWithIndentedBlock expressions within a single grammar
			should share a common indentStack)
		- indent - boolean indicating whether block must be indented beyond the
			the current level; set to False for block of left-most statements
			(default=True)

	   A valid block must contain at least one blockStatement.
	"""
	def checkPeerIndent(s,l,t):
		if l >= len(s): return
		curCol = col(l,s)
		if curCol != indentStack[-1]:
			if curCol > indentStack[-1]:
				raise ParseFatalException(s,l,"illegal nesting")
			raise ParseException(s,l,"not a peer entry")

	def checkSubIndent(s,l,t):
		curCol = col(l,s)
		if curCol > indentStack[-1]:
			indentStack.append( curCol )
		else:
			raise ParseException(s,l,"not a subentry")

	def checkUnindent(s,l,t):
		if l >= len(s): return
		curCol = col(l,s)
		if not(indentStack and curCol < indentStack[-1] and curCol <= indentStack[-2]):
			raise ParseException(s,l,"not an unindent")
		indentStack.pop()

	INDENT = Empty().setParseAction(checkSubIndent)
	PEER   = Empty().setParseAction(checkPeerIndent)
	UNDENT = Empty().setParseAction(checkUnindent)
	if indent:
		smExpr = Group( 
			#FollowedBy(blockStatementExpr) +
			INDENT + (OneOrMore( PEER + Group(blockStatementExpr) )) + UNDENT)
	else:
		smExpr = Group(
			OneOrMore( PEER + Group(blockStatementExpr) ) )
	return smExpr

def checkIndent( indentStack ):
	def checkPeerIndent(s,l,t):
		if l >= len(s): return
		curCol = col(l,s)
		if curCol != indentStack[-1]:
			if curCol > indentStack[-1]:
				raise ParseFatalException(s,l,"illegal nesting")
			raise ParseException(s,l,"not a peer entry")

	PEER = Empty().setParseAction(checkPeerIndent)
	return PEER

def set_whitespace( expression, whitespace, seen = set() ):
	if expression in seen: return
	seen.add( expression )
	skipWhitespace = expression.skipWhitespace
	# setWhitespaceChars resets skipWhitespace value, we don't want that.
	expression.setWhitespaceChars( whitespace )
	expression.skipWhitespace = skipWhitespace
	if hasattr( expression, 'expr' ):
		set_whitespace( expression.expr, whitespace, seen )
	if hasattr( expression, 'exprs' ):
		for e in expression.exprs:
			set_whitespace( e, whitespace, seen )

def line( loc, strg ):
	'''Bug fix for pyparsing.line which returns whole string for when loc
	equals 0 and the first character in the string is a newline.'''
	iLastNewline = strg.rfind( '\n', 0, loc )
	iNextNewline = strg.find( '\n', loc )
	if iNextNewline >= 0:
		return strg[ iLastNewline + 1 : iNextNewline ]
	else:
		return strg[ iLastNewline + 1 : ]
