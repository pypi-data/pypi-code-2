#!/usr/bin/env python
"""
PYIDSERVER.PY
Copyright (C) 2008-2011 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Python implementation of IDServer, a command-line tool
to query an internet server and return information
about it.
"""

import sys
import socket

from plib.utils.chatgen import chat_replies as _chat_replies


def do_output(fileobj, s, linesep=True):
    if linesep:
        fileobj.write("%s\n" % s)
    else:
        fileobj.write(s)
    fileobj.flush()


class chat_replies(_chat_replies):
    # Adds initial output when connection is made
    
    def __init__(self, addr, items, fileobj, callback=None):
        _chat_replies.__init__(self, addr, items, callback)
        self.fileobj = fileobj
    
    def on_connect(self):
        do_output(self.fileobj, "Connected ...")
        do_output(self.fileobj, "Server returned the following:")


PROTO_DEFAULT = 'http'

quitmsgs = [None, "QUIT\r\n"]

protocols = {
    'ftp': (21, [None]),
    'http': (80, ["HEAD / HTTP/1.0\r\n\r\n"]),
    'imap': (143, [None, "A1 CAPABILITY\r\n", "A2 LOGOUT\r\n"]),
    'news': (119, quitmsgs),
    'pop': (110, quitmsgs),
    'smtp': (25, quitmsgs) }


def run_idserver(fileobj, arg, dns_only, protocol, portnum):
    if '://' in arg:
        addrtype, arg = arg.split('://')
        if (addrtype in protocols):
            if protocol:
                do_output(fileobj,
                    "URL includes protocol %s, ignoring specified protocol %s."
                    % (addrtype, protocol))
            protocol = addrtype
        elif addrtype:
            do_output(fileobj,
                "URL includes incorrect protocol %s, ignoring."
                % addrtype)
    if '/' in arg:
        arg, path = arg.split('/')
        if path:
            do_output(fileobj, "URL includes path, ignoring.")
    if ':' in arg:
        arg, portstr = arg.split(':')
        try:
            p = int(portstr)
            if p != portnum:
                if portnum != 0:
                    do_output(fileobj,
                        "URL includes port %d, ignoring specified port %d."
                        % (p, portnum))
                portnum = p
        except ValueError:
            do_output(fileobj,
                "URL includes invalid port %s, ignoring." %
                portstr)
    
    if dns_only:
        do_output(fileobj, "Doing DNS lookup on %s ..." % arg)
    else:
        proto_msg = port_msg = ""
        if protocol == "":
            protocol = PROTO_DEFAULT
        else:
            protocol = protocol.lower()
            proto_msg = " using %s" % protocol
        if protocol in protocols:
            proto_port, proto_items = protocols[protocol]
            if portnum == 0:
                portnum = proto_port
            else:
                port_msg = " on port %i" % portnum
        else:
            raise ValueError, "Invalid protocol: %s." % protocol
    
    ipaddr = socket.gethostbyname(arg)
    if ipaddr == arg:
        # URL was an IP address, reverse lookup
        url = socket.gethostbyaddr(ipaddr)[0]
        do_output(fileobj, "Domain name for %s is %s." % (ipaddr, url))
    else:
        # URL was a domain name, normal lookup
        url = arg
        do_output(fileobj, "IP address for %s is %s." % (url, ipaddr))
    
    if not dns_only:
        do_output(fileobj,
            "Contacting %s%s%s ..." %
                (arg, proto_msg, port_msg))
        for reply in chat_replies((url, portnum), proto_items, fileobj):
            do_output(fileobj, reply, False)
        do_output(fileobj, "Connection closed.")


def run_main(outfile, arg, errfile=None,
        dns_only=False, protocol="", portnum=0):
    """Query server and write results to a file-like object.
    
    This is the intended external API for pyidserver; it wraps the
    ``run_idserver`` function, which does the work, with reasonable
    error handling and diagnostic output.
    
    The purpose of pyidserver is to query an internet server for
    basic information, and output it to the user. It does not actually
    "speak" any of the specific protocols for which it will query a
    server; it relies on the fact that most servers return some sort
    of informational "greeting" when a client connects to them, and
    the information it outputs is taken from such greetings.
    
    In the case of HTTP servers, a request must first be sent for the
    server to return any information (a HEAD request is used for this
    purpose). In the case of IMAP servers, an additional request after
    the first greeting (A1 CAPABILITY) is used to elicit additional
    information.
    
    In all cases where the session with the server is supposed to be
    explicitly terminated (all protocols supported except FTP),
    pyidserver does the termination when it is finished.
    
    Arguments:
    
    - ``outfile``: the file-like object for output (actually it
      can be anything that has ``write`` and ``flush`` methods).
      Defaults to standard output.
    
    - ``arg``: a URL string (either an IP address or a host name).
      May include a protocol specifier at the start (e.g., http://),
      and may include a port specifier at the end (e.g., :80). A
      trailing slash, '/', in the URL, and anything after it, are
      treated as a path specifier and ignored.
    
    - ``errfile``: a file-like object for error output (actually it
      can be anything with a ``write`` method). Defaults to the same
      object as ``outfile``.
    
    - ``dns_only``: If true, only a DNS lookup is done; no connection
      is actually made to the server.
    
    - ``protocol: one of the strings listed as keys in the
      ``protocols`` dictionary above (the default, if nothing is
      passed, is 'http').
    
    - ``portnum``: an integer giving the port number on the server.
      (This parameter should only need to be used very rarely;
      almost always the port number is determined by the protocol
      as shown in the dictionary above.)
    """
    
    if errfile is None:
        errfile = outfile
    try:
        run_idserver(outfile, arg, dns_only, protocol, portnum)
    except ValueError:
        errfile.write("%s\n" % str(sys.exc_info()[1]))
    except (socket.error, socket.herror, socket.gaierror, socket.timeout):
        exc_type, exc_value, _ = sys.exc_info()
        errfile.write("%s %s\n" % tuple(map(str, (exc_type, exc_value))))


if __name__ == '__main__':
    from plib.stdlib.options import parse_options
    
    _, def_dns, def_proto, def_port = run_main.func_defaults
    optlist = (
        ("-l", "--lookup", { 'action': "store_true",
            'dest': "dns_only", 'default': def_dns,
            'help': "Only do DNS lookup, no server query" } ),
        ("-p", "--protocol", { 'action': "store", 'type': "string",
            'dest': "protocol", 'default': def_proto,
            'help': "Use the specified protocol to contact the server" } ),
        ("-r", "--port", { 'action': "store", 'type': "int",
            'dest': "portnum", 'default': def_port,
            'help': "Use the specified port number to contact the server" } )
        )
    arglist = ["URL"]
    
    opts, args = parse_options(optlist, arglist)
    run_main(sys.stdout, args[0], sys.stderr,
        opts.dns_only, opts.protocol, opts.portnum)
