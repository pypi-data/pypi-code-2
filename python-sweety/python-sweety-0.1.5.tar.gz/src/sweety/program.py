#!/usr/bin/env python
'''
sweety.program

@author: Chris Chou <m2chrischou AT gmail.com>
@description: 
'''

import datetime
import exceptions as E
import getopt
import logging
import os
import sys
import traceback
import types

reload(sys)
sys.setdefaultencoding('utf-8')

from sweety.log import get_logger
from sweety import settings
from sweety import error

class OptionManager(object):
    def __init__(self):
        self.usage = '<Usage>'
        self.header = '<Header>'
        self.footer = '<Footer>'
        self.options = {}
        self._options_list = []
        self.environments = {}
        self._environments_list = []

    def add_environment(self, varname, description, argument = None, default = '', repeat = False, delimiter = ',', name = None):
        '''
        Add environment specification.
        
        @param varname: specify the environment variable name.
        @param description: specify the description of the option.
        @param argument: specify the argument.
        @param default: specify the default value.
        @param repeat: specify whether repeatable.
        @param delimiter: specify the delimiter for repeatable argument.
        @param name: specify the option name. [default: env_{varname}]
        '''
        obj = {
                                  'varname': varname,
                                  'description': description,
                                  'argument': argument,
                                  'default': default,
                                  'repeat': repeat,
                                  'delimiter': delimiter,
                                  'name': name
                                  }

        self.environments[varname] = obj
        self._environments_list.append(obj)

    def add_option(self, short, long, description, argument = None, default = '', required = False, repeat = False, delimiter = ',', name = None):
        '''
        Add option specification.
        
        @param short: specify the short option character.
        @param long: specify the long option text.
        @param description: specify the description of the option.
        @param argument: specify the argument.
        @param default: specify the default value.
        @param required: specify whether the option is required.
        @param repeat: specify whether repeatable.
        @param delimiter: specify the delimiter for repeatable argument.
        @param name: specify the option name. [default: opt_{long}]
        '''
        obj = {
                             'short' : short,
                             'long' : long,
                             'description' : description,
                             'argument': argument,
                             'default' : default,
                             'required': required,
                             'repeat': repeat,
                             'delimiter': delimiter,
                             'name': name
                             }
        self.options[long] = self.options[short] = obj
        self._options_list.append(obj)

    def add_option_group(self, groupname):
        self.add_option('@%s' % groupname, '', '')

    def parse_environment(self):
        '''
        Parse environment variables.
        '''
        ret = {}
        for k in os.environ:
            v = os.environ[k]

            if isinstance(v, (str, unicode)):
                v = os.path.expanduser(v)
                v = os.path.expandvars(v)

            if self.environments.has_key(k):
                env = self.environments[k]

                name = env['name']
                if not name:
                    name = 'env_%s' % env['varname']

                argument = None
                if env['argument']:
                    argument = v

                    if env['repeat']:
                        argument = argument.split(env['delimiter'])
                    ret[name] = argument
                else:
                    ret[name] = True

        return ret

    def parse_options(self):
        '''
        Parse options
        '''
        shortopts = set()
        longopts = set()

        for k in self.options:
            opt = self.options[k]

            if opt['argument']:
                if opt['short']:
                    shortopts.add('%s:' % opt['short'][0])
                if opt['long']:
                    longopts.add('%s=' % opt['long'])
            else:
                if opt['short']:
                    shortopts.add('%s' % opt['short'][0])
                if opt['long']:
                    longopts.add('%s' % opt['long'])

        shortopts = ''.join(shortopts)
        opts, args = getopt.getopt(sys.argv[1:], shortopts, longopts)

        #print longopts, shortopts

        ret = {}
        for k, v in opts:

            k = k.strip('-=')

            if isinstance(v, (str, unicode)):
                v = os.path.expanduser(v)
                v = os.path.expandvars(v)

            if self.options.has_key(k):
                opt = self.options[k]

                name = opt['name']
                if not name and opt['long']:
                    name = 'opt_%s' % opt['long']
                elif not name and opt['short']:
                    name = 'opt_%s' % opt['short']

                argument = None
                if opt['argument']:
                    argument = v

                    if opt['repeat']:
                        if not ret.has_key(name):
                            ret[name] = []
                        ret[name].extend(argument.split(opt['delimiter']))
                    else:
                        ret[name] = argument
                else:
                    ret[name] = True

        for i, v in enumerate(list(args)):
            if isinstance(v, str):
                v = os.path.expanduser(v)
                v = os.path.expandvars(v)
            args[i] = v

        return ret, args


    def handle(self):
        '''
        Handle command line arguments and environment variables.
        '''
        ret = {}

        # update env default
        for k in self.environments:
            env = self.environments[k]
            if env['default']:
                name = env['name']
                if not name:
                    name = 'env_%s' % env['varname']

                if env['repeat']:
                    ret[name] = env['default'].split(env['delimiter'])
                else:
                    ret[name] = env['default']

        # update opt default and record required names
        required = {}
        for k in self.options:
            opt = self.options[k]

            name = opt['name']
            if not name and opt['long']:
                name = 'opt_%s' % opt['long']
            elif not name and opt['short']:
                name = 'opt_%s' % opt['short']

            if opt['default']:

                if opt['repeat']:
                    ret[name] = opt['default'].split(opt['delimiter'])
                else:
                    ret[name] = opt['default']

            if opt['required']:
                required[name] = opt

        ret.update(self.parse_environment())
        opts, args = self.parse_options()
        ret.update(opts)

        return ret, args

    def check_required(self, opts):

        required = {}
        for k in self.options:
            opt = self.options[k]

            name = opt['name']
            if not name and opt['long']:
                name = 'opt_%s' % opt['long']
            elif not name and opt['short']:
                name = 'opt_%s' % opt['short']

            if opt['required']:
                required[name] = opt

        # check required
        for name in required:
            if not opts.has_key(name):
                opt = required[name]
                if opt['long']:
                    optstr = '--%s' % opt['long']
                else:
                    optstr = '-%s' % opt['short']
                return 'Option %s required' % optstr

        return ''


    def format_help(self):
        '''
        Format help string.
        '''
        optlines = []
        envlines = []

        track = set()

        maxlength = 0
        for opt in self._options_list:
            #opt = self.options[k]

            if '%s_%s' % (opt['short'], opt['long']) in track:
                continue

            track.add('%s_%s' % (opt['short'], opt['long']))

            if opt['short'].startswith('@'):
                optlines.append(['', ''])
                optlines.append(['%s:' % opt['short'][1:], ''])
                continue

            shortpart = ''
            if opt['short']:
                shortpart = '-%s' % opt['short'][0]

            longpart = ''
            if opt['long']:
                longpart = '--%s' % opt['long']

            if opt['argument']:
                if longpart:
                    longpart = '%s=<%s>' % (longpart, opt['argument'])
                else:
                    shortpart = '%s <%s>' % (shortpart, opt['argument'])

            if shortpart and longpart:
                titlepart = '  %s|%s' % (shortpart, longpart)
            elif shortpart:
                titlepart = '  %s' % shortpart
            elif longpart:
                titlepart = '     %s' % longpart

            if maxlength < len(titlepart):
                maxlength = len(titlepart)

            description = opt['description']
            if opt['default']:
                description = '%s [default: %s]' % (description, opt['default'])
            if opt['required']:
                description = '%s [required]' % description
            if opt['repeat']:
                description = '%s [repeatable]' % description

            optlines.append([titlepart, description])

        for env in self._environments_list:
            #env = self.environments[k]

            if env['argument']:
                titlepart = '  % s=<%s> ' % (env['varname'], env['argument'])
            else:
                titlepart = '  % s' % env['varname']

            if maxlength < len(titlepart):
                maxlength = len(titlepart)

            description = env['description']
            if env['default']:
                description = '%s [default: %s]' % (description, env['default'])

            envlines.append([titlepart, description])

        if maxlength < 24:
            maxlength = 24
        ret = []

        if optlines:
            ret.append('Usage: %s' % self.usage)
            ret.append(self.header)
            ret.append('')
            ret.append('Options:')
            for l in optlines:
                ret.append('%-*s  %s' % (maxlength, l[0], l[1]))

        if envlines:
            ret.append('')
            ret.append('Environment:')
            for l in envlines:
                ret.append('%-*s  %s' % (maxlength, l[0], l[1]))

        if self.footer:
            ret.append('')
            ret.append(self.footer)

        ret.append('')

        return '\n'.join(ret)

class Program(OptionManager):

    def __init__(self):
        super(Program, self).__init__()

        self.log = get_logger(self)

        self.exitcode = 0

        self.starttime = datetime.datetime.now()

        self.add_option('h', 'help', 'display help information.')
        self.add_option('V', 'version', 'display version information.')
        self.add_option('v', 'verbose', 'turn on verbose mode.')

        self.add_environment('SWEETY_VERBOSE', 'turn on verbose mode.')
        self.add_environment('SWEETY_LOG_FILENAME', 'specify the log filename.', 'filename')

        self._output = []

        #if not self.HELP_FILE:
        #    self.HELP_FILE = self.__class__.__name__

    def __getattr__(self, key):
        if key.startswith('opt_') or key.startswith('env_'):
            return ''

    def help(self):
        '''
        help(self) -> None

        Displays help information.
        '''
        print self.format_help()

    def version(self):
        '''
        version(self) -> None

        Displays version information.
        '''
        verdir = os.path.join(
                        os.path.dirname(self.version.func_code.co_filename),
                        '../../..'
                        )
        verfile = os.path.join(verdir, 'VERSION')

        try:
            fd = open(verfile)
        except:
            print 'Failed to display version information.'
            return False


        print 'Version : %s' % fd.read().strip()
        print 'Author  : Chris Chou <yunzhi@yahoo-inc.com>'
        print '          Chengl <chengl@yahoo-inc.com>'

        fd.close()

        return True

    def set_exitcode(self, exitcode):
        self.exitcode = exitcode

    def alert(self):
        '''
        TODO:
        '''
        raise E.NotImplementedError()

    def exit(self, status):
        '''
        exit(self, status) -> None
        
        Exits the program.
        
        @param status: a boolean value indicates whether is normal.
        '''

        retmsg = 'Status OK'
        retcode = 0
        if callable(status):
            retcode = status()
            retmsg = '%s returns %s' % (str(status), str(retcode))
        elif isinstance(status, str):
            retmsg = status
            retcode = 1
        elif isinstance(status, bool):
            retmsg = 'main() returns %s' % str(status)
            retcode = int(not status)
        elif isinstance(status, (int, long)):
            if status:
                retmsg = 'Status code %d' % status
                retcode = status
        else:
            retmsg = 'Unknown error occurred.'
            retcode = 255

        if retcode:
            if os.environ.has_key('SWEETY_ALERT') and os.environ['SWEETY_ALERT']:
                self.alert(retcode, retmsg, 'Please refer to the log for detailed information.')

            self.log.error('Exiting with error - [%d] %s' % (retcode, retmsg))
        else:
            retmsg = '%s: %s' % (os.path.basename(sys.argv[0]), retmsg)
            self.log.info('Exiting normally - [%d] %s' % (retcode, retmsg))

        logging.shutdown()

        sys.exit(retcode)

    def main(self, opts, args):
        '''
        main(self, opts, args) -> status code
        
        Executes the program specific logic.
        
        @param opts: command line _options
        @param args: command line arguments
        @return: boolean value indicates whether is normal.
        '''
        raise E.NotImplementedError()

    def cleanup(self):
        for o in self._output:
            o.flush()


def _print_module(module, log):
    for k in dir(module):
        if k.startswith('_'):
            continue

        v = getattr(module, k)
        if isinstance(v, (types.ModuleType, types.FunctionType)):
            continue

        log.info(' ++++ %s: %s' % (k, str(v)))



def mainwrapper(progclass):
    '''
    mainwrapper(progclass) -> status code
    
    Wraps a main function, handling common tasks before proceeding specific logic.
    
    @param progclass: the class implements following functions:
        help() - displays help information.
        version() - displays version information.
        main() - the program entry.
    '''
    log = get_logger('sweety.program.mainwrapper')

    log.info('Program started, command line [%s]' % ' '.join(sys.argv))

    if len(sys.argv) == 3 and sys.argv[1] == '--':
        args = []
        try:
            fd = open(sys.argv[2])
            for l in fd:
                l = l.strip()
                args.extend(l.split(' ', 1))
            fd.close()

            sys.argv[1:] = args
        except:
            pass

        del fd

    log.info('Program actual command line [%s]' % ' '.join(sys.argv))

    log.info('Environment variables:\n%s' % '\n'.join(
        [' +++ %s: %s' % (k, os.environ[k]) for k in os.environ]
        ))

    log.info('Printing settings:')
    _print_module(settings, log)

    # hack
    if '-v' in sys.argv or '--verbose' in sys.argv:
        os.environ['SWEETY_VERBOSE'] = '1'

    prog = progclass()
    prog.starttime = datetime.datetime.now()

    try:
        opts, args = prog.handle()
    except:
        errinfo = traceback.format_exc()

        log.error(errinfo)

        prog.exit("Failed to parse command line options.")

    #print opts, args

    verbose = False
    if opts.has_key('opt_verbose'):
        verbose = True
    if verbose:
        os.environ['SWEETY_VERBOSE'] = '1'

    if opts.has_key('opt_help'):
        prog.help()
        prog.exit(True)

    if opts.has_key('opt_version'):
        prog.version()
        prog.exit(True)

    requiredmsg = prog.check_required(opts)
    if requiredmsg:
        log.warning(requiredmsg)
        prog.help()
        prog.exit("")


    for k in opts:
        setattr(prog, k, opts[k])

    ret = True
    try:
        ret = prog.main(opts, args)
        prog.cleanup()
    except:
        errinfo = traceback.format_exc()

        log.error(errinfo)

        prog.exit(False)
    else:
        log.info('Exiting normally.')

    prog.exit(ret)


