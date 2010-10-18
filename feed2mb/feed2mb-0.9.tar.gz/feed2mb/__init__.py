# -*- coding: utf-8 -*-
# feed2mb
# Copyright (C) 2009 EBC - Empresa Brasil de Comunicação
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import feedparser, pickle, os, sys, urllib, twitter
from ConfigParser import ConfigParser, NoOptionError
from options import Options
import re, time
from pprint import pprint

from config import MicroblogConfig
import microblog
import os
import tempfile
import logging
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

def update(**kwargs):
    if not kwargs:
        opt = Options()
        options = opt.parse()

        if options.show_version:
	    global __version__
            print(__version__)
            sys.exit(1)

        if options.sample_config:
            from pkg_resources import resource_string
            foo_config = resource_string(__name__, '../docs/default.cfg.sample')
            print(foo_config)
            sys.exit(1)
        if options.log_filename:
            fh = logging.FileHandler(options.log_filename)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            fh.setFormatter(formatter)
            log.addHandler(fh)
#            microblog.log.addHandler(fh)
        else:
            logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            )

        conf = MicroblogConfig(options.config_filename)
        configs = conf.configs()
    else:
        configs=[]
        kwargs['items'] = 5
        configs.append(kwargs)
        url = kwargs['url']
        shortener = kwargs['shortener']
        kwargs['interval'] = parsetime('00:05')
    pid = os.getpid()
    log.debug('Starting feed2mb with pid: ' + str(pid))
    if not configs[0]['pidfile']:
	pidfile = tempfile.NamedTemporaryFile()
    else:
	pidfile = open(configs[0]['pidfile'], 'w+b')

    pidfile.write(str(pid))
    pidfile.flush()
#        pidfile.close()
    log.debug('PID saved in: ' + pidfile.name)
#    print(configs)
#    sys.exit()
    try:
        while True:
            interval = configs[0]['interval']
            for cf in configs:
                the_service = microblog.service(**cf).get()
                the_service.update()
                log.debug('next ' + cf['service'] + ' update in: ' + str(interval) + ' seconds')
		del(the_service)
            time.sleep(interval)
    finally:
	pidfile.close()
	try:
		os.remove(configs[0]['pidfile'])
	except:
		pass



__version__ = '0.9'

