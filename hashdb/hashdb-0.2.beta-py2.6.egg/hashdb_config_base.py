import hashdb_output as output
import os
import shlex
from collections import namedtuple

def parse_text__mapping(mapping):
    def func(text):
        uppr = text.upper()
        if uppr in mapping:
            return mapping.get(uppr)
        else:
            raise ValueError, 'Invalid value (%s)' % text
    return func

parse_text__verbosity = parse_text__mapping({
    'QUIET'  : output.QUIET,
    'DEFAULT': output.DEFAULT,
    'VERBOSE': output.VERBOSE,
    'DEBUG'  : output.DEBUG
})
parse_text__boolean = parse_text__mapping({
    'TRUE'  : True,
    'YES'   : True,
    'T'     : True,
    'Y'     : True,
    '1'     : True,
    'FALSE' : False,
    'NO'    : False,
    'F'     : False,
    'N'     : False,
    '0'     : False
})


def parse_text__exists(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        return filename
    else:
        raise ValueError, '%r is not a valid file'

def parse_text__verbatim(text):
    return text

def parse_text__filename(text):
    if text == '' or text == '""':
        return ''

    s = shlex.shlex(text, posix=True)
    s.whitespace_split = True
    s.whitespace = ''
    s.commenters = ''
    results = list(s)
    if len(results) != 1:
        raise ValueError, 'Invalid filename %r' % text

    return results[0]


def parse_text__filenames(text):
    return shlex.split(text)

CombineDB = namedtuple("CombineDB", "local database remote")
def parse_text__database_combine(text):
    s = shlex.shlex(text, posix=True)
    s.whitespace_split = False
    s.commenters = ''

    parts = list(s)
    if (len(parts) == 5) and (parts[1] == ':' and parts[3] == ':'):
        local, database, remote = parts[0], parts[2], parts[4]
    elif len(parts) == 1:
        local = remote = None
        database = parts[0]
    else:
        raise ValueError, 'Invalid database combine specification %r' % text

    return CombineDB(local, database, remote)