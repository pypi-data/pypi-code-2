# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

from   zope.interface   import Interface

class IEazyTextMacro( Interface ) :
    """Interface specification for wiki Macro plugin. All methods will accept
    a parameter `node` which contains following use attributes,
    EazyText macro / nowiki classes.
      *  node.parser            PLY Yacc parser
      *  node.parser.etparser   ETParser() object

    where `etparser` has the following useful attributes,
      *  etparser.etxconfig   Configuration parameters
      *  etparser.tu          Translation Unit for the parsed text
      *  etparser.text        Raw wiki text.
      *  etparser.pptext      Preprocessed wiki text.
      *  etparser.html        Converted HTML code from Wiki text

    if any of the specified method recieves `igen` as a parameter, it can be
    used generate the stack machine instruction.
    """
    def onparse( node ):
        """Will be invoked after parsing the text and while instantiating the
        AST node corresponding to template-tag.
        """

    def headpass1( node, igen ):
        """Invoked during headpass1 pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def headpass2( node, igen ):
        """Invoked during headpass2 pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def generate( node, igen, *args, **kwargs ):
        """Invoked during generate pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def tailpass( node, igen ):
        """Invoked during tailphass pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """


class IEazyTextMacroFactory( Interface ) :
    """Interface specification to instantiate a handler object for macro
    plugin. Only the class implementing this interface will be registered as
    macro plugin, which must be a callable returning the actual macro
    plugin object implementing IEazyTextMacro methods."""

    def __call__( self, argtext ) :
        """Return an instance of the macro-plugin, using the macro arguments,
        `argtext`.
        """

class IEazyTextExtension( Interface ) :
    """Interface specification for wiki Extension plugin. All methods will accept
    a parameter `node` which contains following use attributes,
    EazyText extension / nowiki classes.
      *  node.parser            PLY Yacc parser
      *  node.text              Raw extension text between {{{ ... }}}
      *  node.parser.etparser   ETParser() object

    where `etparser` has the following useful attributes,
      *  etparser.etxconfig   Configuration parameters
      *  etparser.tu          Translation Unit for the parsed text
      *  etparser.text        Raw wiki text.
      *  etparser.pptext      Preprocessed wiki text.
      *  etparser.html        Converted HTML code from Wiki text

    if any of the specified method recieves `igen` as a parameter, it can be
    used generate the stack machine instruction.
    """
    
    def onparse( node ):
        """Will be invoked after parsing the text and while instantiating the
        AST node corresponding to template-tag.
        """

    def headpass1( node, igen ):
        """Invoked during headpass1 pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def headpass2( node, igen ):
        """Invoked during headpass2 pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def generate( node, igen, *args, **kwargs ):
        """Invoked during generate pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def tailpass( node, igen ):
        """Invoked during tailphass pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """


class IEazyTextExtensionFactory( Interface ) :
    """Interface specification to instantiate a handler object for extension
    plugin. Only the class implementing this interface will be registered as
    extension plugin, which must be a callable returning the actual extention
    plugin object implementing IEazyTextExtension methods."""

    def __call__( self, *args ) :
        """Return an instance of the extension-plugin, using the extension
        arguments list, `args`.
        """


class IEazyTextTemplateTags( Interface ) :
    """Interface specification for templated tag plugins. Implementing
    plugin-class will have to support the multi pass AST processing.
        headpass1(), headpass2(), generate() and tailpass() methods
    """

    def onparse( node ):
        """Will be invoked after parsing the text and while instantiating the
        AST node corresponding to template-tag.
        """

    def headpass1( node, igen ):
        """Invoked during headpass1 pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def headpass2( node, igen ):
        """Invoked during headpass2 pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def generate( node, igen, *args, **kwargs ):
        """Invoked during generate pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """

    def tailpass( node, igen ):
        """Invoked during tailphass pass, `igen` object can be used to
        generate the stack machine instruction. `node` is NonTerminal AST node
        representing the templated-tag.
        """
