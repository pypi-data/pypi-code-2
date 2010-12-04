__all__ = ('VersionInfo')

import datetime
import sys
import re

class VersionInfo(object):
    __slots__ = ('data',)
    
    @classmethod
    def parse(cls, contents):
        pos = 0 
        current = []
        stack = [current]
        
        labels = re.compile(r"^\w+(?!\w)")
        strings = re.compile(r"^'((?:[^']+|'')*)'")
        
        while pos < len(contents):
            c = contents[pos]
            
            if c == ' ':
                pos += 1
                continue
            
            if contents[pos] == '(':
                pos += 1
                stack.append(current)
                current = []
                continue
            
            if contents[pos] == ')':
                pos += 1
                stack[-1].append(current)
                current = stack[-1]
                del stack[-1]
                continue
            
            if contents[pos].isalpha():
                m = labels.search(contents[pos:])
                current.append(m.group(0))
                pos += m.end(0)
                continue
            
            if contents[pos] == "'":
                m = strings.match(contents[pos:])
                current.append(m.group(1))
                pos += m.end(0)
                continue
            
        return VersionInfo(current[0])
    
    def __init__(self, data):
        self.data = dict(zip(data[0::2], data[1::2]))
    
    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.name)
    
    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        return getattr(super(VersionInfo, self), key)
    
    # lazy creation of ancestor instances
    def ancestors(self):
        return [VersionInfo(p) for p in self.data['ancestors']]
    
    # convenience
    def timestamp(self):
        try:
            return datetime.datetime.strptime(self.date + " " + self.time, "%d %B %Y %I:%M:%S %p")
        except ValueError:
            # some versions have millisecond data
            return datetime.datetime.strptime(self.date + " " + self.time, "%d %B %Y %I:%M:%S.%f %p")
