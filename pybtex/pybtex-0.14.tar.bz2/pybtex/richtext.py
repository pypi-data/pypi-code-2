# Copyright (C) 2006, 2007, 2008, 2009  Andrey Golovizin
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

r"""(simple but) rich text formatting tools

Usage:

>>> from pybtex.backends import latex
>>> backend = latex.Writer()
>>> t = Text('this ', 'is a ', Tag('emph', 'very'), Text(' rich', ' text'))
>>> print t.render(backend)
this is a \emph{very} rich text
>>> print t.plaintext()
this is a very rich text
>>> t = t.capfirst().add_period()
>>> print t.render(backend)
This is a \emph{very} rich text.
>>> print t.plaintext()
This is a very rich text.
>>> print Symbol('ndash').render(backend)
--
>>> t = Text('Some ', Tag('emph', Text('nested ', Tag('texttt', 'Text', Text(' objects')))), '.')
>>> print t.render(backend)
Some \emph{nested \texttt{Text objects}}.
>>> print t.plaintext()
Some nested Text objects.
>>> t = t.map(lambda string: string.upper())
>>> print t.render(backend)
SOME \emph{NESTED \texttt{TEXT OBJECTS}}.
>>> print t.plaintext()
SOME NESTED TEXT OBJECTS.

>>> t = Text(', ').join(['one', 'two', Tag('emph', 'three')])
>>> print t.render(backend)
one, two, \emph{three}
>>> print t.plaintext()
one, two, three
>>> t = Text(Symbol('nbsp')).join(['one', 'two', Tag('emph', 'three')])
>>> print t.render(backend)
one~two~\emph{three}
>>> print t.plaintext()
one<nbsp>two<nbsp>three
"""

from copy import deepcopy
from pybtex import textutils
import string

class Text(list):
    """
    Rich text is basically a list of:

    - plain strings
    - Tag objects
    - other Text objects

    Text is used as an internal formatting language of Pybtex,
    being rendered to to HTML or LaTeX markup or whatever in the end.
    """

    def __init__(self, *parts):
        """Create a Text consisting of one or more parts."""

        list.__init__(self, parts)

    def __len__(self):
        """Return the number of characters in this Text."""
        return sum(len(part) for part in self)

    def __add__(self, other):
        """
        Concatenate this Text with another Text or string.

        >>> t = Text('a')
        >>> print (t + 'b').plaintext()
        ab
        >>> print (t + t).plaintext()
        aa
        >>> print t.plaintext()
        a
        """

        if isinstance(other, basestring):
            other = [other]
        return self.from_list(super(Text, self).__add__(other))

    def from_list(self, lst):
        return Text(*lst)

    def append(self, item):
        """Appends some text or something.
        Empty strings and similar things are ignored.
        """
        if item:
            list.append(self, item)

    def extend(self, list):
        for item in list:
            self.append(item)

    def render(self, backend):
        """Return backend-dependent textual representation of this Text."""

        text = []
        for item in self:
            if isinstance(item, basestring):
                text.append(backend.format_text(item))
            else:
                text.append(item.render(backend))
        return "".join(text)

    def enumerate(self):
        for n, child in enumerate(self):
            try:
                for p in child.enumerate():
                    yield p
            except AttributeError:
                yield self, n

    def reversed(self):
        for n, child in reversed(list(enumerate(self))):
            try:
                for p in child.reversed():
                    yield p
            except AttributeError:
                yield self, n

    def map(self, f, condition=None):
        if condition is None:
            condition = lambda index, length: True
        def iter_map_with_condition():
            length = len(self)
            for index, child in enumerate(self):
                if hasattr(child, 'map'):
                    yield child.map(f, condition) if condition(index, length) else child
                else:
                    yield f(child) if condition(index, length) else child
        return self.from_list(iter_map_with_condition())

    def upper(self):
        return self.map(string.upper)

    def apply_to_start(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == 0)

    def apply_to_end(self, f):
        """Apply a function to the last part of the text"""
        return self.map(f, lambda index, length: index == length - 1)

    def get_beginning(self):
        try:
            l, i = self.enumerate().next()
        except StopIteration:
            pass
        else:
            return l[i]

    def get_end(self):
        try:
            l, i = self.reversed().next()
        except StopIteration:
            pass
        else:
            return l[i]

    def join(self, parts):
        """Join a list using this text (like string.join)

        >>> print Text(' ').join([]).plaintext()
        <BLANKLINE>
        >>> print Text(' ').join(['a', 'b', 'c']).plaintext()
        a b c
        >>> print Text(nbsp).join(['a', 'b', 'c']).plaintext()
        a<nbsp>b<nbsp>c
        """

        joined = Text()
        if not parts:
            return joined
        for part in parts[:-1]:
            joined.extend([part, deepcopy(self)])
        joined.append(parts[-1])
        return joined

    def plaintext(self):
        return ''.join(unicode(l[i]) for l, i in self.enumerate())

    def capfirst(self):
        """Capitalize the first letter of the text"""
        return self.apply_to_start(textutils.capfirst)

    def add_period(self, period='.'):
        """Add a period to the end of text, if necessary.

        >>> import pybtex.backends.html
        >>> html = pybtex.backends.html.Writer()

        >>> text = Text("That's all, folks")
        >>> print text.add_period().plaintext()
        That's all, folks.

        >>> text = Tag('emph', Text("That's all, folks"))
        >>> print text.add_period().render(html)
        <em>That's all, folks.</em>
        >>> print text.add_period().add_period().render(html)
        <em>That's all, folks.</em>

        >>> text = Text("That's all, ", Tag('emph', 'folks'))
        >>> print text.add_period().render(html)
        That's all, <em>folks</em>.
        >>> print text.add_period().add_period().render(html)
        That's all, <em>folks</em>.

        >>> text = Text("That's all, ", Tag('emph', 'folks.'))
        >>> print text.add_period().render(html)
        That's all, <em>folks.</em>

        >>> text = Text("That's all, ", Tag('emph', 'folks'))
        >>> print text.add_period('!').render(html)
        That's all, <em>folks</em>!
        >>> print text.add_period('!').add_period('.').render(html)
        That's all, <em>folks</em>!
        """

        end = self.get_end()
        if end and not textutils.is_terminated(end):
            return self + period
        else:
            return self

class Tag(Text):
    """A tag is somethins like <foo>some text</foo> in HTML
    or \\foo{some text} in LaTeX. 'foo' is the tag's name, and
    'some text' is tag's text.

    >>> emph = Tag('emph', 'emphasized text')
    >>> from pybtex.backends import latex, html
    >>> print emph.render(latex.Writer())
    \emph{emphasized text}
    >>> print emph.render(html.Writer())
    <em>emphasized text</em>
    """

    def from_list(self, lst):
        return Tag(self.name, *lst)

    def __init__(self, name, *args):
        self.name = name
        Text.__init__(self, *args)

    def render(self, backend):
        text = super(Tag, self).render(backend)
        return backend.format_tag(self.name, text)

class Symbol(object):
    """A special symbol.

    Examples of special symbols are non-breaking spaces and dashes.

    >>> nbsp = Symbol('nbsp')
    >>> from pybtex.backends import latex, html
    >>> print nbsp.render(latex.Writer())
    ~
    >>> print nbsp.render(html.Writer())
    &nbsp;
    """

    def __init__(self, name):
        self.name = name

    def __len__(self):
        return 1

    def __repr__(self):
        return "Symbol('%s')" % self.name

    def __unicode__(self):
        return u'<%s>' % self.name

    def render(self, backend):
        return backend.symbols[self.name]

nbsp = Symbol('nbsp')
