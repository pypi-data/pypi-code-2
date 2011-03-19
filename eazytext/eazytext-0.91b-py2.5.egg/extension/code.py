# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : none
# Notes  : none
# Todo   : none
#   1. Unit test case for this extension.

from   pygments            import highlight
from   pygments.formatters import HtmlFormatter
from   pygments.lexers     import guess_lexer, get_lexer_for_filename, \
                                  get_lexer_by_name

from   eazytext.extension  import Extension
from   eazytext            import split_style, constructstyle, lhtml

doc = """
h3. Code

: Description ::
    Syntax highlighting for code-snippet. Highlighting is available for
    [[ http://pygments.org/docs/lexers/ | several-dozen formats ]].
    Property key-value pairs accepts CSS styling attributes.

'' Example ''

> [<PRE {{{ Code C
>   struct process {
>     struct process *next;
>     const char *name;
>     PT_THREAD((* thread)(struct pt *, process_event_t, process_data_t));
>     struct pt pt;
>     unsigned char state;
>   };
> }}} >]

{{{ Code C
struct process {
  struct process *next;
  const char *name;
  PT_THREAD((* thread)(struct pt *, process_event_t, process_data_t));
  struct pt pt;
  unsigned char state;
};
}}}

To highlight a different syntax, supply the syntax name as a parameter like,
> [<PRE {{{ Code <syntax-name> >]

To disable line numbers while highlighting add parameter 'noln'. The default
is to list the line numbers.
> [<PRE {{{ Code <syntax-name> nonl >]
"""


class Code( Extension ) :

    tmpl = '<div class="etext-code" style="%s"> %s </div>'
    script_tmpl = '<style type="text/css"> %s </style>'
    code_tmpl = '<div class="codecont"> %s </div>'

    hashtext = None

    def __init__( self, props, nowiki, *args ) :
        self.nowiki = nowiki
        self.style = constructstyle( props )
        self.lexname = args and args[0].lower() or 'text'
        self.linenos = 'noln' not in args

    def on_prehtml( self ) :
        etparser = self.extnode.parser.etparser
        if self.hashtext == etparser.hashtext :
            return None
        else :
            self.hashtext == etparser.hashtext
            script = HtmlFormatter().get_style_defs('.highlight')
            html = self.script_tmpl % script
            return (-100, html)

    def tohtml( self ) :
        try :
            lexer = get_lexer_by_name( self.lexname )
            code  = highlight( self.nowiki, lexer,
                               HtmlFormatter( linenos=self.linenos ) )
            html  = self.tmpl % ( self.style, (self.code_tmpl % code) )
        except:
            html  = self.nowiki
        return html

Code._doc = doc
