# LinkExchange - Universal link exchange service client
# Copyright (C) 2009-2011 Konstantin Korikov
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# NOTE: In the context of the Python environment, I interpret "dynamic
# linking" as importing -- thus the LGPL applies to the contents of
# the modules, but make no requirements on code importing these
# modules.

import sys
import os.path
import optparse
import logging

from linkexchange.config import file_config, ConfigError

def main():
    op = optparse.OptionParser(
            usage = "%prog -c linkexchange.cfg [other options] [name=value...]",
            description = (
                "Refresh links database using configuration from linkexchange.cfg. "
                "Interpolation variables can be specified in arguments using "
                "name=value format."))

    op.add_option('-c', '--config',
            dest='config',
            default=None,
            help="specify path to LinkExchange configuration file",
            metavar="FILE")
    op.add_option('-r', '--request-url',
            dest='request_url',
            default=None,
            help="request URL or domain",
            metavar="URL")
    op.add_option('-q', '--quiet',
            dest='quiet',
            action='store_true',
            default=False,
            help="suppress all normal output")
    op.add_option('--debug',
            dest='debug',
            action='store_true',
            default=False,
            help="print debug output")

    (opts, args) = op.parse_args()
    op.print_usage = lambda file=None: None

    if not opts.config:
        op.error("you must specify configuration file with -c "
                "or --config option!")

    interpolation = dict(
            basedir=os.path.abspath(os.path.dirname(opts.config)))
    for arg in args:
        try:
            k, v = arg.split('=', 1)
        except ValueError:
            op.error("%s is not seems like name=value")
        interpolation[k] = v

    log = logging.getLogger()
    log_hdl = logging.StreamHandler(sys.stderr)
    log.addHandler(log_hdl)
    if opts.debug:
        log.setLevel(logging.DEBUG)
    elif opts.quiet:
        log.setLevel(logging.CRITICAL)
    else:
        log.setLevel(logging.WARNING)

    vars = {}
    try:
        file_config(vars, opts.config,
                defaults=interpolation)
    except ConfigError, e:
        op.error(str(e))

    request_url = opts.request_url
    if request_url is None:
        request_url = vars['options'].get('host', None)
    if not request_url:
        op.error("host undefined! you need to set the host option in "
                "the linkexchange.cfg or pass -r option at the comment line.")
    if '://' not in request_url:
        request_url = 'http://' + request_url

    vars['platform'].refresh_db(request_url)
    return 0

if __name__ == '__main__':
    sys.exit(main())
