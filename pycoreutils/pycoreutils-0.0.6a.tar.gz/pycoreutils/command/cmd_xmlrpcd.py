# -*- coding: utf-8 -*-

# Copyright (c) 2009, 2010, 2011 Hans van Leeuwen.
# See LICENSE.txt for details.

from __future__ import print_function, unicode_literals
import pycoreutils
import sys

if sys.version_info[0] == 2:
    from SimpleXMLRPCServer import SimpleXMLRPCServer
else:
    from xmlrpc.server import SimpleXMLRPCServer


@pycoreutils.addcommand
def xmlrpcd(argstr):
    p = pycoreutils.parseoptions()
    p.description = "Start a PyCoreutils XML-RPC server"
    p.usage = "%prog [OPTION]..."
    p.add_option("-a", "--address", default="", dest="address",
            help="address to bind to")
    p.add_option("-p", "--port", default=8000, dest="port", type="int",
            help="port to listen to")
    (opts, args) = p.parse_args(argstr.split())

    if opts.help:
        return p.format_help()

    def _runcommandline(commandline):
        '''
        Process a commandline.
        Argument is a string representing the commandline, i.e. "ls -l /tmp"
        '''
        output = pycoreutils.runcommandline(commandline)
        s = ''
        if output:
            for out in output:
                s += out
        return s

    server = SimpleXMLRPCServer((opts.address, opts.port))
    server.register_introspection_functions()
    server.register_function(_runcommandline, 'runcommandline')
    try:
        server.serve_forever()
    finally:
        server.server_close()
