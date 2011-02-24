# -*- coding: utf-8 -*-
#
#  Copyright (c) 2010 George Notaras, G-Loaded.eu, CodeTRAX.org
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import sys
import os
import pwd
from optparse import OptionParser
import ConfigParser
import logging
import re
import shutil


__version__ = '0.2.0'

logger = logging.getLogger()

class RMexpressConfigParser(ConfigParser.RawConfigParser):

    VALID_CONFIG_FILE_PATHS = [
        '/usr/local/etc/rmexpress.conf',
        '/etc/rmexpress.conf',
        # TODO: Add more locations
        ]

    def getlist(self, section, option):
        """Returns a list of strings.
        
        Expects a comma-delimited list of strings as the option value.
        
        Multi-line value is supported.
        
        """
        value_list = self.get(section, option)
        return [value.strip() for value in value_list.split(',') if value.strip()]

def verify_user(user, uid):
    """Verifies the username and the UID.
    
    Verifies that the username retrieved from the environment variable
    SUDO_USER corresponds to the UID retrieved from the environment variable
    SUDO_UID.
    
    """
    return uid == str(pwd.getpwnam(user)[2])

def path_is_in_user_homedir(homedir, path):
    """Verifies that the path to be deleted exists inside the user's
    home directory.

    """
    homedir = homedir.rstrip(os.path.sep)
    path = path.rstrip(os.path.sep)
    if not path.startswith(homedir):    # check if path is under homedir
        return False
    elif len(path) == len(homedir):     # check if path is the homedir itself
        return False
    return True

def make_absolute_patterns(homedir, patterns):
    """The homedir is prepended to every pattern.
    
    ``homedir`` should already be an absolute path.
    
    """
    return [os.path.join(homedir, pattern.lstrip(os.path.sep)) for pattern in patterns if pattern]

def pattern_match(patterns, path):
    """Iterate over the patterns and try to find a match.
    
    """
    logger.debug('trying %d patterns...' % len(patterns))
    for pattern in patterns:
        if re.match(pattern, path):
            logger.debug('pattern MATCH: %s' % pattern)
            return True
        logger.debug('pattern not matched: %s' % pattern)

def parse_cli():
    usage = '%prog [options] <path>'
    parser = OptionParser(usage=usage, version=__version__)
    # The --config option is a potential security hole, so this is commented out.
    #parser.add_option('-c', '--config', dest='config', default='/etc/rmexpress.conf', metavar='PATH', help='The path to the configuration file. Default: %default')
    parser.add_option('-d', '--debug', dest='debug', action="store_true", help='Print debug messages.')
    parser.add_option('-t', '--test', dest='test', action="store_true", help='Run normally but do not perform the deletion, even if a match is found.')
    
    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error('Wrong number of arguments')
    return options, args

def main():
    logger.setLevel(logging.INFO)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(logging.Formatter('%(levelname)-8s %(message)s'))
    logger.addHandler(stderr_handler)
    
    logger.info('using: %s v%s' % ( os.path.basename(sys.argv[0]), __version__))

    options, args = parse_cli()
    
    if options.debug:
        logger.setLevel(logging.DEBUG)
    if options.test:
        logger.info('running in testing mode. no deletions will be performed')

    cfg = RMexpressConfigParser()
    cfg.read(RMexpressConfigParser.VALID_CONFIG_FILE_PATHS)

    env = os.environ

    path = os.path.abspath(args[0])
    logger.debug('path: %s' % path)

    user = env['SUDO_USER']
    logger.debug('user: %s' % user)

    homedir = os.path.join(cfg.get('main', 'homes_base_dir'), user)
    homedir = os.path.abspath(homedir)  # Ensure we read an absolute homedir path
    logger.debug('home: %s' % homedir)

    patterns = cfg.getlist('main', 'valid_dir_patterns_under_home')
    patterns = make_absolute_patterns(homedir, patterns)

    if not verify_user(env['SUDO_USER'], env['SUDO_UID']):
        logger.error('could not verify user: %s' % env['SUDO_USER'])
        sys.exit(1)
    elif not path_is_in_user_homedir(homedir, path):
        logger.error('path is outside user\'s home directory: %s' % homedir)
        sys.exit(1)
    elif patterns and not pattern_match(patterns, path):
        logger.error('path did not match a pattern. will not delete')
        sys.exit(1)
    elif not os.path.exists(path):
        logger.error('path does not exist: %s' % path)
        sys.exit(1)
    else:
        if os.path.isfile(path):
            if not options.test:
                os.remove(path)
            logger.info('successful file deletion: %s' % path)
        elif os.path.isdir(path):
            if not options.test:
                shutil.rmtree(path, ignore_errors=False)
            logger.info('successful recursive directory deletion: %s' % path)

if __name__ == '__main__':
    main()

