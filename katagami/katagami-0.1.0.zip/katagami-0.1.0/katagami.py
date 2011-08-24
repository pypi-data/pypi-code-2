#!/usr/bin/env python2
r"""katagami - a very simple xml template engine.
=============================================


# setup...
>>> def testfile(file):
...     if not hasattr(file, 'read'):
...         with open(file) as fp:
...             result = render(fp)
...     else:
...         result = render(file)
...     if sys.platform != 'cli': # IronPython doesn't implement unicode.
...         result = result.encode()
...     return result
>>> def teststr(t):
...     return testfile(StringIO('<html><body>%s</body></html>' % t))
>>> def echo(name, body):
...     with open(os.path.join(tmpdir, name), 'w') as fp:
...         fp.write(body)
>>> def echoxml(name, body):
...     echo(name, '<html><body>%s</body></html>' % body)


Pythonic evaluation
-------------------

Dump the value (call `eval` with attribute value):
>>> teststr('''<python value="'hello, world'"/>''')
'<html><body>hello, world</body></html>'

By the default, xml entities are escaped in `value` attribute of `python` element:
>>> teststr('''<python value="'&lt;p&gt;hello, world&lt;/p&gt;'" escape="false"/>''')
'<html><body><p>hello, world</p></body></html>'


By the default, exceptions are suppressed:
>>> teststr('''<python value="not_found"/>''')
'<html><body></body></html>'

Use `__mode__` for dump exceptions (and see a helpful traceback):
>>> teststr('''<python __mode__="strict" value="not_found"/>''') # fails in IronPython
'<html><pre>Traceback (most recent call last):\n  File "&lt;string&gt;", line 1, in Element "body"\n  File "&lt;string&gt;", line 1, in Element "python"\n  File "&lt;string&gt;", line 1, in Element "python" at line 1-1\n    not_found\nNameError: name \'not_found\' is not defined\n</pre></html>'


Attribute evaluation (attribute value starts with 'python:'):
>>> teststr('''<p class="python:'python-expr'">hello, world</p>''')
'<html><body><p class="python-expr">hello, world</p></body></html>'


Pythonic statements
-------------------

All statements are available in all elements.

`if`, `elif`, `else` statements:
>>> teststr('''
... <p if="0"/>
... <p elif="0"/>
... <p else="">output here</p>
... ''')
'<html><body><p>output here</p></body></html>'


`for` statement (attribute value is Pythonic for style):
>>> teststr('''<p for_="i, j in enumerate(range(3))"><python value="i, j"/></p>''')
'<html><body><p>(0, 0)</p><p>(1, 1)</p><p>(2, 2)</p></body></html>'


`while` statement:
>>> teststr('''
... <python><![CDATA[ i = [1, 2, 3] ]]></python>
... <p while="i">
...     <python value="i[0]"/>
...     <python><![CDATA[ i = i[1:] ]]></python>
... </p>
... ''')
'<html><body><p>1</p><p>2</p><p>3</p></body></html>'


`except` statement:
>>> teststr('''
... <python except="StandardError as e"><![CDATA[ not_found ]]></python>
... <python value="e"/>
... <python except="StandardError"><![CDATA[ not_found ]]></python>
... ''')
"<html><body>name 'not_found' is not defined</body></html>"


`with` statement:
>>> echo('msg.txt', 'hello, world')
>>> teststr('''
... <python with="open(r'%s') as fp">
...     <p><python value="fp.read()"/></p>
...     <p><python value="fp.closed"/></p>
... </python>
... <p><python value="fp.closed"/></p>
... ''' % os.path.join(tmpdir, 'msg.txt'))
'<html><body><p>hello, world</p><p>False</p><p>True</p></body></html>'

Multi items are supported (ex. 'with a, b: pass').
>>> echo('msg2.txt', 'hello, world')
>>> teststr('''
... <python with="open(r'%s') as fp, open(r'%s') as fp2">
...     <p><python value="fp.read()"/></p>
...     <p><python value="fp2.read()"/></p>
... </python>
... ''' % (os.path.join(tmpdir, 'msg.txt'), os.path.join(tmpdir, 'msg2.txt')))
'<html><body><p>hello, world</p><p>hello, world</p></body></html>'


`def` statement (give context by keyword arguments):
>>> teststr('''
... <p def="myfunc">hello, <python value="msg"/></p>
... <python value="myfunc(msg='world')" escape="false"/>
... ''')
'<html><body><p>hello,world</p></body></html>'


Embedded python script
----------------------

`CDATA` is required and `write` is function:
>>> teststr('''
... <python><![CDATA[
...     write('<p>hello, world</p>')
... ]]></python>
... ''')
'<html><body><p>hello, world</p></body></html>'

and escape xml entities:
>>> teststr('''
... <python><![CDATA[
...     write('<p>', 'hello, world', '</p>', escape=True)
... ]]></python>
... ''')
'<html><body>&lt;p&gt;hello, world&lt;/p&gt;</body></html>'


Include python script file:
>>> echo('sub-script.py', '''write('hello, world')''')
>>> echoxml('template.html', '''
...     <p><python src="sub-script.py"/></p>
... ''')
>>> testfile(os.path.join(tmpdir, 'template.html'))
'<html><body><p>hello, world</p></body></html>'

and share variables:
>>> echo('sub-script.py', '''
... global msg 
... msg = 'hello, world'
... msg2 = 'hello, world'
... global myfunc
... def myfunc(name):
...     return 'hello, ' + name
... ''')
>>> echoxml('template.html', '''
...     <python src="sub-script.py"/>
...     <p><python value="msg"/></p>
...     <p>
...         <python value="msg2" __mode__="strict" except="NameError as e"/>
...         <python value="e"/>
...     </p>
...     <p><python value="myfunc('world')"/></p>
... ''')
>>> testfile(os.path.join(tmpdir, 'template.html'))
"<html><body><p>hello, world</p><p>name 'msg2' is not defined</p><p>hello, world</p></body></html>"


Include another template
------------------------

Simply, include all elements:
>>> echoxml('sub-template.html', '<p>hello, world</p>')
>>> echoxml('template.html', '<python template="sub-template.html"/>')
>>> testfile(os.path.join(tmpdir, 'template.html'))
'<html><body><html><body><p>hello, world</p></body></html></body></html>'

Then include a part of elements:
>>> echoxml('sub-template.html', '<p id="myid">hello, world</p>')
>>> echoxml('template.html',
...      '<python template="sub-template.html" fragment="myid"/>')
>>> testfile(os.path.join(tmpdir, 'template.html'))
'<html><body><p id="myid">hello, world</p></body></html>'

And share variables:
>>> echoxml('sub-template.html', '''
...     <p id="myid">hello, world</p>
...     <python><![CDATA[
...         global msg
...         msg = 'hello, world'
...     ]]></python>
...     <p def="global myfunc"><python value="text"/></p>
... ''')
>>> echoxml('template.html', '''
...     <python template="sub-template.html" fragment="myid"/>
...     <p><python value="msg"/></p>
...     <python value="myfunc(text='hello, world')" escape="false"/>
... ''')
>>> testfile(os.path.join(tmpdir, 'template.html'))
'<html><body><p id="myid">hello, world</p><p>hello, world</p><p>hello, world</p></body></html>'


Techniques and notices
----------------------

This module is wrote under assuming that sys.setdefaultencoding('utf-8').

This module works with null xml namespace, but doesn't remove any namespace:
>>> testfile(StringIO('''<?xml version="1.0"?>
... <root xmlns    = "http://default-namespace.org/"
...       xmlns:py = "http://www.python.org/ns/">
...     <py:elem1 py:if="0"/>
...     <elem2 xmlns="" />
...     <py:elem3 if="0"/>
... </root>'''))
'<?xml version="1.0"?>\n<root xmlns="http://default-namespace.org/" xmlns:py="http://www.python.org/ns/"><py:elem1 py:if="0"/><elem2 xmlns=""/></root>'


The namespace is flat like python module and nested in function:
>>> teststr('''
... <python><![CDATA[ a = b = 0 ]]></python>
... <python def="myfunc"><![CDATA[
...     global a
...     write('a = %d\\n' % a)
...     write('b = %d\\n' % b)
...     a = b = 1
... ]]></python>
... <python value="myfunc()"/>
... <python value="a, b"/>
... ''')
'<html><body>a = 0\nb = 0\n(1, 0)</body></html>'


By the default, White spaces and comments are stripped:
>>> teststr('''<p><!-- comment --> hello, world </p>''')
'<html><body><p>hello, world</p></body></html>'

Use `direct` mode:
>>> teststr('''<p __mode__="direct"><!-- comment --> hello, world </p>''')
'<html><body><p><!-- comment --> hello, world </p></body></html>'


The attribute order is important:
>>> teststr('''
... <p if="0" for_="i in range(2)"><python value="i"/></p>
... <p for_="i in range(2)" if="i > 0"><python value="i"/></p>
... ''')
'<html><body><p>1</p></body></html>'


If you need closing tag such as `textarea`, then write below:
>>> teststr('''<textarea><python/></textarea>''')
'<html><body><textarea></textarea></body></html>'


Entities will not be expanded:
>>> teststr('''&nbsp;&unknown_entity;''')
'<html><body>&nbsp;&unknown_entity;</body></html>'


Special variables are available in some cases:
 * __file__ = str -> path of file (template or script)
 * __noloop__ = bool -> whether loop statements executed
                        (and when not `strict` mode)
 * _ = object -> temporary value when extracting variables

Special utility functions are available, see default_namespace.

Special string codecs:
 * percent, uri - known as encodeURIComponent, decodeURIComponent
 * xml - escape '<', '>', '&'

For more information, see `Element` class implementation.
"""
__version__ = '0.1.0'
__author__ = __author_email__ = 'chrono-meter@gmx.net'
__license__ = 'PSF'
__all__ = ('Renderer', 'render', 'Template')
DEBUG = False

import sys
import os
import re
import collections
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from xml.parsers import expat
from xml.sax import saxutils
import distutils.util
import math
import itertools
import traceback
import linecache
import encodings
import codecs
import ast #; assert ast.__version__ == 82160


class Element(object):

    __slots__ = ('parent', 'name', 'attributes', 'children', 'column',
                 'firstlineno', 'lineno')

    def __init__(self, parent, name='', attributes={}):
        self.parent = parent
        self.name = name
        self.attributes = attributes
        self.children = []
        self.column = self.firstlineno = self.lineno = -1

    def evaluate(self, env, globals=None, locals=None):
        """
        env = {
            'globals': {}, # global namespace
            'locals': {}, # local namespace
            'mode': (str, ...), # see .handle_attr_flags(),
            'errors': (Exception, ...), # doesn't suppress these errors,
            'stack': [{
                'condition': bool, # if, elif, else condition
                'onexit': (lambda: None, ...), # handlers on exit
                'onerror': (lambda: None, ...), # handlers on error
                'suppress_errors': bool, # suppress any error
                'set_result': bool, # add evaluate() result to env['result']
                }, ...],
            'includes': (str, ...), # pathname of ancestor templates
            'stdout': StringIO(), # output buffer for write(),
            'result': str, # root.evaluate() returns this if set,
            'fragment': str, # 
            }
        """
        assert self.parent is None

        if globals is None:
            env['globals'] = env['locals'] = {}
        elif locals is None:
            env['globals'] = env['locals'] = globals
        else:
            env['globals'], env['locals'] = globals, locals

        env.setdefault('mode', ())
        env.setdefault('errors', ())
        env.setdefault('stack', [])
        env.setdefault('includes', ())

        if 'stdout' not in env:
            env['stdout'] = StringIO()
            def write(*a, **k):
                for i in a:
                    i = saxutils.escape(i) if k.get('escape') else i
                    env['stdout'].write(i)
            env['globals']['write'] = write

        env['stack'].append({'self': self})
        try:
            result = self._stringify_children(env)
        finally:
            env['stack'].pop()
        return env.pop('result', result)

    def _evaluate(self, env):
        __traceback_supplement__ = \
            (env['globals']['__file__'], self.lineno,
             'Element "%s"' % self.name, None, )

        saved = self.attributes.copy(), env['mode']
        env['stack'].append({'self': self})
        try:
            result = ''
            try:
                result = self._stringify(env)
            except Exception as e:
                env['stack'][-1].pop('onexit', None)
                for i in env['stack'][-1].get('onerror', ()): i()

                if env['stack'][-1].get('suppress_errors'): # `with` given
                    pass
                elif isinstance(e, env.get('errors', ())): # user given
                    raise
                elif 'strict' in env['mode']:
                    raise
                else:
                    result = saxutils.escape(format_exc())
                    # special hack for html
                    try:
                        rootelem = env['stack'][1]['self']
                    except LookupError:
                        pass
                    else:
                        name = rootelem.name.lower()
                        if name == 'html' or name.endswith(':html'):
                            result = '<pre>' + result + '</pre>'

                if DEBUG: raise

            finally:
                if env['stack'][-1].get('set_result'):
                    env['result'] = env.get('result', '') + result
            return result
        finally:
            for i in env['stack'][-1].get('onexit', ()): i()
            env['stack'].pop()
            self.attributes, env['mode'] = saved

    def _stringify(self, env):
        # syntax attributes
        clear_condition = True
        for name in list(self.attributes):
            handler = getattr(self, 'handle_attr_' + name, None)
            if not hasattr(handler, '__call__'):
                continue
            if getattr(handler, 'conditional', False):
                clear_condition = False
            if getattr(handler, 'volatile', True):
                value = self.attributes.pop(name)
            else:
                value = self.attributes[name]
            __traceback_supplement__ = \
                (env['globals']['__file__'], self.lineno,
                 'Attribute "%s"' % name, value, )
            result = handler(env, name, value)
            del __traceback_supplement__
            if result is not None:
                return result
        if clear_condition:
            try:
                del env['stack'][-2]['condition']
            except LookupError:
                pass

        # special elements
        handler = getattr(self, 'handle_elem_' + self.name, None)
        if hasattr(handler, '__call__'):
            result = handler(env)
            if result is not None:
                return result

        # dump
        opening, closing = self._tag(env)
        return opening + self._stringify_children(env) + closing

    def _tag(self, env):
        opening, closing = '<%s' % self.name, ''
        for k in self.attributes:
            v = self.eval_attr(env, k)
            if k in ('id', 'name', ) and v:
                env['stack'][-1]['set_result'] = v == env.get('fragment')
            opening += ' %s=%s' % (k, saxutils.quoteattr(v))
        if self.children:
            opening += '>'
            closing += '</%s>' % self.name
        else:
            opening += '/>'
        return opening, closing

    def _stringify_children(self, env, **handlers):
        result = ''
        for i in self.children:
            if isinstance(i, self.__class__):
                name = 'element'
            elif isinstance(i, dict):
                name = i.get('name', 'default')
            else:
                name = 'text'

            if name in handlers:
                result += handlers[name](env, i['textContent'])
            elif name == 'text':
                if 'direct' not in env['mode']:
                    i = i.strip()
                result += saxutils.escape(i)
            elif name == 'entity':
                result += i['textContent']
            elif name == 'element':
                result += i._evaluate(env)
            elif name == 'comment':
                if 'direct' in env['mode']:
                    result += '<!--' + i['textContent'] + '-->'
            elif name == 'cdata':
                result += '<![CDATA[' + i['textContent'] + ']]>'
            else:
                if not env['includes']: # not included
                    result += i['textContent']

        return result

    def _newscope(self, env, context={}):
        globals, locals = env['globals'], env['locals']
        if globals is locals:
            locals = {}
        else:
            locals = locals.copy()
        locals.update(context)
        return globals, locals

    def _doexec(self, env, expr, globals=None, locals=None):
        env['locals']['__traceback_supplement__'] = \
            (env['globals']['__file__'], 0,
             'Element "%s" at line %d-%d' % (
                self.name, self.firstlineno, self.lineno),
             expr, )
        if globals is None:
            exec expr in env['globals'], env['locals']
        elif locals is None:
            exec expr in globals
        else:
            exec expr in globals, locals

    def _doeval(self, env, expr, globals=None, locals=None):
        env['locals']['__traceback_supplement__'] = \
            (env['globals']['__file__'], 0,
             'Element "%s" at line %d-%d' % (
                self.name, self.firstlineno, self.lineno),
             expr, )
        if globals is None:
            return eval(expr, env['globals'], env['locals'])
        elif locals is None:
            return eval(expr, globals)
        else:
            return eval(expr, globals, locals)

    def _capture_exec(self, env, expr, globals=None, locals=None):
        fp = env['stdout']
        fp.reset()
        fp.truncate()
        self._doexec(env, expr, globals, locals)
        return fp.getvalue()

    def _joinpath(self, env, *names):
        dirname = env['globals']['__file__']
        if os.path.isfile(dirname):
            dirname = os.path.dirname(dirname)
        return os.path.join(dirname, *names)

    def eval_attr(self, env, name):
        """<* *="python:expression"/>"""
        value = self.attributes[name]
        if value.startswith('python:'):
            __traceback_supplement__ = \
                (env['globals']['__file__'], self.lineno,
                 'Attribute "%s"' % name, value, )
            value = str(self._doeval(env, value[7:]))
        return value

    def handle_attr___mode__(self, env, name, expr):
        """<* __mode__="space separated keywords"/>
        strict -> don't pass exceptions
        direct -> don't remove comments and white spaces
        """
        env['mode'] = tuple(re.split('\W+', expr))

    def _handle_attr_if(self, env, name, expr):
        """<* if="expression"/>"""
        if expr:
            try:
                env['stack'][-2]['condition'] = bool(self._doeval(env, expr))
            except env.get('errors', ()):
                raise
            except Exception as e:
                if 'strict' in env['mode']:
                    raise
                env['stack'][-2]['condition'] = False
        else:
            env['stack'][-2]['condition'] = False
        if env['stack'][-2].get('condition') == False:
            return ''

    handle_attr_if = _handle_attr_if

    def handle_attr_elif(self, env, name, expr):
        """<* elif="expression"/>"""
        if env['stack'][-2].get('condition') is None \
           and 'strict' in env['mode']:
            raise SyntaxError(
                'isolated `elif` found at %d,%d' % (self.column, self.lineno))
        if env['stack'][-2].get('condition') in (True, None):
            return ''
        return self._handle_attr_if(env, name, expr)

    def handle_attr_else(self, env, name, expr):
        """<* else="ignore"/>"""
        if env['stack'][-2].get('condition') is None \
           and 'strict' in env['mode']:
            raise SyntaxError(
                'isolated `else` found at %d,%d' % (self.column, self.lineno))
        if env['stack'][-2].get('condition') in (True, None):
            return ''
        env['stack'][-2]['condition'] = None

    handle_attr_if.conditional = True
    handle_attr_elif.conditional = True
    handle_attr_else.conditional = True

    def handle_attr_for_(self, env, name, expr):
        """<* for_="symbols in iterable"/>"""
        result = []

        symbols, expr = re.split('\s+in\s+', expr.strip())
        for item in self._doeval(env, expr):
            variables = {'_': item}
            self._doexec(env, '%s = _' % symbols, {}, variables)
            env['locals'].update(variables)
            result.append(self._evaluate(env))

        if 'strict' not in env['mode']:
            env['locals']['__noloop__'] = bool(result)
        return ''.join(result)

    def handle_attr_while(self, env, name, expr):
        """<* while="expression"/>"""
        result = []
        while bool(self._doeval(env, expr)):
            result.append(self._evaluate(env))
        if 'strict' not in env['mode']:
            env['locals']['__noloop__'] = bool(result)
        return ''.join(result)

    def handle_attr_except(self, env, name, expr):
        """<* except="errors as symbol"/>
        <* except="errors"/>
        """
        try:
            expr, symbols = re.split('\s+as\s+', expr.strip())
        except ValueError:
            symbols = ''

        target = self._doeval(env, expr)

        def onerror():
            e = sys.exc_value
            if not isinstance(e, target):
                return
            env['stack'][-1]['suppress_errors'] = True
            if symbols:
                variables = {'_': e}
                self._doexec(env, '%s = _' % symbols, {}, variables)
                env['locals'].update(variables)
        env['stack'][-1]['onerror'] = \
            env['stack'][-1].get('onerror', ()) + (onerror, )

    def handle_attr_with(self, env, name, expr):
        """<* with="context as symbol"/>
        <* with="context"/>
        """
        contexts = []
        def onexit():
            for i in reversed(contexts):
                i.__exit__(None, None, None)
        def onerror():
            suppress = False
            try:
                etype, value, tb = sys.exc_info()
                for i in reversed(contexts):
                    suppress = i.__exit__(etype, value, tb)
                    if suppress:
                        etype, value, tb = None
            finally:
                del etype, value, tb
            return suppress

        try:
            root = ast.parse('with %s: pass' % expr)
            node = root.body[0]
            while isinstance(node, ast.With):
                expr = astcompile(node.context_expr, '<string>', 'eval')
                contexts.append(self._doeval(env, expr))
                enter = contexts[-1].__enter__()
                if node.optional_vars:
                    expr = ast.Assign(
                        targets=[node.optional_vars],
                        value=ast.Name(id='_', ctx=ast.Load()),
                        )
                    expr = astcompile(expr, '<string>', 'exec')
                    variables = {'_': enter}
                    self._doexec(env, expr, {}, variables)
                    env['locals'].update(variables)
                node = node.body[0]
        except:
            if onerror():
                return ''
            else:
                raise

        env['stack'][-1]['onexit'] = \
            env['stack'][-1].get('onexit', ()) + (onexit, )
        def _onerror():
            env['stack'][-1]['suppress_errors'] = bool(onerror())
        env['stack'][-1]['onerror'] = \
            env['stack'][-1].get('onerror', ()) + (_onerror, )

    def handle_attr_def(self, env, name, expr):
        """<* def="funcname"/>"""
        attributes = self.attributes.copy()

        def function(**context):
            saved = self.attributes, env['locals']
            self.attributes = attributes.copy()
            env['globals'], env['locals'] = self._newscope(env, context)
            try:
                return self._evaluate(env)
            finally:
                self.attributes, env['locals'] = saved

        try:
            scope, symbol = expr.split()
        except ValueError:
            scope, symbol = 'local', expr
        function.__name__ = str(symbol.strip())

        if scope == 'global':
            env['globals'][function.__name__] = function
        elif scope == 'local':
            env['locals'][function.__name__] = function
        else:
            raise SyntaxError('invalid scope')

        return ''

    def handle_elem_python(self, env):
        """<python value="expression" escape="true">ignore</python>
        <python template="filename.html" fragment="string">ignore</python>
        <python src="filename.py" escape="false">ignore</python>
        <python escape="false"><![CDATA[python script]]></python>
        Optionally attributes:
            escape -> escape XML entities. (default=true with value,
                                                    false with others)
        """
        escape = 'false'

        if 'value' in self.attributes:
            escape = 'true'
            try:
                result = str(self._doeval(env, self.attributes['value']))
            except env.get('errors', ()):
                raise
            except Exception as e:
                if 'strict' in env['mode']:
                    raise
                result = ''

        elif 'template' in self.attributes:
            _env = env.copy()
            _env['includes'] = \
                _env['includes'] + (env['globals']['__file__'], )
            _env['fragment'] = self.attributes.get('fragment')

            __file__ = env['globals']['__file__']
            env['globals']['__file__'] = \
                self._joinpath(env, self.attributes['template'])
            try:
                renderer = env['renderer']()
                renderer.ElementFactory = self.__class__
                with open(env['globals']['__file__'], 'r') as fp:
                    renderer.parse(fp)
                result = renderer.element.evaluate(_env, *self._newscope(env))
            finally:
                env['globals']['__file__'] = __file__

        elif 'src' in self.attributes:
            __file__ = env['globals']['__file__']
            env['globals']['__file__'] = \
                self._joinpath(env, self.attributes['src'])
            try:
                with open(env['globals']['__file__'], 'Ur') as fp:
                    expr = fp.read()
                result = self._capture_exec(env, expr, *self._newscope(env))
            finally:
                env['globals']['__file__'] = __file__

        else:
            def cdata(env, expr):
                if 'strict' not in env['mode'] \
                   and re.match('^\s*?[ \t]+\S', expr):
                    expr = 'if 1:\n' + expr.rstrip()
                    # IronPython is bad at indentation and newline.
                return self._capture_exec(env, expr)

            result = self._stringify_children(env, cdata=cdata)

        escape = self.attributes.get('escape', escape).strip()
        if distutils.util.strtobool(escape):
            result = saxutils.escape(result)
        return result


class Renderer(object):

    ElementFactory = Element
    filename = ''

    def __init__(self, file=None):
        if file:
            self.parse(file)

    def __call__(self, file, context=None, environ=None):
        self.parse(file)
        return self.render(context, environ)

    def render(self, context=None, environ=None):
        # `Element` is reusable, but not thread safe.
        #element = copy.deepcopy(element)
        if context is None:
            context = {}
        context['__file__'] = self.filename
        if environ is None:
            environ = {}
        environ['renderer'] = self.__class__
        return self.element.evaluate(environ, context)

    def parse(self, file):
        self.filename = getattr(file, 'name', '<string>')

        self.element = self.ElementFactory(None)
        self.parser = self._parser()
        try:
            self.parser.ParseFile(file)
        finally:
            del self.parser

        #cache[self.ElementFactory, self.filename] = self.element

    def _parser(self):
        # http://docs.python.org/library/pyexpat.html
        result = expat.ParserCreate()
        result.ordered_attributes = True
        result.returns_unicode = True
        result.DefaultHandler = self.DefaultHandler
        result.StartElementHandler = self.StartElementHandler
        result.EndElementHandler = self.EndElementHandler
        result.StartCdataSectionHandler = self.StartCdataSectionHandler
        result.EndCdataSectionHandler = self.EndCdataSectionHandler
        result.CharacterDataHandler = self.CharacterDataHandler
        result.CommentHandler = self.CommentHandler
        result.UseForeignDTD() # inhibit expansion of entities
        return result

    def StartElementHandler(self, name, attributes):
        self.element = self.ElementFactory(self.element, name,
            collections.OrderedDict(zip(attributes[::2], attributes[1::2])))
        self.element.column = self.parser.CurrentColumnNumber
        self.element.firstlineno = self.parser.CurrentLineNumber

    def EndElementHandler(self, name):
        self.element.lineno = self.parser.CurrentLineNumber
        element = self.element
        self.element = self.element.parent
        self.element.children.append(element)

    def StartCdataSectionHandler(self):
        self.cdata = []

    def EndCdataSectionHandler(self):
        self.element.children.append(
            {'name': 'cdata', 'textContent': ''.join(self.cdata)})
        del self.cdata

    def DefaultHandler(self, data):
        if data.startswith('&') and data.endswith(';'):
            self.element.children.append(
                {'name': 'entity', 'textContent': data})
        else:
            self.element.children.append({'textContent': data})

    def CharacterDataHandler(self, data):
        if not hasattr(self, 'cdata'):
            self.element.children.append(data)
        else:
            self.cdata.append(data)

    def CommentHandler(self, data):
        self.element.children.append({'name': 'comment', 'textContent': data})


def render(file, context={}, environ=None):
    renderer = Renderer(file)
    ctx = default_namespace.copy()
    ctx.update(context)
    return renderer.render(ctx, environ)


class Template(object):

    def __init__(self, *path):
        self._path = list(path)
        self._suffixes = ('.html', '.htm', '.tmpl')
        self._namespace = default_namespace.copy()
        self._environ = {}
        self._Element = Element

    def _Renderer(self, filename):
        def result(_context={}, **kwargs):
            renderer = Renderer()
            renderer.ElementFactory = self._Element
            ctx = self._namespace.copy()
            ctx.update(_context)
            ctx.update(kwargs)
            with open(filename, 'r') as fp:
                return renderer(fp, ctx, self._environ.copy())
        return result

    def __getattr__(self, name):
        for path in self._path:
            for root, dirs, files in os.walk(os.path.abspath(path)):
                del dirs[:]
                for file in files:
                    basename, ext = os.path.splitext(file)
                    if basename == name and ext.lower() in self._suffixes:
                        return self._Renderer(os.path.join(root, file))
        result = self.__class__(*[os.path.join(i, name) for i in self.path])
        result._suffixes = self._suffixes
        result._namespace = self._namespace
        result._environ = self._environ
        result._Element = self._Element
        return result


def astcompile(expr, filename='<unknown>', mode='exec'):
    if mode == 'eval':
        node = ast.Expression(body=expr)
    elif isinstance(expr, list):
        node = ast.Module(body=expr)
    else:
        node = ast.Module(body=[expr])
    return compile(ast.fix_missing_locations(node), filename, mode)


def extract_tb(tb):
    f = tb.tb_frame
    co = f.f_code
    if '__traceback_supplement__' in f.f_locals:
        filename, lineno, name, line = f.f_locals['__traceback_supplement__']
        if not filename:
            filename = co.co_filename
        if lineno <= 0:
            lineno = tb.tb_lineno
        if not name:
            name = co.co_name
        if not line:
            linecache.checkcache(filename)
            line = linecache.getline(filename, lineno, f.f_globals)
        elif line.count('\n') > 1:
            try:
                line = line.splitlines()[tb.tb_lineno - 1]
            except LookupError:
                line = None
    else:
        return
    #    filename = co.co_filename
    #    lineno = tb.tb_lineno
    #    name = co.co_name
    #    linecache.checkcache(filename)
    #    line = linecache.getline(filename, lineno, f.f_globals)
    line = line.strip() if line else None
    return filename, lineno, name, line


def format_exc(limit=None):
    """see traceback.format_exc"""
    if limit is None:
        if hasattr(sys, 'tracebacklimit'):
            limit = sys.tracebacklimit
    result = ['Traceback (most recent call last):\n']
    try:
        etype, value, tb = sys.exc_info()
        tblist = []
        n = 0
        while tb is not None and (limit is None or n < limit):
            info = extract_tb(tb)
            if info:
                tblist.append(info)
            tb = tb.tb_next
            n = n + 1
        result = result + traceback.format_list(tblist)
        result = result + traceback.format_exception_only(etype, value)
    finally:
        etype = value = tb = None
    return ''.join(result)


#if __debug__:
#    from traceback import format_exc


def walk(callable, initial, sentinel=None):
    while initial and initial != sentinel:
        yield initial
        initial = callable(initial)


Nogiven = object()
class ProtectDict(object):

    def __init__(self, __o, *args, **kwargs):
        self.__dict__.update(locals())

    def __enter_(self):
        if self.args or self.kwargs:
            self.saved = {}
            items = itertools.chain(zip(self.args, [Nogiven] * len(self.args)),
                                    self.kwargs.items())
            for name, value in items:
                self.saved[name] = self.__o.get(name, Nogiven)
                if value is not Nogiven:
                    self.__o[name] = value
        else:
            self.saved = self.__o.copy()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.args or self.kwargs:
            for name in itertools.chain(self.args, self.kwargs):
                value = self.saved[name]
                if value is not Nogiven:
                    self.__o[name] = value
                else:
                    del self.__o[name]
        else:
            self.__o.clear()
            self.__o.update(self.saved)


def open2(filename, mode='r', bufsize=-1):
    if not mode.lstrip('U').startswith('r'):
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
    return open(filename, mode, bufsize)


def fssafe(filename, strict=False, replace=None):
    FORBIDDEN = '\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D'\
                '\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B'\
                '\x1C\x1D\x1E\x1F"*/:<>?\\|\x7f'
    result = ''
    for _c in filename:
        c = unichr(_c)
        if c in FORBIDDEN or (strict and not c.isalnum()):
            _c = replace(_c) if replace else ''
        result += _c
    return result


def overlay(*args):
    """
    >>> list(overlay((0, ), (1, 1, ), (2, 2, 2, ), (3, 3, 3, 3, ), ))
    [0, 1, 2, 3]
    """
    n = 0
    for it in args:
        for i, obj in enumerate(it):
            if n <= i:
                yield obj
                n += 1


def ring(iterable, beginning, reversed=False):
    """
    >>> list(ring(list(range(10)), 5))
    [5, 6, 7, 8, 9, 0, 1, 2, 3, 4]
    >>> list(ring(list(range(10)), 5, reversed=True))
    [5, 4, 3, 2, 1, 0, 9, 8, 7, 6]
    """
    length = len(iterable)
    if not reversed:
        it = itertools.chain(xrange(beginning, length), xrange(0, beginning))
    else:
        it = itertools.chain(
            xrange(beginning, -1, -1), xrange(length - 1, beginning, -1))
    for i in it:
        yield iterable[i]


def parity(i, marks=('even', 'odd')):
    """
    >>> parity(10)
    'even'
    >>> parity(50, ('un', 'deux', 'trois'))
    'trois'
    """
    return marks[i % len(marks)]


def toggle(**kwargs):
    """Utility function for html class attribute.
    >>> toggle(a=True, b=False, c=True)
    'a c'
    >>> toggle(a=False, b=False, c=True)
    'c'
    """
    return ' '.join(k for k, v in sorted(kwargs.items()) if v)


def countup(obj):
    """
    >>> countup(10)
    10
    >>> countup([1, ] * 10)
    10
    >>> countup(xrange(10))
    10
    """
    if isinstance(obj, int):
        return obj
    else:
        try:
            return len(obj)
        except TypeError:
            length = 0
            for i in obj:
                length += 1
            return length


def limit(number, *limitations):
    """
    >>> limit(10, 0, 9)
    9
    >>> limit(-1, 0, 9)
    0
    >>> limit(5, 0, 9)
    5
    """
    leftmost = min(*limitations)
    rightmost = max(*limitations)
    return max(leftmost, min(number, rightmost))


def _normpage(length, index, divisor):
    if length <= 0:
        return 0, 0
    pages = int(math.ceil(float(length) / divisor))
    if index < 0:
        index = (pages + index) % pages
    return pages, index


def paginate_items(iterable_or_length, index, divisor):
    """
    >>> items = range(100)
    >>> list(paginate_items(items, 0, 10))
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> list(paginate_items(items, 4, 10))
    [40, 41, 42, 43, 44, 45, 46, 47, 48, 49]
    >>> list(paginate_items(items, 10, 10))
    []
    >>> list(paginate_items(items, -1, 10))
    [90, 91, 92, 93, 94, 95, 96, 97, 98, 99]
    """
    if isinstance(iterable_or_length, int):
        length = iterable_or_length
        pages, index = _normpage(length, index, divisor)
        for i in xrange(divisor * index, divisor * (index + 1)):
            yield i

    elif hasattr(iterable_or_length, '__getitem__'):
        length = len(iterable_or_length)
        pages, index = _normpage(length, index, divisor)
        for i in xrange(divisor * index, divisor * (index + 1)):
            try:
                yield iterable_or_length[i]
            except LookupError:
                break

    else:
        if index < 0:
            raise ValueError('negative index is not supported')
        for i, o in enumerate(iterable_or_length):
            if divisor * index > i:
                continue
            if i >= divisor * (index + 1):
                break
            yield o


def paginate_index(iterable_or_length, index, divisor, width=5,
                   left='&laquo;', right='&raquo;'):
    """
    >>> items = range(100)
    >>> list(paginate_index(items, 1, 10))
    [(0, '1', 'prev'), (1, '2', 'current'), (2, '3', 'next'), (3, '4', ''), (4, '5', ''), (5, '6', ''), (9, '&raquo;', 'rightmost')]
    >>> list(paginate_index(items, 5, 10))
    [(0, '&laquo;', 'leftmost'), (2, '3', ''), (3, '4', ''), (4, '5', 'prev'), (5, '6', 'current'), (6, '7', 'next'), (7, '8', ''), (9, '&raquo;', 'rightmost')]
    """
    length = countup(iterable_or_length)
    pages, index = _normpage(length, index, divisor)

    if pages < 2: # navigation is not required
        return
    elif pages <= width:
        for i in xrange(pages):
            yield i, str(i + 1), toggle(prev=i == (index - 1),
                                        current=i == index,
                                        next=i == (index + 1))
    else:
        if index > pages - width:
            median = pages - float(width) / 2
        elif index < width:
            median = float(width) / 2
        else:
            median = index
        leftmost = 0
        rightmost = pages - 1
        begin = int(limit(median - float(width) / 2, leftmost, rightmost))
        end = int(limit(begin + width, leftmost, rightmost))
        if left and begin != leftmost:
            yield leftmost, left, 'leftmost'
        for i in xrange(begin, end + 1):
            yield i, str(i + 1), toggle(prev=i == (index - 1),
                                        current=i == index,
                                        next=i == (index + 1))
        if right and end != rightmost:
            yield rightmost, right, 'rightmost'


def parse_ua(text):
    result = []
    for whole, product, comment in re.findall('((\S+)\s*(\([^)]+\))?)', text):
        result.append(whole)
        result.append(product)
        result.append(product.split('/')[0])
        for item in re.split(';\s*', comment[1:-1]):
            result.append(item)
            result.append(re.sub('(:?[^a-zA-Z])[\d.]+$', '', item))
    _result = set()
    for i in result:
        i = i.strip()
        if i:
            _result.add(i)
            _result.add(i.lower())
    return _result


default_namespace = {
    'render': render,
    'open2': open2,
    'fssafe': fssafe,
    'overlay': overlay,
    'ring': ring,
    'parity': parity,
    'toggle': toggle,
    'limit': limit,
    'paginateItems': paginate_items,
    'paginateIndex': paginate_index,
    'parseUserAgent': parse_ua,
    #and others such as web.utils ...
    }


class Codec(object):
    """
    >>> import base64
    >>> class TestCodec(Codec):
    ...     name = 'test'
    ...     def _encode(self, input, errors):
    ...         return base64.encodestring(input)
    ...     def _decode(self, input, errors):
    ...         return base64.decodestring(input)
    >>> test = TestCodec()
    >>> test.register()
    >>> 'abc'.encode('test')
    'YWJj\\n'
    >>> test.unregister()
    """
    name = '' # codec name
    aliases = () # alias names

    def register(self):
        sys.modules['encodings.' + self.name] = self
        for alias in self.aliases:
            encodings.aliases.aliases[alias] = self.name

    def unregister(self):
        sys.modules.pop('encodings.' + self.name, None)
        for alias in self.aliases:
            encodings.aliases.aliases.pop(alias, None)

    def getregentry(self):
        return codecs.CodecInfo(
            name=self.name,
            encode=self.encode,
            decode=self.decode,
            #incrementalencoder=self.IncrementalEncoder,
            #incrementaldecoder=self.IncrementalDecoder,
            #streamwriter=self.StreamWriter,
            #streamreader=self.StreamReader,
            )

    def _encode(self, input, errors='strict'):
        raise NotImplemented

    def _decode(self, input, errors='strict'):
        raise NotImplemented

    def encode(self, input, errors='strict'):
        result = self._encode(input, errors)
        if isinstance(result, tuple):
            return result
        else:
            return result, len(input)

    def decode(self, input, errors='strict'):
        result = self._decode(input, errors)
        if isinstance(result, tuple):
            return result
        else:
            return result, len(input)

    #@property
    #def IncrementalEncoder(self):
    #    __module__ = self
    #    class IncrementalEncoder(codecs.IncrementalEncoder):
    #        def encode(self, input, final=False):
    #            return __module__.encode(input)[0]
    #    return IncrementalEncoder

    #@property
    #def IncrementalDecoder(self):
    #    __module__ = self
    #    class IncrementalDecoder(codecs.IncrementalDecoder):
    #        def decode(self, input, final=False):
    #            return __module__.decode(input)[0]
    #    return IncrementalDecoder

    #@property
    #def StreamReader(self):
    #    __module__ = self
    #    class StreamReader(codecs.StreamReader):
    #        def decode(self, input, errors='strict'):
    #            return __module__.decode(input, errors)
    #    return StreamReader

    #@property
    #def StreamWriter(self):
    #    __module__ = self
    #    class StreamWriter(codecs.StreamWriter):
    #        def decode(self, input, errors='strict'):
    #            return __module__.decode(input, errors)
    #    return StreamWriter


class PercentEscapeCodec(Codec):
    """
    >>> u'a, b, c'.encode('percent')
    'a,%20b,%20c'
    >>> u'?query'.encode('uri')
    '%3Fquery'
    >>> 'q%3Dkeyword'.decode('uri')
    u'q=keyword'
    """

    name = 'percent'
    aliases = ('uri', )

    def _encode(self, input, errors='strict'):
        assert isinstance(input, unicode)
        assert errors == 'strict'
        input = input.encode('utf-8')
        return re.sub('([^0-9A-Za-z_!\'()*-.~])',
                      lambda m: '%%%.2X' % ord(m.group()), input)

    def _decode(self, input, errors='strict'):
        assert isinstance(input, str)
        assert errors == 'strict'
        result = re.sub(
            '%([0-9A-Fa-f]{2})', lambda m: chr(int(m.group(1), 16)), input)
        return result.decode('utf-8')


class XMLEntityCodec(Codec):
    """
    >>> '<tag attr="val"/>'.encode('xml')
    '&lt;tag attr="val"/&gt;'
    >>> '&lt;tag attr="val"/&gt;'.decode('xml')
    '<tag attr="val"/>'
    """

    name = 'xml'

    def _encode(self, input, errors='strict'):
        assert errors == 'strict'
        return saxutils.escape(input)

    def _decode(self, input, errors='strict'):
        assert errors == 'strict'
        return saxutils.unescape(input)


percentescape = PercentEscapeCodec()
percentescape.register()
xmlentity = XMLEntityCodec()
xmlentity.register()


if __name__ == '__main__':
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == 'test':
        import doctest
        import tempfile
        import shutil
        tmpdir = tempfile.mkdtemp()
        try:
            doctest.testmod()
        finally:
            shutil.rmtree(tmpdir)
        raise SystemExit

    __name__ = os.path.splitext(os.path.basename(__file__))[0]
    sys.modules[__name__] = sys.modules['__main__']
    from distutils.core import setup
    setup(
        name=__name__,
        version=__version__,
        description=__doc__.splitlines()[0],
        long_description=__doc__,
        author=__author__,
        author_email=__author_email__,
        url='http://pypi.python.org/pypi/' + __name__,
        classifiers=[
            'Development Status :: 4 - Beta',
            #'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Python Software Foundation License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2.7',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Text Processing :: Markup :: HTML',
            'Topic :: Text Processing :: Markup :: XML',
            ],
        license=__license__,
        py_modules=[__name__, ],
        )


