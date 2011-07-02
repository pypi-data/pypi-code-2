"""Sleipninr RCA Flows"""

from os import path
from glob import iglob
from operator import itemgetter
from itertools import imap


def __import(match):
    """Import modules"""
    modules = (path.splitext(path.basename(x)) for x in iglob(match))
    modules = set(imap(itemgetter(0), modules))
    [__import__(mod, globals()) for mod in modules if mod[0] != '_']

# now import flows
__import(path.join(path.dirname(__file__), "./*.py*"))
