# Insert docstring from README.rst
# [[[cog
# import cog
# cog.outl('"""'); cog.outl(file('README.rst').read()); cog.outl('"""')
# ]]]
"""
============================================
 Spreadsheet directive for reStructuredText
============================================

reStructuredSpreadsheet adds the `spreadsheet` directive for
reStructuredText. You can use it from Docutils or Sphinx.
Any python function/module can be used to calculate the cell value.


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

"""
# [[[end]]]

__author__  = "Takafumi Arakaki"
__version__ = "0.1"
__license__ = "MIT License"

from docutils import nodes
from docutils.parsers.rst.directives.tables import RSTTable


def parse_equations(argument):
    """Parse `eq` option"""
    defdict = {}
    for eqstr in argument.split('\n'):
        (dest, defun) = [s.strip() for s in eqstr.split('=', 1)]
        defdict[int(dest.strip('{}'))] = defun
    return defdict


def parse_setup(argument):
    scope = {}
    exec argument in scope
    return scope


def parse_format(argument):
    return eval('{%s}' % ' '.join(argument.split('\n')))


def new_paragraph(rawtext):
    paragraph = nodes.paragraph()
    paragraph += nodes.Text(rawtext)
    return paragraph


class SpreadSheet(RSTTable):

    option_spec = {'eq': parse_equations,
                   'setup': parse_setup,
                   'format': parse_format,}

    def run(self):
        table_node_list = RSTTable.run(self)
        table_node = table_node_list[0]
        message = table_node_list[1:]

        if 'eq' not in self.options:
            return [table_node] + message

        defdict = self.options['eq']
        scope = self.options.get('setup', {})
        formatdict = self.options.get('format', {})
        for tbody in table_node.traverse(nodes.tbody):
            for row in tbody.traverse(nodes.row):
                # fetch data
                coldata = [
                    None if len(entry) == 0 else str(entry[0][0])
                    for entry in row.traverse(nodes.entry)]
                # calculate
                for (i, eq) in defdict.iteritems():
                    result = eval(eq.format(*coldata), scope)
                    if i in formatdict:
                        coldata[i] = formatdict[i] % result
                    else:
                        coldata[i] = str(result)
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
