import re

from genshi.core import TEXT, START, END, Stream
from genshi.builder import tag
from genshi.input import HTML

from tw.api import lazystring as _

__all__ = ["cut_text", "summarize_stream"]

expand_start, __, expand_end = \
    list(tag.span('dummy', class_='rum-expandable-span-hidden'))
unexpanded_start,__,unexpanded_end=\
    list(tag.span('dummy', class_='rum-expandable-span-visible'))
#TODO: test these functions

def cut_text(text, max_chars):
    if max_chars < 1:
        return '', text
    pattern = r".{" + str(max_chars)+ r"}.*?\b"
    match = re.match(pattern, text, flags=re.S)
    if match and match.end() < len(text):
        end = match.end()
        return text[:end], text[end:]
    return text, ''

def summarize_stream(stream, max_chars):
    expand = False
    count = 0
    stack = []
    backup=[]
    yield unexpanded_start
    for kind, data, __ in stream:
        if not expand:
            backup.append((kind,data))
        if kind is START:
            stack.append(data)
            yield kind, data, (None, -1, -1)
        elif kind is END:
            stack.pop(-1)
            yield kind, data, (None, -1, -1)
        elif not expand and kind is TEXT:
            data, expand = cut_text(data, max_chars-count)
            count += len(data)
            yield kind, data, (None, -1, -1)
            if expand:
                for data in stack[::-1]:
                    yield END, data[0], (None, -1, -1)

                yield unexpanded_end
                for i in tag.a('...', href='#', class_='span_expander rum-expandable-span-visible',
                               title=_('expand')):
                    yield i
                yield expand_start

                for kind, data in backup:
                    yield kind, data, (None, -1, -1)
                #yield TEXT, expand, (None, -1, -1)
        else:
            yield kind, data, (None, -1, -1)
    if expand:
        yield expand_end
        for i in tag.a(_('(collapse)'), href='#', class_='span_expander rum-expandable-span-hidden'):
            yield i
    else:
        yield unexpanded_end
