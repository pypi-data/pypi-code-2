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

def jsonify_query(obj):
    """
    >>> q = Query(and_([eq('name', 'Alberto'), or_([gt('age', 20), lt('age', 30)])]), [desc('join_date')], 10, 10)
    >>> jsonify_query(q)
    {'sort': [{'c': 'join_date', 'dir': 'desc'}], 'count': None, 'join': [], 'q': {'a': None, 'c': [{'a': 'Alberto', 'c': 'name', 'o': 'eq'}, {'a': None, 'c': [{'a': 20, 'c': 'age', 'o': 'gt'}, {'a': 30, 'c': 'age', 'o': 'lt'}], 'o': 'or'}], 'o': 'and'}, 'limit': 10, 'offset': 10}
    """
    d = obj.as_dict()
    d['count'] = obj.count
    return d

def summarize_stream(stream, max_chars):
    r'''
        >>> from genshi import XML
        >>> stream = XML("""<div>Lorem ipsum dolor sit amet, consectetur adipisicing elit, <a href='foo'>sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit</a> esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</div>""")
        >>> list(summarize_stream(stream, 80))
    
    '''

    
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


