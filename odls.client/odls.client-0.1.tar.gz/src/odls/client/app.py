"""The main odls client application.
"""
##
## app.py
## Login : <uli@pu.smp.net>
## Started on  Tue Apr 20 15:50:34 2010 Uli Fouquet
## $Id$
## 
## Copyright (C) 2010 Uli Fouquet
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
## 
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
## 
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##
import logging
import signal
import sys
import time
from odls.client.configuration import ODLSConfiguration, VERSION
from odls.client.http import ODLSHTTPClient
from odls.client.iowatchdog import ODLSIOWatcher
from odls.client.logger import init_logger
from odls.client.parsermanager import ODLSParserManager

class ODLSClient(object):
    """The main ODLS client.

    The client starts the needed component, controls their flow and
    pulls the emergency break if neccessary.
    """

    #: The configuration of the client.
    config = None
    shutdown = False
    _logger = None
    _evt_receivers = dict()

    @property
    def logger(self):
        """The logger.
        """
        if self._logger is None:
            self._logger = logging.getLogger(self.config.options.logname)
        return self._logger

    def __init__(self):
        self.config = ODLSConfiguration()
        init_logger(self.config.options)
        self._evt_receivers = dict()
    
    def run(self):
        """Start the client.
        """
        self.logger.info('Starting ODLS client (Python) v%s' % VERSION)
        version = sys.version.replace('\n', ' ')
        self.logger.debug('Using Python %s' % version)
        try:
            self.io_watcher = ODLSIOWatcher(self)
            self.parser_manager = ODLSParserManager(self)
            self.http_client = ODLSHTTPClient(self)
        except ValueError:
            self.logger.error('FATAL ERROR!')
            self.logger.error('%s' % (sys.exc_info()[1]))
            self.logger.error('Aborting.')
            self.stop()
            return
        print "Started."
        self._run_forever()

    def stop(self):
        """Shutdown all components properly.
        """
        for component in [
            'parser_manager', 'io_watcher', 'http_client']:
            if not hasattr(self, component):
                # Only handle subcomponents that could be created.
                continue
            getattr(self, component).stop()
        return

    def _run_forever(self):
        """The main service loop.
        """
        def signal_handler(signal, frame):
            self.logger.info('Received signal %s' % signal)
            self.shutdown = True
            print "Stopping..."

        signal.signal(signal.SIGINT, signal_handler)
        while True and not self.shutdown:
            start_time = time.time()
            self.http_client.sendUnsentChanges()
            new_changes = self.io_watcher.getChanges()
            self.http_client.sendChanges(new_changes)
            
            elapsed = time.time() - start_time
            sleeptime = self.config.options.watch_updatetime - elapsed
            self.logger.info('Sleeping for %s seconds', sleeptime)
            time.sleep((sleeptime > 0 and sleeptime) or 0)
        self.logger.info('Shutting down...')
        self.stop()
        self.logger.info('Done.')
        sys.exit(0)

    def _handleChange(self, change):
        """React on a filesystem change.
        """
        return
