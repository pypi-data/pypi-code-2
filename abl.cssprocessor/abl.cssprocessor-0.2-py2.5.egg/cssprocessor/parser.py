"""
Copyright (c) 2009 Ableton AG

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""
import urlparse

from pyparsing import *


# modeled after the grammar found at
# http://www.w3.org/TR/CSS21/grammar.html



class Node(object):

    def __init__(self, position, tokens):
        self.position = position
        self.tokens = tokens



class StringNode(Node):

    def __init__(self, position, tokens):
        super(StringNode, self).__init__(position, tokens)
        self.text = "".join(tokens)
        self.quotechar = self.text[0]
        self.content = self.text[1:-1]


    @classmethod
    def parse_action(cls, input, loc, tokens):
        start, text, end = tokens
        position = slice(start, end)
        return cls(position, [text])


class URINode(Node):

    def __init__(self, position, tokens):
        super(URINode, self).__init__(position, tokens)
        path = tokens[1]
        if isinstance(path, StringNode):
            self.relative = True
            self.path = path.content
        else:
            # we got a string, which is a URL-terminal
            self.path = path
            protocol, _, path, _, _, _ = urlparse.urlparse(path)
            self.relative = protocol is not None and not path.startswith("/")


    @classmethod
    def parse_action(cls, input, loc, tokens):
        position = slice(tokens[0], tokens[-1])
        return cls(position, tokens[1:-1])



class CSSParser(object):


    def __init__(self, robust=False):
        self.charset = "utf-8"

        escapes = r"\\\\|\\\."
        
        MINUS = Literal("-")
        IDENT = Regex(ur"(-|\*)?([a-zA-Z_-]|(%(escapes)s|[\u0200-\u0377]))([a-zA-Z0-9_-]|(%(escapes)s|[\u0200-\u0377]))*" %
                       dict(escapes=escapes))
        COMMA = Literal(",")
        LBRACE = Literal("{")
        RBRACE = Literal("}")
        LSQUARE = Literal("[")
        RSQUARE = Literal("]")
        LPAREN = Literal("(")
        RPAREN = Literal(")")
        IMPORT_SYM = Keyword("@import")
        CHARSET_SYM = Keyword("@charset")
        MEDIA_SYM = Keyword("@media")
        SEMI = Literal(";")
        HASH = Combine(Literal("#") + Regex("([a-zA-Z0-9_-]|(%(escapes)s))+" %
                                            dict(escapes=escapes)))
        ASTERISK = Literal("*")
        DOT = Literal(".")
        COLON = Literal(":")
        PLUS = Literal("+")
        GREATER = Literal(">")
        SLASH = Literal("/")
        IMPORTANT_SYM = Literal("!") + Keyword("important") # TODO: comment missing
        EQUAL = Literal("=")

        STRING = originalTextFor(quotedString)
        STRING.setParseAction(StringNode.parse_action)

        INCLUDES = Literal("~=")
        DASHMATCH = Literal("|=")
        #FUNCTION = Combine(IDENT+ LPAREN)
        URL = OneOrMore(Word(srange("[!#$%&*-~]"))) # TODO

        URI = originalTextFor(Literal("url(") + (STRING | URL) + Literal(")"))
        URI.setParseAction(URINode.parse_action)

        NUMBER = Regex(r"[0-9]*\.[0-9]+|[0-9]+")
        #NUMBER = Combine(OneOrMore(numlit)) ^ Combine(ZeroOrMore(numlit) + DOT + OneOrMore(numlit))

        PERCENTAGE = Combine(NUMBER + Literal("%"))
        # LENGTH = Combine(NUMBER + (Literal("px") ^ Literal("cm") ^ Literal("mm") ^
        #                                Literal("in") ^ Literal("pt") ^ Literal("pc")))
        LENGTH = Combine(NUMBER + (Literal("px") | Literal("cm") | Literal("mm") |
                                       Literal("in") | Literal("pt") | Literal("pc")))
        EMS = Combine(NUMBER + Literal("em"))
        EXS =Combine(NUMBER + Literal("ex"))
        ANGLE = Combine(NUMBER + (Literal("deg") | Literal("rad") | Literal("grad")))
        TIME = Combine(NUMBER + (Literal("ms") | Literal("s")))
        FREQ = Combine(NUMBER + (Literal("hz") | Literal("khz")))

        # BNF
        medium = IDENT

        import_location = STRING | URI

        import_ = originalTextFor(IMPORT_SYM + import_location + Optional(medium + ZeroOrMore(COMMA + medium)) + SEMI)

        unary_operator = MINUS | PLUS

        operator =  SLASH | COMMA

        hexcolor = HASH

        expr = Forward()

        # this is not according to the
        #function = FUNCTION + ZeroOrMore(Optional(IDENT + EQUAL) + expr) + RPAREN
        funcarg = Optional(IDENT + EQUAL) + expr
        function = IDENT + LPAREN + Group(Optional(delimitedList(funcarg))) + RPAREN

        term = Optional(unary_operator) + ((PERCENTAGE | LENGTH | EMS | EXS | ANGLE | TIME | FREQ | NUMBER)\
                                           | STRING | URI | hexcolor | (function ^ IDENT))

        expr << (term + ZeroOrMore( Optional(operator) +  term))

        property_ = IDENT

        prio = IMPORTANT_SYM

        declaration_value = expr + Optional(prio)
        if robust:
            declaration_value = Optional(declaration_value)

        declaration = property_ + COLON + declaration_value

        element_name = IDENT | ASTERISK

        class_ = Combine(DOT + IDENT)

        attrib = LSQUARE + IDENT + Optional((EQUAL ^ INCLUDES ^ DASHMATCH ) + ( IDENT ^ STRING ) ) + RSQUARE

        pseudo = COLON + ( IDENT ^ (IDENT + LPAREN + Optional(funcarg) + RPAREN))

        simple_selector = (element_name + (ZeroOrMore( HASH | class_ | attrib | pseudo )) |
                           OneOrMore( HASH | class_ | attrib | pseudo))

        combinator = PLUS | GREATER

        selector = simple_selector + ZeroOrMore(Optional(combinator) + simple_selector)

        ruleset = selector + ZeroOrMore(COMMA + selector) + \
                  LBRACE + Optional(declaration) + ZeroOrMore(SEMI + Optional(declaration)) + RBRACE

        media = MEDIA_SYM + medium + ZeroOrMore(COMMA + medium) + LBRACE + ruleset + RBRACE

        charset_declaration = originalTextFor(CHARSET_SYM + STRING + SEMI)
        charset_declaration.setParseAction(self.set_charset)

        # TODO-dir: implement the "page"-stuff
        content = media | ruleset
        # The SEMI below is just because some stylesheets are "dirty"
        if robust:
            content =  content ^ SEMI
        stylesheet = Optional(charset_declaration) +\
                     ZeroOrMore(import_) +\
                     ZeroOrMore(content) +\
                     StringEnd()


        stylesheet.ignore(cppStyleComment)
        stylesheet.ignore(htmlComment)

        for name in ("stylesheet", "import_", "URI", "import_location", "declaration",
                     "declaration_value", "NUMBER", "function", "expr", "LENGTH", "ANGLE",
                     "TIME", "FREQ", "term", "selector", "charset_declaration", "STRING",
                     "IDENT",
                     ):
            setattr(self, name, locals()[name])



    def set_charset(self, input, loc, tokens):
        self.charset = tokens[2].content.lower()


    def parseString(self, string, parseAll=False):
        # we need this because otherwise replacement
        # won't work - it works with the "raw" bytes,
        # not with expanded tabs.
        self.stylesheet.parseWithTabs()
        return self.stylesheet.parseString(string, parseAll)




if __name__ == "__main__":
    import sys
    parser = CSSParser()
    if len(sys.argv) == 2:
        parser.parseString(open(sys.argv[1]).read(), True)
        sys.exit(0)


    print parser.stylesheet.parseString("""@import url(../foo);""", parseAll=True)
