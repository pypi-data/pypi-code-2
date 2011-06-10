# Insert docstring from README.rst
# [[[cog
# import cog
# cog.outl('"""'); cog.outl(file('README.rst').read()); cog.outl('"""')
# ]]]
"""
============================================
 Spreadsheet directive for reStructuredText
============================================

rstSpreadsheet provides the `spreadsheet` directive for
reStructuredText. You can use it from Docutils or Sphinx.
Any python function/module can be used to calculate the cell value.
Please see the
`documentation <http://tkf.bitbucket.org/rstspreadsheet-doc/>`_
and
`examples <http://tkf.bitbucket.org/rstspreadsheet-doc/sample.html>`_


Install
-------
::

    pip install rstspreadsheet  # or
    easy_install rstspreadsheet


Usage
-----

Use as a standalone program::

    python -m rstspreadsheet sample.rst sample.html

Or use as a sphinx extension by adding it to `extensions`::

    extensions = [
        # other extensions...
        'rstspreadsheet']


Examples
--------

Simple spreadsheet
^^^^^^^^^^^^^^^^^^

You can do this simple calculation:

=== === ========= ===============
 p   q   p and q   not (p and q)
=== === ========= ===============
 0   0   0         1
 1   0   0         1
 0   1   0         1
 1   1   1         0
=== === ========= ===============

with this simple code::

    .. spreadsheet::
       :eq: {2} = {0} and {1}
            {3} = int(not {2})

       === === ========= ===============
        p   q   p and q   not (p and q)
       === === ========= ===============
        0   0
        1   0
        0   1
        1   1
       === === ========= ===============


Spreadsheet with python functions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to calculate some complicated math functions like this:

.. table::

   ======== ======== ========== ======
   function argument expression result
   ======== ======== ========== ======
   fac      5        fac(5)     120.00
   sin      pi       sin(pi)    0.00
   cos      pi       cos(pi)    -1.00
   exp      1        exp(1)     2.72
   ======== ======== ========== ======

use python module/function!::

    .. spreadsheet::
       :eq: {2} = '{0}({1})'
            {3} = {2}
       :setup: from math import sin, cos, exp, pi
               def fac(n):
                   return fac(n-1) * n if n > 1 else 1
       :format: 3:'%0.2f'

       ======== ======== ========== ======
       function argument expression result
       ======== ======== ========== ======
       fac      5
       sin      pi
       cos      pi
       exp      1
       ======== ======== ========== ======


`You can see more examples here.
<http://tkf.bitbucket.org/rstspreadsheet-doc/sample.html>`_

"""
# [[[end]]]

__author__  = "Takafumi Arakaki"
__version__ = "0.1.2"
__license__ = "MIT License"

import re
from docutils import nodes
from docutils.parsers.rst.directives.tables import RSTTable


class ListLike(object):
    """
    An iterative class with convenient cast functions

    >>> col = ListLike(['1', '2', '3'])
    >>> col
    ListLike(['1', '2', '3'])
    >>> ', '.join(col)
    '1, 2, 3'
    >>> col.str
    ['1', '2', '3']
    >>> col.int
    [1, 2, 3]
    >>> col.float
    [1.0, 2.0, 3.0]

    """

    def __init__(self, data=None):
        if data is None:
            self._data = []
        else:
            self._data = list(data)

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self._data)

    def __getitem__(self, key):
        """
        >>> col = ListLike(['1', '2', '3'])
        >>> col[0]
        '1'
        """
        return self._data[key]

    def __iter__(self):
        """
        >>> col = ListLike(['1', '2', '3'])
        >>> list(col)
        ['1', '2', '3']
        """
        return iter(self._data)

    def __contains__(self, item):
        """
        >>> col = ListLike(['1', '2', '3'])
        >>> '1' in col
        True
        """
        return item in self._data

    def __reversed__(self):
        """
        >>> reversed(ListLike(['1', '2', '3']))
        ListLike(['3', '2', '1'])
        """
        return ListLike(reversed(self._data))

    def __len__(self):
        """
        >>> col = ListLike(['1', '2', '3'])
        >>> len(col)
        3
        """
        return len(self._data)

    def append(self, val):
        """
        >>> col = ListLike(['1', '2', '3'])
        >>> col.append('4')
        >>> col
        ListLike(['1', '2', '3', '4'])
        """
        self._data.append(val)

    @property
    def str(self):
        """Access the stored data as a list of strings (original data)"""
        return self._data

    @property
    def int(self):
        """Access the stored data as a list of ints"""
        return map(int, self._data)

    @property
    def float(self):
        """Access the stored data as a list of floats"""
        return map(float, self._data)

    def sum(self, type='float'):
        """
        Get the sum of the stored data

        >>> col = ListLike(['1', '2', '3'])
        >>> col.sum('int')
        6

        """
        return sum(getattr(self, type))

    def mean(self):
        """
        Get the mean of the stored data

        >>> col = ListLike(['1', '2', '3'])
        >>> col.mean()
        2.0

        """
        return self.sum('float') / len(self)


_RE_EQ_LHS = re.compile(
    r"\{(?P<col>[^\:\}]*)(\:(?P<cond>[^\:\}]*))?\} *= *(?P<eq>.*) *")


def parse_equations(argument):
    r"""
    Parse `eq` option

    >>> parse_equations('''\
    ... {1:i==0} = 0
    ... {1:i==last} = sum(col.int)
    ... {1:i<0<last} = {p} + 1
    ... {2} = {1} * 2''')  #doctest: +NORMALIZE_WHITESPACE
    [(1, 'i==0', '0'),
     (1, 'i==last', 'sum(col.int)'),
     (1, 'i<0<last', '{p} + 1'),
     (2, None, '{1} * 2')]

    """
    deflist = []
    for eqstr in argument.splitlines():
        match = _RE_EQ_LHS.match(eqstr)
        if match:
            (dest, _, cond, defun) = match.groups()
        else:
            raise ValueError("cannot parse '{0}'".format(eqstr))
        deflist.append((int(dest), cond, defun))
    return deflist


def safecall(func):
    """
    Decorator to call a function w/o a system error

    This decorator adds two "hidden" arguments to the original function.

    _debug : bool
        If this argument is True, the error occurred int the function
        call will not be suppressed.  (Default: False)
    _mix : bool
        If this argument is True, the traceback will be returned
        instead of the original returned value when the error occurred.
        If this argument is False, the original result and traceback
        will be returned in 2-tuple always.  (Default: False)


    >>> @safecall
    ... def somethingwrong(wrong):
    ...     if wrong == 'wrong':
    ...         raise Exception(wrong)
    ...     return wrong
    ...
    >>> somethingwrong('nothing wrong')
    'nothing wrong'
    >>> somethingwrong('nothing wrong', _mix=False)
    ('nothing wrong', None)
    >>> tb = somethingwrong('wrong')  # error will be suppressed
    >>> tb.splitlines()[-1]
    'Exception: wrong'
    >>> somethingwrong('wrong', _debug=True)  # error will be raised
    Traceback (most recent call last):
        ...
    Exception: wrong

    """
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwds):
        mix = kwds.pop('_mix', True)
        if kwds.pop('_debug', False):
            result = func(*args, **kwds)
            tb = None
        else:
            try:
                result = func(*args, **kwds)
                tb = None
            except:
                import traceback
                result = None
                tb = traceback.format_exc()
        if mix:
            return result if tb is None else tb
        else:
            return (result, tb)

    return wrapper


class ScopeSetup(object):

    def __init__(self, code=None):
        if code is not None:
            (self.scope, self.tb) = self._get_scope(code, _mix=False)
            if self.tb is None:
                self.fail = False
            else:
                self.fail = True
        else:
            self.scope = {}
            self.tb = None
            self.fail = False

    def with_default(self, *args, **kwds):
        default = dict(*args, **kwds)
        default.update(self.scope)
        return default

    @staticmethod
    @safecall
    def _get_scope(code):
        scope = {}
        exec code in scope
        return scope


empty_setup = ScopeSetup()
safe_eval = safecall(eval)


def parse_format(argument):
    (result, tb) = safe_eval('{%s}' % ' '.join(argument.split('\n')),
                             _mix=False)
    if tb is not None:
        raise ValueError("fail to parse '{0}'".format(argument))
    return result


def new_paragraph(rawtext):
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(rawtext)
    return paragraph


def error_with_tb(tb, error, msg):
    tb_node = nodes.literal_block(tb, tb)
    return [error(msg, tb_node)]


class SpreadSheet(RSTTable):

    option_spec = {'eq': parse_equations,
                   'setup': ScopeSetup,
                   'format': parse_format,}

    def run(self):
        table_node_list = RSTTable.run(self)
        table_node = table_node_list[0]
        message = table_node_list[1:]

        if 'eq' not in self.options:
            return [table_node] + message

        deflist = self.options['eq']
        setup = self.options.get('setup', empty_setup)
        if setup.fail:
            return [table_node] + message + error_with_tb(
                setup.tb,
                self.state.reporter.error,
                'An error occurs while executing `:setup:`')
        formatdict = self.options.get('format', {})
        for tbody in table_node.traverse(nodes.tbody):
            last = len(tbody.traverse(nodes.row)) - 1
            cols = {}
            for (irow, row) in enumerate(tbody.traverse(nodes.row)):
                # fetch data
                coldata = [
                    None if len(entry) == 0 else str(entry[0][0])
                    for entry in row.traverse(nodes.entry)]
                if irow == 0:
                    for i in range(len(coldata)):
                        cols[i] = ListLike()
                # calculate
                for (i, cond, eq) in deflist:
                    _scope = setup.with_default(
                        i=irow, col=cols[i], cols=cols, last=last)
                    if cond is not None:
                        (cond_result, cond_tb,
                         ) = safe_eval(cond, _scope, _mix=False)
                        if cond_tb is not None:
                            message += error_with_tb(
                                cond_tb,
                                self.state.reporter.error,
                                "Following error occurs while "
                                "validating the condition of the cell "
                                "in {0}-th row, {1}-th col: '{2}'"
                                .format(irow, i, cond))
                    else:
                        cond_result = True
                    if cond_result:
                        (result, tb,
                         ) = safe_eval(eq.format(*coldata), _scope,
                                       _mix=False)
                        if tb is None:
                            if i in formatdict:
                                coldata[i] = formatdict[i] % result
                            else:
                                coldata[i] = str(result)
                        else:
                            message += error_with_tb(
                                tb,
                                self.state.reporter.error,
                                "Following error occurs while "
                                "validating the equation of the cell "
                                "in {0}-th row, {1}-th col: '{2}'"
                                .format(irow, i, eq))
                # store cols
                for (i, c) in enumerate(coldata):
                    cols[i].append(c)
                # fill-in
                for (entry, col) in zip(row.traverse(nodes.entry),
                                        coldata):
                    if len(entry) == 0 and col is not None:
                        entry += new_paragraph(col)
        return [table_node] + message


def register_directive():
    from docutils.parsers.rst import directives
    directives.register_directive("spreadsheet", SpreadSheet)


def setup(app):
    app.add_directive("spreadsheet", SpreadSheet)


_WRITER_LIST = [
    'html', 'latex', 'pprint', 'pformat', 'pdf', 'xml', 's5',
    'pseudoxml']

_USAGE = '%prog [<writer>] [options] [<source> [<destination>]]'


def main():
    try:
        import locale
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

    import sys
    from docutils.core import publish_cmdline, default_description

    description = (
        'Generates document with <writer>.  Choose a '
        'writer from [{0}].  The default writer is "html". '
        ).format('|'.join(_WRITER_LIST)) + default_description + (
        '  This generation tool includes "spreadsheet" directive.')

    if len(sys.argv) < 2 or sys.argv[1] not in _WRITER_LIST:
        writer_name = 'html'
        argv = sys.argv[1:]
    else:
        writer_name = sys.argv[1]
        argv = sys.argv[2:]

    register_directive()
    publish_cmdline(writer_name=writer_name, description=description,
                    usage=_USAGE, argv=argv)


if __name__ == '__main__':
    main()
