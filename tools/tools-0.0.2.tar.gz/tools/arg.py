#!/usr/bin/env python
"""
Arg framework:
"""

from argparse import ArgumentParser

COMMANDS = []

def option(*args, **kwargs):
    return lambda: (args, kwargs)


def command(*options):
    def wrapper(func):
        def old_func(*args, **kwargs):
            return func(*args, **kwargs)
        old_func.__name__ = func.__name__
        old_func.__doc__ = func.__doc__
        old_func._options = options
        COMMANDS.append(old_func)
        return old_func
    return wrapper


def dispatch():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()
    commands = []
    for command in COMMANDS:
        sub = subparsers.add_parser(command.__name__, help=command.__doc__)
        for _option in command._options:
            args, kwargs = _option()
            sub.add_argument(*args, **kwargs)
        sub.set_defaults(func=command)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':

    @command(
        option('path', help='path to the dump'))
    def load(args):
        "load dump"

        print 'loading dump from %s' % args.path

    dispatch()
