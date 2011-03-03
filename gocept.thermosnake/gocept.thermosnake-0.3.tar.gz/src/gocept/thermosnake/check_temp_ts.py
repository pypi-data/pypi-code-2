#!/usr/bin/env python

# Copyright (c) 2011 gocept gmbh & co. kg
# See also LICENSE.txt

import nagiosplugin
import os


class CheckThermosnakeTemp(nagiosplugin.Check):

    version = u'0.1'

    def __init__(self, optp, logger):
        """Set up options."""
        optp.add_option(u'-w', u'--warning', metavar=u'RANGE',
            help=u'set WARNING status if value '
            u'does not match RANGE',
            default=u'')
        optp.add_option(u'-c', u'--critical', metavar=u'RANGE',
            help=u'set CRITICAL status if value '
            u'does not match RANGE',
            default=u'')
        optp.add_option(u'-a', u'--address', help=u'Sensor address')
        optp.add_option(u'-l', u'--location', help=u'Sensor location')
        self.log = logger

    @property
    def name(self):
        return 'Temperature at: %s' % self.location

    def process_args(self, opts, args):
        self.warn = opts.warning
        self.crit = opts.critical
        self.address = opts.address
        self.location = opts.location

    def get_temp(self):
        CMD_RPS = 'measuretemp -s %s' % self.address

        cmd = os.popen(CMD_RPS)
        output = cmd.read()
        if not output:
            raise ValueError("Couldn't get output from measuretemp")
        cmd.close()
        self.temp = output
        self.log.info(u'Temperature at %s: %s' % (
                self.location, self.temp))

    def obtain_data(self):
        self.get_temp()
        self.measures = [nagiosplugin.Measure(
            u'temperature', float(self.temp), warning=self.warn, critical=self.crit,
            minimum=0)]

    def default_message(self):
        return u'%s (%s)' % (self.temp, self.location)


main = nagiosplugin.Controller(CheckThermosnakeTemp)
if __name__ == '__main__':
    main()
