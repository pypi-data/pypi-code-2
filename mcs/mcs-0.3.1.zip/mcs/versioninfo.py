__all__ = ('VersionInfo')

import datetime
import sys

sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))

class VersionInfo(object):
    __slots__ = ('data',)
    
    @classmethod
    @apply #beware!
    def parse():
        from pyparsing import Forward, Group, QuotedString, Suppress, Word, \
                              ZeroOrMore, alphanums, nums, printables
        
        # simple entities
        LPAR, RPAR = Suppress("("), Suppress(")")
        token = Word(alphanums)
        string_ = token | QuotedString(quoteChar="'", escQuote="''", multiline=True)
        
        # complex parser entities
        dictlist = Forward()
        keyvalue = Group(token + (string_ | dictlist))
        dictionary = Group(LPAR + ZeroOrMore(keyvalue) + RPAR).setParseAction(lambda s, l, t: dict(tuple(t[0])))
        dictlist << Group(LPAR + ZeroOrMore(dictionary) + RPAR)
        
        # return real parse method
        return lambda cls, contents: cls(dictionary.parseString(contents, parseAll=True)[0])
    
    def __init__(self, data):
        self.data = dict(tuple(data.items()))
        if 'ancestors' in self.data:
            self.data['ancestors'] = [VersionInfo(p) for p in self.data['ancestors']]
    
    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.name)
    
    def __getattr__(self, key):
        if key in self.data:
            return self.data[key]
        return getattr(super(VersionInfo, self), key)

    # convenience
    def timestamp(self):
        try:
            return datetime.datetime.strptime(self.date + " " + self.time, "%d %B %Y %I:%M:%S.%f %p")
        except ValueError:
            return datetime.datetime.strptime(self.date + " " + self.time, "%d %B %Y %I:%M:%S %p")
