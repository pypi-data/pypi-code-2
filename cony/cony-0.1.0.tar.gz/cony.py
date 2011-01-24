#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import route, run, debug, request, redirect

DEBUG = True


def cmd_g(term):
    """Google search."""
    redirect('http://www.google.com/search?q=%s' % term)


def cmd_pypi(term):
    """Python package index search."""
    redirect('http://pypi.python.org/pypi?:action=search&term=%s&submit=search' % term)


try:
    from local_commands import *
except ImportError:
    pass


def cmd_help(term):
    """Shows all available commands."""
    commands = []
    for name, obj in sorted(globals().items()):
        if name.startswith('cmd_') and callable(obj):
            commands.append('%s — %s' % (name[4:], obj.__doc__))
    return '<br/>'.join(commands)


@route('/')
def do_command():
    """Runs a command"""
    search_string = request.GET['s']

    tokens = search_string.split(' ', 1)
    command_name = tokens[0]
    term = len(tokens) == 2 and tokens[1] or ''

    command = globals()['cmd_' + command_name]
    return command(term)

if __name__ == '__main__':
    debug(DEBUG)
    run(reloader = DEBUG)

