from docutils import nodes
from docutils.parsers.rst import directives, Directive


class SearchDirective(Directive):
    has_content = False

    def run(self):
	text = '''
    	<form method='get' action='/find'>
            <input name='query' style='width: 100%'></input>
	        </form>
	'''
        return [nodes.raw('', text, format='html')]

directives.register_directive("search", SearchDirective)
