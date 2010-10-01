from docutils import nodes
from docutils.parsers.rst import Directive, directives

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


class HtmlCodeBlock(Directive):
    """
    *Borrowed from the Sphinx project* (Alright, stolen)

    Docutils does not natively understand a ..code-bock:: directive.  Sphinx
    adds this so that you can get Pygments syntax highlighting of literal
    blocks.

    Sphinx does this in such a way that it can be converted to XML or Latex.
    This is not necessary for our purposes, so we are using a Raw docutils node
    at the end instead of returning a more agnostic node.

    Setting the format to `html` allows the html writer to output the contents.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec = {
        'linenos': directives.flag,
    }

    def run(self):
        code = u'\n'.join(self.content)

        linenos = 'linenos' in self.options
        lexer = get_lexer_by_name(self.arguments[0])
        formatter = HtmlFormatter(linenos=linenos)

        hi_code = highlight(code, lexer, formatter)

        raw = nodes.raw('', hi_code, **{'format': 'html', 'source': None})
        return [raw]

directives.register_directive('code-block', HtmlCodeBlock)
