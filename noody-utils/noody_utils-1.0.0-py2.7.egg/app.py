#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys
import optparse
from noody.session import Session, GW_PORT, GW_ADDRESS, GW_ID

VERSION = '1.0.0'

def open():
    p = optparse.OptionParser(
        description=u'Open a Noody session.',
        prog='open-noody-session',
        version=VERSION,
        usage='%prog -U username -P password [other options]')
    p.add_option('--username', '-U', action='store', default=None,
                 help=u'Noody username.')
    p.add_option('--password', '-P', action='store', default=None,
                 help=u'Noody password.')
    p.add_option('--gw-address', '-a', action='store',
                 default=GW_ADDRESS, dest='gw_address',
                 help=u'Noody gateway ip address.')
    p.add_option('--gw-port', '-p', action='store',
                 default=GW_PORT, dest='gw_port',
                 help=u'Noody gateway port.')
    p.add_option('--gw-id', '-i', action='store',
                 default=GW_ID, dest='gw_id',
                 help=u'Noody gateway id.')
    p.add_option("--debug", "-d", action="store_true",
             default=False,
             help="Debug mode ON.")


    options, arguments = p.parse_args()
    if not options.username or not options.password:
        print "\n'Username' and 'password' options required.\n"
        p.print_usage()
        sys.exit(1)

    session = Session(username=options.username, password=options.password,
                      gw_address=options.gw_address, gw_port=options.gw_port,
                      gw_id=options.gw_id)
    if options.debug:
        session.debug_on()

    session.open()

def close():
    pass



  