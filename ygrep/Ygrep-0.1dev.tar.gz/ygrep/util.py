import re

class MatchStatus:
    matched = 3
    descendant = 2
    ancestor = 1
    unrelated = 0

def printable_len(text):
    return len(re.sub('\x1B\[[0-9]+m', '', text))
        
