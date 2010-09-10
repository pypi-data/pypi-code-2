#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Copyright (C) 2005-2008 Juan David Ibáñez Palomar <jdavid@itaapy.com>
# Copyright (C) 2006-2007 Hervé Cauwelier <herve@itaapy.com>
# Copyright (C) 2007 Sylvain Taverne <sylvain@itaapy.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Import from the Standard Library
from optparse import OptionParser
from os import mkdir
import sys

# Import from itools
import itools
from itools.core import start_subprocess

# Import from ikaaro
from ikaaro.database import make_database
from ikaaro.resource_ import DBResource
from ikaaro.root import Root
from ikaaro.utils import generate_password
from ikaaro.server import get_fake_context


template = (
"""# The "modules" variable lists the Python modules or packages that will be
# loaded when the applications starts.
#
modules = {modules}

# The "listen-address" and "listen-port" variables define, respectively, the
# internet address and the port number the web server listens to for HTTP
# connections.
#
# These variables are required (i.e. there are not default values).  To
# listen from any address write the value '*'.
#
listen-address = 127.0.0.1
listen-port = {listen_port}

# The "smtp-host" variable defines the name or IP address of the SMTP relay.
# The "smtp-from" variable is the email address used in the From field when
# sending anonymous emails.  (These options are required for the application
# to send emails).
#
# The "smtp-login" and "smtp-password" variables define the credentials
# required to access a secured SMTP server.
#
smtp-host = {smtp_host}
smtp-from = {smtp_from}
smtp-login =
smtp-password =

# The "log-level" variable may have one of these values (from lower to
# higher verbosity): 'critical' 'error', 'warning', 'info' and 'debug'.
# The default is 'warning'.
#
log-level = warning

# The "database-size" variable defines the number of file handlers to store
# in the database cache.  It is made of two numbers, the upper limit and the
# bottom limit: when the cache size hits the upper limit, handlers will be
# removed from the cache until it hits the bottom limit.
#
database-size = 4800:5200

# If the "profile-time" variable is set to "1", profiling information will
# be written to the 'log/profile' file.  If the "profile-space" variable is
# set to "1", remote monitoring will be enabled (see http://guppy-pe.sf.net/
# to learn more).
#
profile-time = 0
profile-space = 0

# The "index-text" vairable defines whether the catalog must process full-text
# indexing. It requires (much) more time and third-party applications.
# To speed up catalog updates, set this option to 0 (default is 1).
index-text = 1
""")



def init(parser, options, target):
    try:
        mkdir(target)
    except OSError:
        parser.error('can not create the instance (check permissions)')

    # Get the email address for the init user
    if options.email is None:
        sys.stdout.write("Type your email address: ")
        email = sys.stdin.readline().strip()
    else:
        email = options.email

    # Get the password
    if options.password is None:
        password = generate_password()
    else:
        password = options.password

    # Load the root class
    if options.root is None:
        root_class = Root
        modules = ''
    else:
        modules = options.root
        exec('import %s' % modules)
        exec('root_class = %s.Root' % modules)

    # The configuration file
    namespace = {
        'modules': modules,
        'listen_port': getattr(options, 'port') or '8080',
        'smtp_host': getattr(options, 'smtp_host') or 'localhost',
        'smtp_from': email,
    }
    config = template.format(**namespace)
    open('%s/config.conf' % target, 'w').write(config)

    # Create the folder structure
    start_subprocess('%s/database' % target)
    database = make_database(target)
    mkdir('%s/log' % target)
    mkdir('%s/spool' % target)

    # Create a fake context
    context = get_fake_context()
    context.database = database

    # Make the root
    folder = database.get_handler('.')
    root = root_class._make_resource(root_class, folder, email, password)
    context.root = root
    # Save changes
    database.save_changes()
    # Index
    catalog = database.catalog
    for resource in root.traverse_resources():
        if isinstance(resource, DBResource):
            catalog.index_document(resource)
    catalog.save_changes()

    # Bravo!
    print '*'
    print '* Welcome to ikaaro'
    print '* A user with administration rights has been created for you:'
    print '*   username: %s' % email
    print '*   password: %s' % password
    print '*'
    print '* To start the new instance type:'
    print '*   icms-start.py %s' % target
    print '*'



if __name__ == '__main__':
    # The command line parser
    usage = '%prog [OPTIONS] TARGET'
    version = 'itools %s' % itools.__version__
    description = 'Creates a new instance of ikaaro with the name TARGET.'
    parser = OptionParser(usage, version=version, description=description)
    parser.add_option('-e', '--email',
                      help='e-mail address of the admin user')
    parser.add_option('-p', '--port', type='int',
                      help='listen to PORT number')
    parser.add_option('-r', '--root',
        help='create an instance of the ROOT application')
    parser.add_option('-s', '--smtp-host',
        help='use the given SMTP_HOST to send emails')
    parser.add_option('-w', '--password',
        help='use the given PASSWORD for the admin user')
    parser.add_option('--profile',
        help="print profile information to the given file")

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('incorrect number of arguments')

    target = args[0]

    # Action!
    if options.profile is not None:
        from cProfile import runctx
        runctx("init(parser, options, target)", globals(), locals(),
               options.profile)
    else:
        init(parser, options, target)
