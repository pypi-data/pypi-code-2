# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

"""Module containing Node definition for all non-teminals and translator
functions for translating the text to HTML"""

# -*- coding: utf-8 -*-

# Gotcha : None
# Notes  : None
# Todo   :
#   1. Add unicode support
#   2. Add ismatched() method.
#   3. For links that open in new window, append a character that would say
#      so.
#   4. Remove old Textlexer based parsing.

import sys
import re
from   random       import randint
from   os.path      import basename, abspath, dirname, join, isdir, isfile
import types

from   eazytext.macro        import build_macro
from   eazytext.extension    import build_ext
from   eazytext              import escape_htmlchars, split_style, \
                                    obfuscatemail, lhtml
from   eazytext.stylelookup  import styleparser 
import eazytext.ttags        as tt

# text type for BasicText
TEXT_CHARPIPE            = 1001    #'charpipe'
TEXT_ALPHANUM            = 1002    #'alphanum'
TEXT_SPECIALCHAR         = 1003    #'specialchar'
TEXT_SPECIALCHAR_LB      = 1004    #'linebreak'
TEXT_HTTPURI             = 1005    #'httpuri'
TEXT_WWWURI              = 1006    #'wwwuri'
TEXT_ESCAPED             = 1007    #'escaped'
TEXT_LINK                = 1008    #'link'
TEXT_MACRO               = 1009    #'macro'
TEXT_HTML                = 1010    #'html'
TEXT_NEWLINE             = 1011    #'newline'

TEXT_M_SPAN                = 2001  #'m_span'
TEXT_M_BOLD                = 2002  #'m_bold'
TEXT_M_ITALIC              = 2003  #'m_italic'
TEXT_M_UNDERLINE           = 2004  #'m_underline'
TEXT_M_SUBSCRIPT           = 2005  #'m_subscript'
TEXT_M_SUPERSCRIPT         = 2006  #'m_superscript'
TEXT_M_BOLDITALIC          = 2007  #'m_bolditalic'
TEXT_M_BOLDUNDERLINE       = 2008  #'m_boldunderline'
TEXT_M_ITALICUNDERLINE     = 2009  #'m_italicunderline'
TEXT_M_BOLDITALICUNDERLINE = 2010  #'m_bolditalicunderline'

# List Type
LIST_ORDERED        = 'ordered'
LIST_UNORDERED      = 'unordered'

# Markup
M_PIPE              = '|'
M_PIPEHEAD          = '|='

FORMAT_NON          = 'fmt_non'
FORMAT_EMPTY        = 'fmt_empty'
FORMAT_BTABLE       = 'fmt_bt'
FORMAT_BTABLESTYLE  = 'fmt_btstyle'

templtdir = join( dirname(__file__), 'templates' )

html_templates = {
    TEXT_M_SPAN : [
        '<span class="etmark" style="%s">',
        '</span>', ],
    TEXT_M_BOLD : [
        '<strong class="etmark" style="%s">',
        '</strong>', ],
    TEXT_M_ITALIC : [
        '<em class="etmark" style="%s">',
        '</em>', ],
    TEXT_M_UNDERLINE : [
        '<u class="etmark" style="%s">',
        '</u>', ],
    TEXT_M_SUPERSCRIPT : [
        '<sup class="etmark" style="%s">',
        '</sup>', ],
    TEXT_M_SUBSCRIPT : [
        '<sub class="etmark" style="%s">',
        '</sub>', ],
    TEXT_M_BOLDITALIC : [
        '<strong class="etmark" style="%s"><em class="etmark">',
        '</em></strong>', ],
    TEXT_M_BOLDUNDERLINE : [
        '<strong class="etmark" style="%s"><u class="etmark">',
        '</u></strong>', ],
    TEXT_M_ITALICUNDERLINE : [
        '<em class="etmark" style="%s"><u class="etmark">',
        '</u></em>', ],
    TEXT_M_BOLDITALICUNDERLINE : [
    '<strong class="etmark" style="%s"><em class="etmark"><u class="etmark">',
    '</u></em></strong>' ]
}
def markup2html( type_, mtext, steed ) :
    if steed == 0 :
        return html_templates[type_][0] % styleparser( mtext[2:] )
    else :
        return html_templates[type_][1]

class ASTError( Exception ):
    pass

class Content( object ) :
    """The whole of wiki text is parsed and encapulated as lists of Content
    objects."""
    def __init__( self, parser, text, type=None, html=None ) :
        self.parser = parser
        self.text   = text
        self.type   = type
        self._html  = html

    def _gethtml( self ) :
        attr = self._html
        return attr() if hasattr(attr, '__call__') else attr

    def _sethtml( self, value ) :
        self._html = value

    def __repr__( self ) :
        return "Content<'%s','%s','%s'>" % (self.text, self.type, self.html )

    html = property( _gethtml, _sethtml )

def process_textcontent( contents ) :
    """From the list of content objects (tokenized), construct the html
    page."""
    count = len(contents)
    for i in range( count ) :
        beginmarkup_cont = contents[i]
        if beginmarkup_cont.html or \
           beginmarkup_cont.type == TEXT_SPECIALCHAR or\
           beginmarkup_cont.type == TEXT_ALPHANUM :
            continue
        for j in range( i+1, count ) :
            endmarkup_cont = contents[j]
            if endmarkup_cont.type == beginmarkup_cont.type and j != i+1  :
                # Found the markup pair, with some text in between
                beginmarkup_cont.html = markup2html( beginmarkup_cont.type,
                                                     beginmarkup_cont.text,
                                                     0
                                                   )
                endmarkup_cont.html   = markup2html( endmarkup_cont.type,
                                                     endmarkup_cont.text,
                                                     1
                                                   )
                # All the markups in between should be self contained between
                # i and j
                process_textcontent( contents[i+1:j] )
                break;
        else :
            beginmarkup_cont.html = beginmarkup_cont.text

    return

# ---------------------- AST class nodes -------------------

class Node( object ):
    """Abstract base class for EazyText AST nodes. DO NOT instanciate."""

    def children( self ):
        """A sequence of all children that are ``Nodes``"""
        pass

    def tohtml( self ):
        """Translate the node and all the children nodes to html markup and
        return the content"""

    def ismatched( self ) :
        """This interface should return a boolean indicating whether the html
        generated by this node is matched. If a node expects that the html
        might be mismatched.
        After replacing etree with lxml mismatched elements are automatically
        taken care."""
        return True

    def dump( self ):
        """Simply dump the contents of this node and its children node and
        return the same."""

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ):
        """ Pretty print the Node and all its attributes and children
        (recursively) to a buffer.
            
        file:   
            Open IO buffer into which the Node is printed.
        
        offset: 
            Initial offset (amount of leading spaces) 
        
        attrnames:
            True if you want to see the attribute names in name=value pairs.
            False to only see the values.
        
        showcoord:
            Do you want the coordinates of each Node to be displayed."""
        pass


class Wikipage( Node ):
    """class to handle `wikipage` grammar."""

    # Class etpage or etblk
    template = """<div class="%s" style="%s">
                    %s
                    %s
                    %s
                    %s
                </div>"""

    def __init__( self, parser, paragraphs ) :
        self.parser     = parser
        self.paragraphs = paragraphs

    def children( self ) :
        return (self.paragraphs,)

    def tohtml( self ):
        etparser = self.parser.etparser
        # Call the registered prehtml methods.
        etparser.onprehtml_macro()
        etparser.onprehtml_ext()
        # Generate HTML from childrens
        etparser.html  = ''.join([ c.tohtml() for c in self.children() ])
        # Call the registered posthtml methods.
        etparser.onposthtml_macro()
        etparser.onposthtml_ext()

        # Sort prehtmls and posthtmls based on the weight
        allhtmls = sorted( etparser.prehtmls + etparser.posthtmls,
                           key=lambda x : x[0] )
        prehtmls = filter( lambda x : x[0] < 0, allhtmls )
        posthtmls = filter( lambda x : x[0] >= 0, allhtmls )

        # Join them together
        prehtmls = ''.join( map( lambda x : x[1], prehtmls ))
        posthtmls = ''.join( map( lambda x : x[1], posthtmls ))

        # Final html
        skin = '' if etparser.skin == None else etparser.skin
        etparser.html = self.template % (
                            'etblk' if etparser.nested else 'etpage',
                            etparser.styleattr,
                            '' if etparser.nested else skin,
                            prehtmls,
                            etparser.html,
                            posthtmls
                        )
        return etparser.html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'wikipage: ' )

        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children():
            c.show( buf, offset + 2, attrnames, showcoord )


class Paragraphs( Node ) :
    """class to handle `paragraphs` grammar."""

    template = None

    def __init__( self, parser, *args  ) :
        self.parser = parser
        if len( args ) == 1 :
            self.paragraph_separator = args[0]
        elif len( args ) == 2 :
            self.paragraph = args[0]
            self.paragraph_separator = args[1]
        elif len( args ) == 3 :
            self.paragraphs = args[0]
            self.paragraph = args[1]
            self.paragraph_separator = args[2]

    def children( self ) :
        attrs = [ 'paragraphs', 'paragraph', 'paragraph_separator' ]
        nodes = filter( None, [ getattr( self, a, None ) for a in attrs ] )
        return tuple(nodes)

    def tohtml( self ):
        return ''.join([ c.tohtml() for c in self.children() ])

    def dump( self ) :
        return ''.join([ c.dump() for c in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'paragraphs: ' )

        if showcoord:
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children():
            c.show( buf, offset + 2, attrnames, showcoord )


class Paragraph( Node ) :
    """class to handle `paragraph` grammar."""

    template = None

    def __init__( self, parser, paragraph ) :
        self.parser = parser
        self.paragraph = paragraph

    def children( self ) :
        return ( self.paragraph, )

    def tohtml( self ):
        return self.paragraph.tohtml()

    def dump( self ) :
        return self.paragraph.dump()

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'paragraph: ')

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children() :
            c.show( buf, offset + 2, attrnames, showcoord )


class NoWiki( Node ) :
    """class to handle `nowikiblock` grammar."""

    def __init__( self, parser, opennowiki, opennl, nowikilines,
                  closenowiki=None, closenl=None, skip=False  ) :
        _t = opennowiki[3:]
        self.parser = parser
        self.xparams = _t.strip( ' \t' ).split(' ')
        self.xwikiname = self.xparams and self.xparams.pop(0) or ''
        self.opennewline = Newline( parser, opennl )
        self.nowikilines = nowikilines
        self.skip = skip
        self.nowikitext   = opennowiki  + opennl + nowikilines
        if not self.skip :
            self.closenewline = Newline( parser, closenl )
            self.wikixobject = build_ext( self, nowikilines )
            self.nowikitext += closenowiki + closenl
        self.text = self.nowikitext

    def children( self ) :
        return (self.nowikilines,)

    def tohtml( self ):
        html = '' if self.skip else self.wikixobject.tohtml()
        return html

    def dump( self ) :
        return self.nowikitext

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + ( 
                   'nowikiblock: `%s` ' % self.nowikilines.split('\n')[0] )
                 )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class Heading( Node ) :
    """class to handle `heading` grammar."""

    template = """
    <h%s class="etsec" style="%s">
      %s
      <a name="%s"></a>
      <a class="etseclink" href="#%s" title="Link to this section">&#9875;</a>
    </h%s>
    """

    def __init__( self, parser, headmarkup, headline, newline ) :
        self.headmarkuptxt = headmarkup
        self.headmarkup, self.level, self.style = self._parseheadmarkup(
                                                            headmarkup )
        self.parser = parser
        self.textcontents = headline
        self.newline = Newline( parser, newline )

    def _parseheadmarkup( self, headmarkup ) :
        """Convert the header markup into respective level. Note that, header
        markup can be specified with as ={1,5} or h[1,2,3,,4,5]"""
        headmarkup = headmarkup.lstrip( ' \t' )
        off = headmarkup.find( '{' )
        if off > 0 :
            headmarkup = headmarkup[:off]
            style = styleparser( headmarkup[off:] )
        else :
            headmarkup = headmarkup
            style = ''

        if '=' in headmarkup :
            level = len(headmarkup)
        elif headmarkup[0] in 'hH' :
            level = int(headmarkup[1])
        else :
            level = 5
        return headmarkup, level, style

    def children( self ) :
        return ( self.headmarkup, self.textcontents, self.newline )

    def tohtml( self ):
        l = self.level
        contents = []
        if isinstance( self.textcontents, TextContents ) :
            [ contents.extend( item.contents )
              for item in self.textcontents.textcontents ]
        process_textcontent( contents )
        html = self.textcontents.tohtml().strip(' \t=')
        text = ''.join( lhtml.fromstring(html).xpath( '//text()' ) )
        html = ( self.template % ( l, self.style, html, text, text, l )) + \
               self.newline.tohtml()
        return html

    def dump( self ) :
        return self.headmarkuptxt + self.textcontents.dump() + \
               self.newline.dump()

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'heading: `%s` ' % list(self.children()[:-1] ))

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')
        self.newline.show( buf, offset + 2, attrnames, showcoord )


class HorizontalRule( Node ) :
    """class to handle `horizontalrule` grammar."""

    template = '<hr class="ethorz"/>'

    def __init__( self, parser, hrule, newline ) :
        self.parser = parser
        self.hrule   = hrule
        self.newline = Newline( parser, newline )

    def children( self ) :
        return (self.hrule, self.newline)

    def tohtml( self ):
        return self.template

    def dump( self ) :
        return self.hrule + self.newline.dump()

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'horizontalrule:' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        self.newline.show( buf, offset + 2, attrnames, showcoord )


class TextLines( Node ) :
    """class to handle `textlines` grammar."""

    template = '<p class="ettext"> %s </p>'

    def __init__( self, parser, textcontents, newline  ) :
        self.parser = parser
        self.textlines = [ (textcontents, Newline( parser, newline )) ]

    def appendline( self, textcontents, newline ) :
        self.textlines.append(
            ( textcontents, Newline( self.parser, newline ) )
        )

    def children( self ) :
        return (self.textlines,)

    def tohtml( self ) :
        # Combine text lines, process the text contents and convert them into
        # html
        contents = []
        [ contents.extend( item.contents )
          for textcontents, nl in self.textlines 
          for item in textcontents.textcontents ]
        process_textcontent( contents )
        html = ''
        for textcontents, newline in self.textlines :
            html += textcontents.tohtml()
            html += newline.tohtml()
        return self.template % html

    def dump( self ) :
        fn = lambda x : ''.join([ item.dump() for item in x.textcontents ])
        txt = ''.join([ fn(textcontents) + newline.dump()
                        for textcontents, newline in self.textlines ])
        return txt

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'textlines: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        linecount = 1
        for textcontent, newline in self.textlines :
            buf.write( lead + '(line %s)\n' % linecount )
            linecount += 1
            textcontent.show( buf, offset + 2, attrnames, showcoord )
            newline.show( buf, offset + 2, attrnames, showcoord )


class BtableRows( Node ) :
    """class to handle `btablerows` grammar"""

    tbl_template = '<table class="etbtbl sortable" cellspacing="0px" ' + \
                   ' cellpadding="5px" style="%s">'
    row_template = '  <tr class="etbtbl" style="%s">'
    hdrcell_template = '<th class="etbtbl" style="%s"> %s </th>'
    cell_template = '<td class="etbtbl" style="%s"> %s </td>'

    def __init__( self, parser, row ) :
        self.parser = parser
        self.rows = [ row ]

    def appendrow( self, row ) :
        self.rows.append( row )

    def children( self ) :
        return self.rows

    def tohtml( self ) :
        html = ''
        closerow = []       # Stack to manage rows
        closetable = []     # Stack to manage table
        for row in self.rows :
            mrkup = row.rowmarkup.lstrip( ' \t' )[:3]
            style = row.style()
            if mrkup == '||{' :     # open table
                if closetable : continue
                html += self.tbl_template % style
                closetable.append( '</table>' )
            elif mrkup == '||-' :   # Row
                if closerow : html += closerow.pop()
                html += self.row_template % style
                closerow.append( '</tr>' )
            elif mrkup == '||=' :   # header cell
                html += self.hdrcell_template % ( style, row.tohtml() )
            elif mrkup == '|| ' :   # Cell
                html += self.cell_template % ( style, row.tohtml() )
            elif mrkup == '||}' :   # close table
                pass
        if closerow :
            closerow.reverse()
            html += ''.join( closerow )
        if closetable :
            closetable.reverse()
            html+= ''.join( closetable )
        return html

    def dump( self ) :
        return ''.join([ row.dump() for row in self.rows ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for row in self.rows :
            row.show( buf, offset + 2, attrnames, showcoord )


class BtableRow( Node ) :
    """class to handle `btablerow` grammar"""

    template = None

    def __init__( self, parser, rowmarkup, rowitem, newline, type=None ) :
        self.parser = parser
        self.rowtype = type
        self.rowmarkup = rowmarkup
        self.textlines = [( rowitem, Newline(parser, newline) )]

    def contlist( self, parser, textcontents, newline ) :
        self.textlines.append( 
            ( textcontents, Newline( self.parser, newline ) )
        )

    def children( self ) :
        return ( self.rowmarkup, self.textlines )

    def tohtml( self ) :
        html = ''
        mrkup = self.rowmarkup.lstrip( ' \t' )[:3]
        # For header cell and normal cell
        if mrkup in [ '|| ', '||=' ] and self.textlines:
            contents = []
            [ contents.extend( item.contents )
              for textcontents, nl, in self.textlines
              if isinstance( textcontents, TextContents )
              for item in textcontents.textcontents ]
            process_textcontent( contents )
            celltext = ''
            for textcontents, newline in self.textlines :
                celltext += textcontents.tohtml()
                celltext += newline.tohtml()
            html += celltext
        return html

    def style( self ) :
        if self.rowtype == FORMAT_BTABLESTYLE :
            style = self.rowmarkup.lstrip( ' \t' )[3:].lstrip( ' \t' )
            style = styleparser( style.rstrip( '| \t' ) )
        else :
            style = ''
        return style

    def dump( self ) :
        text = self.rowmarkup
        for textcontents, nl in self.textlines :
            text += textcontents.dump() + nl.dump()
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'btablerow : `%s`' % self.rowmarkup )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write( '\n' )
        if self.textcontents :
            self.textcontents.show()
        elif self.empty :
            self.empty.show()
        else :
            raise ASTError(
                    "show() : No bqitem available for BtableRow() node"
            )


class TableRows( Node ) :
    """class to handle `table_rows` grammar."""
    tbl_template = '<table class="ettbl sortable" cellspacing="0" ' + \
                   ' cellpadding="5px"> %s </table>'
    tr_template = '<tr class="ettbl"> %s </tr>'

    def __init__( self, parser, row, pipe=None, newline=None  ) :
        """`row` is table_cells"""
        self.parser = parser
        self.rows = [ (row, pipe, Newline( parser, newline )) ]

    def appendrow( self, row, pipe=None, newline=None ) :
        self.rows.append( (row, pipe, Newline( self.parser, newline )) )

    def tohtml( self ) :
        html = ''
        for row, pipe, newline in self.rows :
            cont = row.tohtml() + ( newline.tohtml() if newline else '' )
            html += self.tr_template % cont
        html = self.tbl_template % html
        return html

    def children( self ) :
        return self.rows

    def dump( self ) :
        return ''.join(
            [ row.dump() + (pipe or '') + (nl and nl.dump()) or ''
              for row, pipe, nl in self.rows ]
        )

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'table_rows: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        rowcount = 1
        for row, pipe, nl in self.rows :
            buf.write( lead + '(row %s)\n' % rowcount )
            rowcount += 1
            row.show( buf, offset + 2, attrnames, showcoord )
            nl and nl.show( buf, offset + 2, attrnames, showcoord )


class TableCells( Node ) :
    """class to handle `table_cells` grammar."""

    hdrcell_template = '<th class="ettbl" colspan="%s" style="%s"> %s </th>'
    cell_template = '<td class="ettbl" colspan="%s" style="%s"> %s </td>'

    RIGHTALIGN = '$'

    def __init__( self, parser, markup, cell  ) :
        """`cell` can be `Empty` object or `TextContents` object"""
        self.parser = parser
        self.cells = [ [markup, cell, 1] ] # `markup` is pipe+style

    def appendcell( self, markup, cell ) :
        if isinstance(cell, Empty) :
            # If no content for this cell, then merge the cell with the
            # previous cell
            self.cells[-1][2] += 1 # By incrementing the colspan
            # skip this cell in tohtml() and dump()
            self.cells.append([ markup, cell, 0 ])
        else :
            self.cells.append([ markup, cell, 1 ])

    def children( self ) :
        return ( self.cells, )

    def totalcells( self ) :
        return sum([
                  1 for markup, cell, colspan in self.cells 
                  if isinstance( cell, TextContents )
                ])

    def tohtml( self ) :
        style = ''
        htmlcells = []
        for markup, cell, colspan in self.cells :
            if colspan == 0 : continue
            markup = markup.strip()
            contents = []
            if isinstance( cell, TextContents ) :
                [ contents.extend( x.contents ) for x in cell.textcontents ]
                chtml = contents[-1].html
                if chtml and (chtml[-1] == self.RIGHTALIGN) : # text alignment
                    style +=  'text-align : right; '
                    contents[-1].html = chtml[-1][:-1]
            process_textcontent( contents )
            style_, template = ( styleparser( markup[2:] ),
                                self.hdrcell_template 
                              ) if markup[:2] == M_PIPEHEAD else (
                                styleparser( markup[1:] ),
                                self.cell_template  )
            style += style_
            htmlcells.append( template % (colspan, style, cell.tohtml()) )
        return ''.join( htmlcells )

    def dump( self ) :
        return ''.join(
            [ markup + cell.dump() for markup, cell, colspan in self.cells ]
        )

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'table_cells: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        cellcount = 1
        for markup, cell, colspan in self.cells :
            buf.write( lead + '(cell %s)\n' % cellcount )
            cellcount += 1
            cell.show( buf, offset + 2, attrnames, showcoord )


class Lists( Node ) :
    """class to handle `orderedlists` and `unorderedlists` grammar."""

    patt = re.compile( r'[\*\#]{1,5}$', re.MULTILINE | re.UNICODE )
    list_styletype = { '#' : ['decimal', 'lower-roman', 'lower-alpha'],
                       '*' : ['disc', 'disc', 'disc' ] }
    template = {
        '#' : ('<ol class="et" style="list-style-type: %s;">', '</ol>'),
        '*' : ('<ul class="et" style="list-style-type: %s;">', '</ul>')
    }

    def __init__( self, parser, l ) :
        self.parser = parser
        self.listitems = [ l ]

    def appendlist( self, l ) :
        self.listitems.append( l )

    def children( self ) :
        return self.listitems

    def tohtml( self ) :
        closemarkups = []   # Stack to manage nested list.
        html = pm = cm = ''
        for l in self.listitems :
            cm = re.search( self.patt, l.listmarkup ).group()
            cmpmark = cmp( len(pm), len(cm) )  # -1 or 0 or 1
            diffmark = abs( len(cm) - len(pm))  # 0 to 4
            if cmpmark > 0 :
                # previous list markup (pm) one level deeper, end the list
                html += ''.join([closemarkups.pop() for i in range(diffmark)])
            elif cmpmark < 0 :
                # current list markup (cm) one level deeper, open a new list
                for i in range(diffmark) :
                    style = self.list_styletype[ cm[0]][len(l.listmarkup)%3 ]
                    html += self.template[cm[0]][0] % style
                    closemarkups.append( self.template[cm[0]][1] )
            html += l.tohtml()
            pm = cm
        closemarkups.reverse()
        html += ''.join( closemarkups )
        return html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.listitems ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for c in self.listitems :
            c.show( buf, offset + 2, attrnames, showcoord )


class List( Node ) :
    """class to handle `orderedlist` and `unorderedlist` grammar."""

    template = '<li class="et" style="%s"> %s </li>'

    def __init__( self, parser, ltype, listmarkup, textcontents, newline ) :
        self.parser = parser
        self.listtype = ltype
        self.listmarkup = listmarkup
        self.textlines = [ (textcontents, Newline( parser, newline )) ]

    def contlist( self, parser, textcontents, newline ) :
        self.textlines.append( (textcontents, Newline(parser, newline)) )

    def children( self ) :
        return ( self.listtype, self.listmarkup, self.textlines )

    def _style( self ) :
        markup = self.listmarkup.strip( ' \t' )
        off = markup.find('{')
        style = off > 0 and styleparser( markup[off:] ) or ''
        return style

    def tohtml( self ) :
        # Process the text contents and convert them into html
        contents = []
        [ contents.extend(item.contents)
          for textcontents, nl in self.textlines
          if isinstance( textcontents, TextContents )
          for item in textcontents.textcontents ]
        process_textcontent( contents )

        text = ''.join([ textcontents.tohtml() + newline.tohtml()
                         for textcontents, newline in self.textlines ])
        html = self.template % ( self._style(), text )
        return html

    def dump( self ) :
        text = ''.join([ textcontents.dump() + nl.dump()
                         for textcontents, nl in self.textlines ])
        text = self.listmarkup + text
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if self.listtype == 'ordered' :
            buf.write( lead + 'orderedlist: `%s` ' % self.listmarkup )
        if self.listtype == 'unordered' :
            buf.write( lead + 'unorderedlist: `%s` ' % self.listmarkup )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for textcontents, nl in self.textlines :
            if textcontents :
                textcontents.show()
            else :
                raise ASTError(
                            "show() : No textcontent available for List()"
                )


class Definitions( Node ) :
    """class to handle `definitionlists` grammar."""

    template = '<dl class="et"> %s </dl>' 

    def __init__( self, parser, definition ) :
        self.parser = parser
        self.listitems = [ definition ]

    def appendlist( self, definition ) :
        self.listitems.append( definition )

    def children( self ) :
        return self.listitems

    def tohtml( self ) :
        html = self.template % ''.join([ c.tohtml() for c in self.listitems ])
        return html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.listitems ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for c in self.listitems :
            c.show( buf, offset + 2, attrnames, showcoord )

class Definition( Node ) :
    """class to handle `definitionlist` grammar."""
    template = '<dt class="et"><b> %s </b></dt> <dd class="et"> %s </dd>'

    def __init__( self, parser, defnmarkup, defnitem, newline ) :
        self.parser = parser
        self.defnmarkup = defnmarkup
        self.dt = defnmarkup.strip( ' \t' )[1:-2]
        self.textlines = [ (defnitem, Newline(parser, newline )) ]

    def contlist( self, parser, textcontents, newline ) :
        self.textlines.append( (textcontents, Newline(parser, newline)) )

    def children( self ) :
        return ( self.defnmarkup, self.textlines )

    def tohtml( self ) :
        # Process the text contents and convert them into html
        contents = []
        [ contents.extend(item.contents)
          for textcontents, nl in self.textlines
          if isinstance( textcontents, TextContents )
          for item in textcontents.textcontents ]
        process_textcontent( contents )

        dd = ''.join([ textcontents.tohtml() + newline.tohtml()
                       for textcontents, newline in self.textlines ])
        html = self.template % ( escape_htmlchars( self.dt ), dd )
        return html

    def dump( self ) :
        text = self.defnmarkup
        for textcontents, nl in self.textlines :
            text += textcontents.dump() + nl.dump()
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'definition: `%s` ' % self.defnmarkup )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for textcontents, nl in self.textlines :
            if textcontents :
                textcontents.show()
            else :
                raise ASTError(
                   "show() : No defnitem available for Definition() node"
                )


class BQuotes( Node ) :
    """class to handle `blockquotes` grammar."""
    patt = re.compile( r'[\>]{1,5}$', re.MULTILINE | re.UNICODE )
    template = '<blockquote class="et %s">'

    def __init__( self, parser, bq ) :
        self.parser = parser
        self.listitems = [ bq ]

    def appendlist( self, bq ) :
        self.listitems.append( bq )

    def children( self ) :
        return self.listitems

    def _extendcontents( self, bq, contents ) :
        # Collect the contents that spans across muliple lines of same block
        # level. 'contents' is the accumulator
        [ contents.extend( item.contents )
          for item in bq.textcontents.textcontents
        ] if bq.textcontents else None
        return

    def _processcontents( self, contents ) :
        # Process the accumulated contents
        process_textcontent( contents )
        html = ''.join([ cont.html for cont in contents ])
        return html

    def tohtml( self ) :
        html = pm = cm   = ''
        closemarkups = []   # Stack to manage nested list.
        contents = []
        for i in range(len(self.listitems)) :
            cls = (i == 0) and 'firstlevel' or 'innerlevel'
            bq = self.listitems[i]
            cm = re.search( self.patt, bq.bqmarkup ).group()
            cmpmark = cmp( len(pm), len(cm) )  # -1 or 0 or 1
            diffmark = abs( len(cm) - len(pm))  # 0 or 1

            if cmpmark > 0 :
                # previous bq markup (pm) is one or more level deeper,
                # so end the blockquote(s)
                # And, process the accumulated content
                html += self._processcontents( contents )
                contents = []
                html += ''.join([closemarkups.pop() for i in range(diffmark)])

            elif cmpmark < 0 :
                # current bq markup (cm) is one or more level deeper, 
                # open new blockquote(s)
                # And, process the accumulated content
                html += self._processcontents( contents )
                contents = []

                for j in range(diffmark-1) :
                    html += self.template % ''
                    closemarkups.append( '</blockquote>' )
                html += self.template % cls
                closemarkups.append( '</blockquote>' )
            self._extendcontents( bq, contents )
            contents.append(Content(self.parser, '\n', TEXT_NEWLINE, '<br/>'))
            pm = cm

        # Pop-out the last new-line (<br/>)
        contents.pop( -1 ) if contents[-1].html == '<br/>' else None
        html += self._processcontents( contents )
        closemarkups.reverse()
        html += ''.join( closemarkups )
        return html

    def dump( self ) :
        return ''.join([ c.dump() for c in self.listitems ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for c in self.listitems :
            c.show( buf, offset + 2, attrnames, showcoord )


class BQuote( Node ) :
    """class to handle `blockquote` grammar."""

    def __init__( self, parser, bqmarkup, bqitem, newline ) :
        self.parser = parser
        self.bqmarkup = bqmarkup
        if isinstance( bqitem, Empty ) :
            self.empty = bqitem
            self.textcontents = None
        elif isinstance( bqitem, TextContents ) :
            self.empty = None
            self.textcontents = bqitem
        else :
            raise ASTError( "Unknown `bqitem` for BQuote() node" )
        self.newline = Newline( parser, newline )

    def children( self ) :
        return ( self.bqmarkup, self.textcontents, self.newline )

    def tohtml( self ) :
        # This function is not used. The logic for html translation is with
        # BQuotes class
        pass
    #    # Process the text contents and convert them into html
    #    if self.textcontents :
    #        contents = []
    #        [ contents.extend( item.contents )
    #          for item in self.textcontents.textcontents ]
    #        process_textcontent( contents )
    #        html = self.textcontents.tohtml()
    #    elif self.empty :
    #        html = self.empty.tohtml()
    #    else :
    #        raise ASTError(
    #                "tohtml() : No bqitem available for BQuote() node" )
    #    return html

    def dump( self ) :
        if self.textcontents :
            text = self.bqmarkup + self.textcontents.dump()  + \
                   self.newline.dump()
        elif self.empty :
            text = self.bqmarkup + self.empty.dump()  +\
                   self.newline.dump()
        else :
            raise ASTError(
                    "dump() : No bqitem available for BQuote() node" )
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'blockquote: `%s` ' % self.bqmarkup )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        if self.textcontents :
            self.textcontents.show()
        elif self.empty :
            self.empty.show()
        else :
            raise ASTError("show() : No bqitem available for BQuote() node")


class TextContents( Node ) :
    """class to handle `textcontents` grammar."""

    template = None

    def __init__( self, parser, item  ) :
        # item can be Link or Macro or Html or BasicText
        self.parser = parser
        self.textcontents = [ item ]

    def appendcontent( self, item ) :
        # item is Link or Macro or Html or BasicText
        self.textcontents.append( item )

    def extendtextcontents( self, textcontents ) :
        # item is Link or Macro or Html or BasicText
        if isinstance( textcontents, TextContents ) :
            self.textcontents.extend( textcontents.textcontents )

    def children( self ) :
        return self.textcontents

    def tohtml( self ) :
        html = ''.join([ item.tohtml() for item in self.textcontents ])
        return html

    def dump( self ) :
        return ''.join([ item.dump() for item in self.textcontents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'textcontent: ' )
        if showcoord :
            buf.write( ' (at %s)' % self.coord )

        for textcontent in self.textcontents :
            textcontent.show( buf, offset + 2, attrnames, showcoord )


class Link( Node ) :
    """class to handle `link` grammer.
    There are special links, 
        * - Open in new window,
        # - Create an anchor
        + - Image
    """

    l_template = '<a class="etlink" target="%s" href="%s">%s</a>'
    a_template = '<a class="etlink anchor" name="%s">%s</a>'
    img_template = '<img class="et" src="%s" alt="%s" style="%s"/>'

    def __init__( self, parser, link ) :
        self.parser = parser
        app = parser.etparser.app

        # parse the text
        tup  = link[2:-2].split( '|', 1 )
        href = tup and tup.pop(0).strip(' \t') or ''
        text = tup and escape_htmlchars(tup.pop(0)).strip(' \t') or ''

        # parse the href and for special notations
        html   =''
        prefix = href[:1]

        if prefix == '*' :              # Link - Open in new window
            html = self.l_template % ( '_blank', href[1:], text or href[1:] )

        elif href[:1] == '#' :          # Link - Anchor 
            n = 'name="%s"' % href[1:]
            html = self.a_template % (n, text or href[1:] )

        elif prefix == '+' :            # Link - Image (actually no href)
            style = 'float: left;' if href[1:2] == '<' else (
                    'float: right;' if href[1:2] == '>' else ''
                    )
            src = href[1:].strip( '<>' )
            html = self.img_template % ( src, text or src, style )

        elif app and (app.name == 'zeta' and prefix == '@') :
                                        # Link - InterZeta or ZetaLinks
            from eazytext.zetawiki import parse_link2html
            html = parse_link2html( parser.etparser, href, text )

        elif href[:6] == "mailto" :     # Link - E-mail
            if self.parser.etparser.obfuscatemail :
                href = "mailto" + obfuscatemail(href[:6])
                text = obfuscatemail(text or href[:6]) 
            html = self.l_template % ( '', href, text )

        else :
            html = self.l_template % ( '', href, text or href )

        self.contents = [ Content( parser, link, TEXT_LINK, html ) ]

    def children( self ) :
        return self.contents

    def tohtml( self ) :
        return ''.join([ c.html for c in self.contents ])

    def dump( self ) :
        return ''.join([ c.text for c in self.contents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'link: ' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class Macro( Node ) :
    """class to handle `macro` grammer."""

    template = None     # no wrapper with `macro` & <macroname> classes

    def __init__( self, parser, macro  ) :
        self.parser = parser
        self.text = macro
        self.macroobject = build_macro( self, macro )
        self.contents = [
                Content( parser, macro, TEXT_MACRO, self.macroobject.tohtml )
        ]

    def children( self ) :
        return self.contents

    def tohtml( self ) :
        return ''.join([ c.html for c in self.contents ])

    def dump( self ) :
        return ''.join([ c.text for c in self.contents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'macro: `%s`' % self.text )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class Html( Node ) :
    """class to handle `html` grammer."""

    def __init__( self, parser, html_text ) :
        self.parser = parser
        self.text = html_text
        self.html = html_text[2:-2]
        self.html = tt.parsetag( self.html )
        self.contents = [ Content( parser, self.text, TEXT_HTML, self.html ) ]

    def children( self ) :
        return self.contents

    def tohtml( self ) :
        html = ''.join([ c.html for c in self.contents ])
        try :
            if html and self.parser.etparser.stripscript :
                e = lhtml.fromstring( html )
                [ es.getparent().remove(es) for es in e.xpath( '//script' ) ]
                html = lhtml.tostring(e)
        except :
            html = escape_htmlchars( html )
        return html

    def dump( self ) :
        return ''.join([ c.text for c in self.contents ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write( lead + 'html: `%s`' % self.html )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class BasicText( Node ) :
    """class to handle `basictext` grammar."""

    httpuri_template = '<a class="ethttpuri" href="%s"> %s </a>'
    wwwuri_template = '<a class="etwwwuri" href="http://%s"> %s </a>'

    def __init__( self, parser, type, text  ) :
        self.parser = parser
        # self.contents as list of Content object

        if type == TEXT_SPECIALCHAR :
            self.contents = []
            virtuallines = text.split( '\\\\' )
            self.contents.append(
                Content( parser, virtuallines[0], TEXT_SPECIALCHAR,
                         escape_htmlchars( virtuallines[0] ))
            )
            for line in virtuallines[1:] :
                self.contents.append(
                    Content( parser, '\\\\', TEXT_SPECIALCHAR_LB, '<br/>' )
                )
                self.contents.append( Content( parser, line, TEXT_SPECIALCHAR,
                                               escape_htmlchars(line) ))

        elif type == TEXT_HTTPURI :
            self.contents = [ Content( parser, text, type,
                                       self.httpuri_template % (text, text)
                              )
                            ]

        elif type == TEXT_WWWURI :
            self.contents = [ Content( parser, text, type,
                                       self.wwwuri_template % (text,text)
                              )
                            ]
        
        elif type > 2000 :
            self.contents = [ Content( parser, text, type ) ]

        else : # TEXT_CHARPIPE, TEXT_ALPHANUM, TEXT_ESCAPED
            self.contents = [ Content( parser, text, type, text ) ]

    def children( self ) :
        return self.contents

    def tohtml( self ):
        return ''.join([ c.html for c in self.contents ])

    def dump( self ) :
        text = ''
        for c in self.contents :
            text += [ c.text, '~' + c.text ][ c.type == TEXT_ESCAPED ]
        return text

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'basictext :' )

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')


class ParagraphSeparator( Node ) :
    """class to handle `paragraph_separator` grammar."""

    def __init__( self, parser, *args ) :
        self.parser  = parser
        self.newline = None
        self.empty   = None
        self.paragraph_separator = None
        if len(args) == 1 :
            if args[0] == '\n' or args[0] == '\r\n' :
                self.newline = Newline( parser, args[0] )
            elif isinstance( args[0], Empty ) :
                self.empty   = args[0]
        elif len(args) == 2 :
            self.paragraph_separator = args[0]
            self.newline             = Newline( parser, args[1] )

    def children( self ) :
        childnames = [ 'newline', 'empty', 'paragraph_separator' ]
        nodes      = filter(
                        None,
                        [ getattr( self, attr, None ) for attr in childnames ]
                     )
        return tuple(nodes)

    def tohtml( self ) :
        return ''.join([ c.tohtml() for c in self.children() ])

    def dump( self ) :
        return ''.join([ c.dump() for c in self.children() ])

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'paragraph_separator: ')

        if showcoord :
            buf.write( ' (at %s)' % self.coord )
        buf.write('\n')

        for c in self.children() :
            c.show( buf, offset + 2, attrnames, showcoord )


class Empty( Node ) :
    """class to handle `empty` grammar"""

    def __init__( self, parser ) :
        self.parser = parser

    def children( self ) :
        return ()

    def tohtml( self ):
        return ''

    def dump( self ) :
        return ''

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'empty: ')
        buf.write('\n')


class Newline( Node ) :
    """class to handle `newline` grammer"""

    def __init__( self, parser, newline ) :
        self.parser = parser
        self.newline = newline

    def children( self ) :
        return ( self.newline, )

    def tohtml( self ):
        return self.newline

    def dump( self ) :
        return self.newline

    def show( self, buf=sys.stdout, offset=0, attrnames=False,
              showcoord=False ) :
        lead = ' ' * offset
        buf.write(lead + 'newline: ')
        buf.write('\n')
