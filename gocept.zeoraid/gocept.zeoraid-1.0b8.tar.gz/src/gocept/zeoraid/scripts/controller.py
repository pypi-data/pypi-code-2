##############################################################################
#
# Copyright (c) 2007-2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""The management utility for gocept.zeoraid.

Usage: controller.py [options] <command> [command_options]

Options:

    -p port -- port to connect to (default is 8100)

    -h host -- host to connect to (default is 127.0.0.1)

    -S name -- storage name (default is '1')

Commands:

    status -- Print short status information

    details -- Print detailed status information

    recover <storage> -- Start recovery for a storage

    disable <storage> -- Disable a storage

    reload -- Reload this raid storage's configuration from the zeo.conf

"""

import ZEO.ClientStorage
import optparse
import sys
import logging

logging.getLogger().setLevel(100)

NAGIOS_OK = 0
NAGIOS_WARNING = 1
NAGIOS_CRITICAL = 2
NAGIOS_UNKNOWN = 3

STATUS_TO_NAGIOS = dict(
    optimal=NAGIOS_OK,
    failed=NAGIOS_CRITICAL,
    degraded=NAGIOS_CRITICAL,
    recovering=NAGIOS_WARNING)


class RAIDManager(object):

    def __init__(self, host, port, storage):
        self.host = host
        self.port = port
        self.storage = storage

        self.raid = ZEO.ClientStorage.ClientStorage(
            (self.host, self.port), storage=self.storage, read_only=1,
            wait=False)
        if not self.raid.is_connected():
            self.raid.close()
            raise RuntimeError(
                'Could not connect to ZEO server at %s:%s' %
                (self.host, self.port))

    def cmd_status(self):
        status = self.raid.raid_status()
        print status
        return STATUS_TO_NAGIOS[status]

    def cmd_details(self):
        col1 = 25

        storages = self.raid.raid_details()
        print " %s| Status" % ('%s:%s' % (self.host, self.port)).ljust(col1)
        print " %s+-------------------" % ('-' * col1)
        print " %s| %s" % (('RAID %s' % self.storage).ljust(col1),
                           self.raid.raid_status().ljust(col1))
        print " %s+-------------------" % ('-' * col1)

        for storage in sorted(storages):
            print ' %s| %s' % (str(storage).ljust(col1), storages[storage])

        return STATUS_TO_NAGIOS[self.raid.raid_status()]

    def cmd_recover(self, storage):
        print self.raid.raid_recover(storage)
        return NAGIOS_OK

    def cmd_disable(self, storage):
        print self.raid.raid_disable(storage)
        return NAGIOS_OK

    def cmd_reload(self):
        self.raid.raid_reload()
        return NAGIOS_OK


def main(host="127.0.0.1", port=8100, storage="1"):
    usage = "usage: %prog [options] command [command-options]"
    description = (
        "Connect to a RAIDStorage on a ZEO server and perform "
        "maintenance tasks. Available commands: status, details, "
        "recover <STORAGE>, disable <STORAGE>, reload </PATH/TO/ZEO.CONF>. "
        "Returns a Nagios-compatible exit code depending on success, "
        "failure or RAID status.")

    parser = optparse.OptionParser(usage=usage, description=description)
    parser.add_option("-S", "--storage", default=storage,
                      help="Use STORAGE on ZEO server. Default: %default")
    parser.add_option("-H", "--host", default=host,
                      help="Connect to HOST. Default: %default")
    parser.add_option("-p", "--port", type="int", default=port,
                      help="Connect to PORT. Default: %default")
    options, args = parser.parse_args()

    if not args:
        parser.error("no command given")

    command, subargs = args[0], args[1:]

    try:
        m = RAIDManager(options.host, options.port, options.storage)
        command = getattr(m, 'cmd_%s' % command)
        result = command(*subargs)
    except Exception, e:
        print str(e)
        result = NAGIOS_CRITICAL
    sys.exit(result)


if __name__ == '__main__':
    main()
