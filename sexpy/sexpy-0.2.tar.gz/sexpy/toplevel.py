# Copyright 2007 Ero-sennin
#
# This file is part of SEXpy.
#
# SEXpy is free software; you can redistribute it and/or modify
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# SEXpy is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pybtex; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
# USA

import traceback
from sexpy.parser import parse, SexpSyntaxError
from sexpy.translator import sex_compile


class Input(object):
    """File-like read() and readline() interface for console input"""

    def __init__(self):
        from io import StringIO
        self.buffer = StringIO()
        self.incomplete = False

    def read(self, size=-1):
        data = self.buffer.read(size)
        if not data:
            self.get_line()
            data = self.buffer.read(size)
        return data

    next = read

    def readline(self):
        data = self.buffer.readline()
        if not data:
            self.get_line()
            data = self.buffer.readline()
        return data

    def get_line(self):
        self.buffer.truncate(0)
        self.buffer.seek(0)
        if self.incomplete:
            prompt = '...    '
        else:
            prompt = 'SEXpy> '
        try:
            self.buffer.write(input(prompt))
        except ValueError:
            raise EOFError
        if self.buffer.getvalue().strip():
            self.incomplete = True
        self.buffer.write('\n')
        self.buffer.seek(0)

    def __iter__(self):
        return self


def toplevel():
    """Launch a toplevel interactive loop"""

    try:
        import readline
    except ImportError:
        pass
    from sexpy.translator import lineno

    interactive_namespace = {}
    interactive_namespace['__name__'] = '__main__'

    while True:
        i = Input()
        try:
            for statement in parse(i):
                i.incomplete = False
                try:
                    code = sex_compile([statement], mode='single')
                except:
                    print('"<input>", line %s: invalid statement' % lineno(statement))
                    print(' -->', repr(statement))
                    raise
                    continue
                try:
                    exec(code, interactive_namespace)
                except SystemExit:
                    return
                except:
                    traceback.print_exc()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        except SexpSyntaxError as error:
            print(error)
            continue
