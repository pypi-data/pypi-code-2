"""
Copyright (c) 2009 Ableton AG

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""


class OverlapError(Exception):
    pass


class Replacer(object):


    def __init__(self, content):
        self.content = content
        self.replacements = []

    def __setitem__(self, position, replacement):
        assert position.step is None
        lc = len(self.content)
        start, stop = position.start, position.stop
        # adapt position to size of our actual
        # content
        if start is None:
            start = 0
        if stop is None:
            stop = lc
        if start < 0:
            start += lc
        if stop < 0:
            stop += lc

        if not stop <= lc:
            raise IndexError, "Assignemnt only within content size"

        position = slice(start, stop)
        self.replacements.append((position, replacement))


    def get_value(self):
        return "".join(iter(self))


    def __iter__(self):
        content = self.content
        replacements = sorted(self.replacements)
        if not replacements:
            yield content
            raise StopIteration
        # check for overlaps
        until = -1
        for position, _ in replacements:
            if position.start < until:
                raise OverlapError()
            until = position.stop
        offset = 0
        sit = iter(replacements)
        position, chunk = sit.next()


        if position.start > 0:
            yield content[:position.start]
        while True:
            if callable(chunk):
                chunk = chunk()
            yield chunk
            stop = position.stop
            try:
                position, chunk = sit.next()
            except StopIteration:
                break
            if position.start > stop:
                yield content[stop:position.start]
        if stop < len(content):
            yield content[stop:]



