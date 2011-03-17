#!/usr/bin/env python

'''py2thefacer - Python based Picasa Face Recognition to Flickr tool.
'''

license = ''' Copyright (C) 2011  <see AUTHORS file>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from py2facer.commands import base
from py2facer.lib import utils
import logging
import logging.config

LOGGER = logging.getLogger('main')

def main():
    args = base.CLI_PARSER.parse_args()
    cmd = args.COMMAND()
    cmd.execute(cli_args=args)
    
if __name__ == '__main__':
    log_config = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {'format': '%(levelname)s %(asctime)s %(name)s %(message)s' },
            'simple': { 'format': '%(levelname)s %(message)s' },
        },
        'filters' : {
            'picasa' : {'()' : utils.LogClassFilter,
                        'name' : 'picasa.ContactParser',
                        },
        },
        'handlers' : {
            'console' : {'class' : 'logging.StreamHandler',
                         'formatter' : 'verbose'},
            'simple_console' : {'class' : 'logging.StreamHandler',
                                'formatter' : 'simple',
                                },
            'null' : {'class' : 'logging.NullHandler'}
        },
        'loggers' : {
            'commands' : {},
            'lib' : {},
            'lib.picasa.ContactParser' : {'propagate' : False,
                                      'handlers' : ['null']}
        },
        'root' : {'level' : 'DEBUG', 'handlers' : ['console',]},
 }
    logging.config.dictConfig(log_config)
    main()
