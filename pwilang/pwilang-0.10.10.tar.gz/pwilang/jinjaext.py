from jinja2 import nodes, compiler, parser
from jinja2.ext import Extension
from jinja2 import environmentfilter, Markup, contextfilter, environmentfunction

from os.path import abspath, dirname, join
from os import getcwd

#@environmentfilter
#def abspath (value, env):
#    pass

filters = {
}

import types

def can_assign (self):
    return True
setattr (nodes.Getitem, 'can_assign', can_assign)
setattr (nodes.Getattr, 'can_assign', can_assign)

def parse_assign_target(self, with_tuple=True, name_only=False,
                        extra_end_rules=None):
    """Parse an assignment target.  As Jinja2 allows assignments to
    tuples, this function can parse all allowed assignment targets.  Per
    default assignments to tuples are parsed, that can be disable however
    by setting `with_tuple` to `False`.  If only assignments to names are
    wanted `name_only` can be set to `True`.  The `extra_end_rules`
    parameter is forwarded to the tuple parsing function.
    """
    if self.stream.look ().value == 'in':
        name_only = True

    if name_only:
        token = self.stream.expect('name')
        target = nodes.Name(token.value, 'store', lineno=token.lineno)
    else:
        if with_tuple:
            target = self.parse_tuple(simplified=False,
                                      extra_end_rules=extra_end_rules)
        else:
            target = self.parse_primary()
        target.set_ctx('store')
    if not target.can_assign():
        self.fail('can\'t assign to %r' % target.__class__.
                  __name__.lower(), target.lineno)
    return target

setattr (parser.Parser, 'parse_assign_target', parse_assign_target)

def visit_Getattr(self, node, frame):
    if node.ctx == "load":
        self.write('environment.getattr(')
        self.visit(node.node, frame)
        self.write(', %r)' % node.attr)
    else:
        self.visit(node.node, frame)
        self.write ('.')
        self.write(node.attr)

setattr (compiler.CodeGenerator, 'visit_Getattr', visit_Getattr)

def visit_Getitem(self, node, frame):
    # slices bypass the environment getitem method.
    # We bybasse the environment getitem method since it's pretty useless anyway !
    # if isinstance(node.arg, nodes.Slice):
    self.visit(node.node, frame)
    self.write('[')
    self.visit(node.arg, frame)
    self.write(']')
   # else:
   #     self.write('environment.getitem(')
   #     self.visit(node.node, frame)
   #     self.write(', ')
   #     self.visit(node.arg, frame)
   #     self.write(')')
setattr (compiler.CodeGenerator, 'visit_Getitem', visit_Getitem)


class AbspathExtension (Extension):
    tags = set (['abspath'])

    def __init__ (self, env):
        self.__env = env
        super (AbspathExtension, self).__init__ (env)

    def parse (self, parser):
        filename = parser.filename

        if not filename:
            dir = getcwd ()
        else:
            dir = dirname (parser.filename)

        tag = next (parser.stream) # Removing from the stream
            # the "abspath" tag

        filename = parser.stream.expect ("string")

        while parser.stream.current.type != "block_end":
            pass # We iterate until the end.

        path = abspath (join (dir, filename.value))

        return nodes.Output ([nodes.Const (unicode (path))])

class SassExtension (Extension):
    tags = set (['sass'])

    def __init__ (self, env):
        self.__env = env
        super (SassExtension, self).__init__ (env)

    def parse (self, parser):
        # lineno = parser.stream.next().lineno
    
        acc = ""

        if not parser.filename:
            dir = getcwd ()
        else:
            dir = dirname (parser.filename)
        self._dir = dir

        tag = next (parser.stream) # Removing tag from the stream
        self.args = [tag.value]

        lineno = tag.lineno
        self.lineno = tag.lineno
        while parser.stream.current.type != "block_end":
            self.args.append (parser.stream.current.value)
            next (parser.stream)

        # now we parse the body of the cache block up to `endbody` and
        # drop the needle (which would always be `endbody` in that case)
        body = parser.parse_statements(['name:endsass'], drop_needle=True)

        return nodes.CallBlock (self.call_method ('_parse_css', {}), [], [], body).set_lineno (lineno)

    def _parse_css (self, caller):
        import shlex
        from subprocess import Popen, PIPE

        scss_code = caller ()
        cmd = self.args
        process = Popen (cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        result = process.communicate (input=scss_code)
        if result[1]:
            from jinja2.exceptions import TemplateSyntaxError
            raise TemplateSyntaxError ("Sass Problem: %s" %(result[1]), lineno=self.lineno)

        return result[0]


@environmentfunction
def set_global (env, name, value):
    env.globals[name] = value
    return ""

@environmentfunction
def get_global (env, name):
    return env.globals.get (name, None)

