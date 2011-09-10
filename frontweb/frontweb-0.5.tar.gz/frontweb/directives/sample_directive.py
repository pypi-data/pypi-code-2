from cgi import escape

from docutils import nodes
from docutils.parsers.rst import directives, Directive

class SampleDirective(Directive):
    has_content = True

    def run(self):
        self.assert_has_content()
        text = '<div class="sample"><h5>sample</h5> %s</div>' % self.content
        return [nodes.raw('', text, format='html')]

directives.register_directive("sample", SampleDirective)
