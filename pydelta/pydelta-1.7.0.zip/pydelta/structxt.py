"""Utility functions for working with 'structured' text, i.e. strings with
segments (e.g. comments) delimited by particular characters, which should be
treated differently."""
# -*- coding: utf-8 -*-
import re

def _mapchunks(text, opener, closer):
    """Utility function to find chunks in a string, marked by the opener and
    closer. Yields tuples of (level, openindex, closeindex), where level is
    zero-based.
    
    Note that chunks show up the order they close, not the order they open."""
    assert opener != closer, "Opener and closer must be different"
    openpoints = [m.start() for m in re.finditer(re.escape(opener), text)]
    closepoints = [m.start() for m in re.finditer(re.escape(closer), text)]
    
    chunkstarts = []
    while (closepoints or openpoints):
        if openpoints and (openpoints[0] < closepoints[0]):
            chunkstarts.append(openpoints.pop(0))
        else:
            chunkend = closepoints.pop(0)
            if chunkstarts:
                yield (len(chunkstarts)-1, chunkstarts.pop(), chunkend)
            
def _mapflatchunks(text, marker):
    """Utility function to map chunks delimited by the same start and end
    marker, such as " or '. Returns a list of (start, end) tuples."""
    togglepoints = [m.start() for m in re.finditer(re.escape(marker), text)]
    return zip(* [iter(togglepoints)]*2)  # Cluster into groups of 2

def grabchunks(text, opener, closer):
    """
    Get 'chunks' as marked by the specified opener and closer. Only the first
    level of chunks will be returned. These may contain similar chunks, which
    can be extracted by running the function again.
    
    This is a generator: to get an indexable list of the chunks, use
    list(grabchunks(...))
    
    Example usage:
    foo = "green <eggs <and>> multicoloured <spam>."
    for chunk in grabchunks(foo, "<",">"):
        print(chunk)
    # eggs <and>
    # spam
    """
    for inlevel, chunkstart, chunkend in _mapchunks(text, opener, closer):
        if inlevel == 0:
            yield text[chunkstart+len(opener):chunkend]
                
def removechunks(text, opener, closer):
    """Strip out 'chunks', e.g. comments, as marked by the specified opener and
    closer. E.g.
    foo = "green <eggs <and>> multicoloured <spam>."
    print removechunks(foo, "<", ">")
    # green  multicoloured .
    """
    chunks = [(o, c) for level, o, c in _mapchunks(text, opener, closer) \
                        if level == 0]
    if not chunks:
        return text
    outtxt = [text[:chunks[0][0]]]
    prev_chunk_end = chunks.pop(0)[1] + len(closer)
    for start, end in chunks:
        outtxt.append(text[prev_chunk_end:start])
        prev_chunk_end = end + len(closer)
    outtxt.append(text[prev_chunk_end:])
    return "".join(outtxt)
      
def splitwithout(text, spliton, containermarks = [('"','"')]):
    """Splits text in a similar manner to text.split(spliton), but ignoring
    spliton where it occurs between start and end markers. E.g. 
    'a,<b,c>' could be split into ['a', '<b,c>'], rather than ['a', '<b', 'c>'].

    You can specify any number of containers, and the text will only be split 
    where the delimiter occurs outside all of them. Each container should be a
    tuple of the opening symbol and the closing symbol (even if they are the
    same).
    
    Example usage:
    foo = 'Green, "Eggs, Spam", etc.'
    splitwithout(foo, ',')
    # ['Green', ' "Eggs, Spam"', ' etc.']

    bar = "Do | {{Re | {{Mi | Fa }}}} | Sol | <La | Ti> | Do"
    splitwithout(bar,'|', [('{{','}}'), ('<','>')])
    # ['Do ', ' {{Re | {{Mi | Fa }}}} ', ' Sol ', ' <La | Ti> ', ' Do']
    """
    posssplitpoints = [m.start() for m in re.finditer(re.escape(spliton), text)]
    for opener, closer in containermarks:
        if opener == closer:
            chunkmap = _mapflatchunks(text, opener) 
        else:   # Different opener and closer.
            chunkmap = [(o, c) for level, o, c \
                        in _mapchunks(text, opener, closer) if level == 0]
        
        splitpoints = []
        # Check if each split point is within a container
        for point in posssplitpoints:
            if not any(openpt < point < closept for openpt, closept in chunkmap):
                splitpoints.append(point)
        posssplitpoints = splitpoints
    
    sections = []
    prevpoint = 0
    for point in splitpoints:
        sections.append(text[prevpoint:point])
        prevpoint = point + len(spliton)
    return sections + [text[prevpoint:]]         
