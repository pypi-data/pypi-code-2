#!/usr/bin/env python

"""
free-form arg parser

python parser.py foo -bar --fleem blah -gaz hi --flarg=play
['foo', 'hi']
['bar', 'gaz']
{'fleem': 'blah', 'flarg': 'play'}
"""

def parse(args):
    _args1 = []
    _args2 = []
    kw = {}
    key = None
    for arg in args:
        if arg.startswith('-'):
            if key:
                raise Exception
            if arg.startswith('--'):
                if arg.startswith('---'):
                    raise Exception
                arg = arg.lstrip('-')
                if '=' in arg:
                    key, value = arg.split('=', 1)
                    kw[key] = value
                    key = None
                else:
                    key = arg
            else:
                _args2.append(arg[1:])
        else:
            if key:
                kw[key] = arg
                key = None
            else:
                _args1.append(arg)
    if key:
        raise Exception
    return _args1, _args2, kw

if __name__ == '__main__':
    import sys
    args, positional_args, kwargs = parse(sys.argv[1:])
    print args
    print positional_args
    print kwargs
