#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2002-2010 Chris Liechti <cliechti@gmx.net>
# All Rights Reserved.
# Simplified BSD License (see LICENSE.txt for full text)

"""
JTAG programmer for the MSP430 embedded processor. This implementation
direcltly talks to HID based interfaces such as the LaunchPad.
"""

import sys
import os
import logging
import time
from msp430.jtag import jtag
from msp430 import hid

from optparse import OptionGroup
import msp430.target

VERSION = "1.0"

#define C_INITIALIZE            0x01
#define C_CLOSE                 0x02
#define C_IDENTIFY              0x03
#define C_DEVICE                0x04
#define C_CONFIGURE             0x05
#define C_VCC                   0x06
#define C_RESET                 0x07
#define C_READREGISTERS         0x08
#define C_WRITEREGISTERS        0x09
#define C_READREGISTER          0x0a
#define C_WRITEREGISTER         0x0b
#define C_ERASE                 0x0c
#define C_READMEMORY            0x0d
#define C_WRITEMEMORY           0x0e
#define C_FASTFLASHER           0x0f
#define C_BREAKPOINT            0x10
#define C_RUN                   0x11
#define C_STATE                 0x12
#define C_SECURE                0x13
#define C_VERIFYMEMORY          0x14
#define C_FASTVERIFYMEMORY      0x15
#define C_ERASECHECK            0x16
#define C_EEMOPEN               0x17
#define C_EEMREADREGISTER       0x18
#define C_EEMREADREGISTERTEST   0x19
#define C_EEMWRITEREGISTER      0x1a
#define C_EEMCLOSE              0x1b
#define C_ERRORNUMBER           0x1c
#define C_GETCURVCCT            0x1d
#define C_GETEXTVOLTAGE         0x1e
#define C_FETSELFTEST           0x1f
#define C_FETSETSIGNALS         0x20
#define C_FETRESET              0x21
#define C_READI2C               0x22
#define C_WRITEI2C              0x23
#define C_ENTERBOOTLOADER       0x24


class JTAGTarget(hid.HIDConnection):

    def __init__(self):
        pass


    def command(self, cmd, data=None, *args):
        packet = bytearray()
        packet.append(bytes(struct.pack('<BB',
                cmd,
                1 + bool(args) + 2*bool(data))))
        if args:
            packet.append(bytes(struct.pack('<H', len(args))))
            for x in args:
                packet.append(bytes(struct.pack('<I', x)))
        if data:
            packet.append(bytes(struct.pack('<I', len(data))))
            packet.append(bytes(data))
        packet.append(bytes(struct.pack('<H', checksum(packet))))
        packet.append(0x7e)

    def configure(self, interface):
        if interface == 'spy-bi-wire':
        elif interface == 'spy-bi-wire-jtag':

        self.command(C_CONFIGURE)

    def memory_read(self, address, length):
        """Read from memory."""
        return bytearray(self.jtagobj.uploadData(address, length))

    def memory_write(self, address, data):
        """Write to memory."""
        return self.jtagobj.downloadData(address, data)

    def mass_erase(self):
        """Clear all Flash memory."""
        self.jtagobj.actionMassErase()

    def main_erase(self):
        """Clear main Flash memory (excl. infomem)."""
        self.jtagobj.actionMainErase()

    def erase(self, address):
        """Erase Flash segment containing the given address."""
        self.jtagobj.makeActionSegmentErase(address)()

    def execute(self, address):
        """Start executing code on the target."""
        self.jtagobj.actionRun(address) # load PC and execute

    def version(self):
        """The 16 bytes of the ROM that contain chip and BSL info are returned."""
        return self.jtagobj.uploadData(0x0ff0, 16)

    def reset(self):
        """Reset the device."""
        if not self.release_done:
            self.release_done = True
            try:
                self.jtagobj.reset(1, 1)
            except IOError, e: # XXX currently getting EEM errors on launchpad
                pass

    def close(self):
        self.transmit(bytearray([0x02, 0x02, 0x01, 0x00]))



class JTAG(JTAGTarget, msp430.target.Target):
    """Combine the JTAG backend and the common target code."""

    def __init__(self):
        JTAGTarget.__init__(self)
        msp430.target.Target.__init__(self)
        self.logger = logging.getLogger('HID-JTAG')

        # some variables used in help texts
        self.text_variables = {
            'prog': sys.argv[0],
            'version': VERSION,
        }

    def add_extra_options(self):
        group = OptionGroup(self.parser, "Connection")

        group.add_option("--spy-bi-wire-jtag",
                dest="spy_bi_wire_jtag",
                help="interface is 4 wire on a spy-bi-wire capable device",
                default=False,
                action='store_true')

        group.add_option("--spy-bi-wire",
                dest="spy_bi_wire",
                help="interface is 2 wire on a spy-bi-wire capable device",
                default=False,
                action='store_true')

        self.parser.add_option_group(group)

        group = OptionGroup(self.parser, "JTAG fuse", """\
WARNING: This is not reversible, use with care!",
""")

        group.add_option("--secure",
                dest="do_secure",
                help="blow JTAG security fuse",
                default=False,
                action='store_true')

        self.parser.add_option_group(group)

        group = OptionGroup(self.parser, "Examples", """\
Mass erase and program from file: "%(prog)s -e firmware.elf"
Dump information memory: "%(prog)s --upload=0x1000-0x10ff"
""" % self.text_variables)
        self.parser.add_option_group(group)


    def parse_extra_options(self):
        """Process the extra options we added above"""
        if self.options.spy_bi_wire:
            interface = 'spy-bi-wire'
        if self.options.spy_bi_wire_jtag:
            interface = 'spy-bi-wire-jtag'

        self.configure(interface)

        if self.options.do_secure:
            self.add_action(self.jtagobj.actionSecure)

        if self.verbose:
            sys.stderr.write("MSP430 JTAG (HID) programmer Version: %s\n" % VERSION)

        self.jtagobj.data = self.download_data      # prepare downloaded data


    def close_connection(self):
        """Close connection to target"""
        self.close()


    def open_connection(self):
        """Connect to target"""
        self.jtagobj.open(0x0451, 0xf432)       # try to open port
        self.jtagobj.connect()                  # connect to target


def main():
    # run the main application
    jtag_target = JTAG()
    jtag_target.main()

if __name__ == '__main__':
    main()
