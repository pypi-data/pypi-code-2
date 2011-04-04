"""
So, processing in three stages:

* Specify the details for each command and sub-command
* Parse the main command and extract the data
* Parse the sub-command
  if anything left over, raise an error
* Convert the options to internal variables
* Run the sub-command

Global arguments are a very bad idea because it means you can't access the
sub-command's help without specifying them. This is rather confusing behaviour
for users.

Approaches which didn't work very well:

Using the docstring of the handler in reStructuredText, converting it to HTML
and piping it through a text-based web browser to generate command line help

    The reason is that it is a pain to regenerate the correct help strings and
    man pages so you just don't bother. At the same time it is more useful than
    expected to have the sub commands and options automatically documented.

Using the same reStructuedText to and rst2man to automatically generate a man
page

    Same reason, you just don't bother keeping the man page up to date.

Allowing options anywhere and trying to decide whether they are command or
sub-command options.

    It is possible, as long as all sub-commands treat all of the options in the
    same way. For example if --quiet is a flag in one sub-command it can't take an
    option in another. This proves overly restrictive.

Restrictions I've added to the default implementation of ``to_internal()``
which are easily ignored with a custom ``convert()`` function.

* Multiple flags of the same type are disallowed
* If an option doesn't use a metavar it is made True if it exists, False otherwise.
"""

import getopt
import logging
import sys
import os
from logging.config import fileConfig

from recipes_267662 import wrap_onspace_strict, indent
from bn import AttributeDict

log = logging.getLogger(__name__)

def to_internal(option_spec, parsed_options):
    internal = AttributeDict()
    for k, v in option_spec.items():
        if not v.get('metavar', ''):
            if v.get('multiple', ''):
                internal[k] = []
            else:
                internal[k] = False
    options_used = AttributeDict()
    values_used = AttributeDict()
    position = AttributeDict()
    i = -1
    for pair in parsed_options:
        i += 1
        option, value = pair
        for int_var, opt in option_spec.items():
            if option in opt.get('options', []):
                if not opt.get('metavar', '') and value:
                    raise getopt.GetoptError(
                        'The argument %r after %r was unexpected'%(
                            value, 
                            option
                        )
                    )
                # Make this check optional at some point
                multiple = opt.get('multiple', False)
                if options_used.has_key(int_var) and not multiple:
                    raise getopt.GetoptError(
                        'The option %r is unexpected (the related option %r '
                        'has already been used)'%( 
                            option,  
                            options_used[int_var][-1], 
                        )
                    )
                else:
                    if opt.get('metavar', ''):
                        if multiple:
                            if not internal.has_key(int_var):
                                internal[int_var] = [value]
                            else:
                                internal[int_var].append(value)
                        else:
                            internal[int_var] = value
                    else:
                        if multiple:
                            internal[int_var].append(True)
                        else:
                            internal[int_var] = True
                    if options_used.has_key(int_var):
                        options_used[int_var].append(option)
                        values_used[int_var].append(value)
                        position[int_var].append(i)
                    else:
                        options_used[int_var] = [option]
                        values_used[int_var] = [value]
                        position[int_var] = [i]
    log.debug('Internal: %r', internal)
    return AttributeDict(opts=internal, options=options_used, values=values_used, position=position)

def check_command(name, command):
    if name is None and not isinstance(command.arg_spec, (list, tuple)):
        if name is None: 
            name='main'
        else:
            name = repr(name)
        raise Exception(
            'Expected a tuple or list if (name, help) pairs for \'args\' in '
            'the %s command, not %r'%(
                name, 
                command.arg_spec,
            )
        )
    if isinstance(command, dict):
        for name_, command_ in command.items():
            check_command(name_, command_)
    else:
        for k, opt in command.option_spec.items():
            for options in opt.get('options', []):
                if not options.startswith('-'):
                    raise Exception(
                        'Expected the %r option for the %r variable in command '
                        '%r to start with the characters \'--\' or \'-\''%(
                            options, k, name
                        )
                    )

#
# Help helpers
#

def two_cols(rows):
    i = [0]
    def wrapper(x):
        if len(x) < 20:
            x += (20-len(x))*' '
        i[0] += 1
        if i[0]%2:
            return wrap_onspace_strict(x, 25)
        else:
            return wrap_onspace_strict(x, 49)
    return indent(
        rows, 
        hasHeader=False, 
        prefix='  ', 
        postfix='', 
        headerChar='', 
        delim='  ', 
        separateRows=False,
        wrapfunc=wrapper
    )

def usage(commands, name, program):
    help = 'Usage: %s '%program
    if commands[None].option_spec:
        help += '[OPTIONS] '
    if commands[None].arg_spec:
        for parts in commands[None].arg_spec:
            if isinstance(parts[0], int):
                help += parts[3]+' '
            else:
                help += parts[0]+' '
    if name is None:
        help += 'COMMAND '
    else:
        help += name+' '
    if name is not None:
        help += '[OPTIONS] '
        if commands[name].arg_spec:
            for parts in commands[name].arg_spec:
                if isinstance(parts[0], int):
                    arg_name = parts[3]
                else:
                    arg_name = parts[0]
                help += arg_name + ' '
        help = help[:-1]
    return help

def global_options(commands, name, program):
    help = ''
    rows = []
    for int_value, opt in commands[None].option_spec.items():
        cur_opts = []
        if not opt.get('metavar'):
            cur_opts += opt.get('options', [])
        else:
            metavar = opt.get('metavar')
            for option in opt.get('options', []):
                if option.startswith('--'):
                    cur_opts.append('%s=%s'%(option, metavar))
                else:
                    cur_opts.append('%s %s'%(option, metavar))
        rows.append((' '.join(cur_opts), opt.get('help', '')))
    if rows:
        help += 'Options:\n'
        help += two_cols(rows)
    return help

def global_args(commands, name, program):
    help = ''
    rows = []
    for parts in commands[None].arg_spec:
        if isinstance(parts[0], int):
            arg_name = parts[3]
        else:
            arg_name = parts[0]
        rows.append((arg_name, parts[1]))
    if rows:
        help += 'Global arguments:\n'
        help += two_cols(rows)
    return help

def sub_command_options(commands, name, program):
    help = ''
    rows = []
    for int_value, opt in commands[name].option_spec.items():
        cur_opts = []
        cur_opts += opt.get('options', [])
        rows.append((' '.join(cur_opts),  opt.get('help', '')))
    if rows:
        help += "Command '%s' options:\n"%name
        help += two_cols(rows)
    return help

def sub_command_args(commands, name, program):
    help = ''
    rows = []
    for parts in commands[name].arg_spec:
        if isinstance(parts[0], int):
            arg_name = parts[3]
        else:
            arg_name = parts[0]
        rows.append((arg_name, parts[1]))
    if rows:
        help += "Command '%s' arguments:\n"%(name)
        help += two_cols(rows)
    return help

def sub_commands(commands, name, program):
    help = ''
    rows = []
    for sub_command in commands.keys():
        if sub_command is not None:
            if isinstance(commands[sub_command], dict):
                rows.append(
                    (
                        sub_command, 
                        commands[sub_command][None].help.get('summary', '')
                    )
                )
            else:
                rows.append(
                    (
                        sub_command, 
                        commands[sub_command].help.get('summary', '')
                    )
                )
    if rows:
        help += 'Commands:\n'
        help += two_cols(rows)
    return help

def tip(commands, name, program):
    help = ''
    if name is None:
        if not commands[None].arg_spec:
            args = ''
        else: 
            args = ' '+(' '.join([arg[0] for arg in commands[None].arg_spec]))
        help += (
            '\nType `%(program)s%(args)s COMMAND --help\' ' 
            'for help on individual commands.'
        ) % {
           'program': program,
           'args': args,
        }
    else:
        help += (
            '\nType `%(program)s --help\' for a full list of '
            'commands.'
        ) % {
           'program': program,
        }
    return help

def assemble_help(
    commands, 
    name, 
    program, 
):
    def show_help(service):
        template = commands[name].help.get('template')
        if template is None:
            if name is None:
                # This is a main command help
                template = """%(summary)s
%(usage)s

%(global_options)s

%(global_args)s

%(sub_commands)s

%(tip)s"""
            else:
                template = """%(summary)s
%(usage)s

%(sub_command_options)s

%(sub_command_args)s

%(tip)s"""
        summary = commands[name].help.get('summary')
        if summary is None:
            summary = ''
        else:
            summary = summary
        help = (template % dict(
            summary = summary,
            usage = usage(commands, name, program),
            global_options = global_options(commands, name, program),
            global_args = global_args(commands, name, program),
            sub_command_args = sub_command_args(commands, name, program),
            sub_command_options = sub_command_options(commands, name, program),
            sub_commands = sub_commands(commands, name, program),
            program = program,
            sub_command = name,
            tip = tip(commands, name, program),
        )).strip()
        while '\n\n\n' in help:
            help = help.replace('\n\n\n', '\n\n')
        import textwrap
        output = ''
        for part in help.split('\n'):
            output += '\n'.join(textwrap.wrap(part, 78))+'\n'
        return output.strip()
    return show_help

def process_command(cmd_line_parts, name, command):
    new_cmd_line_parts = cmd_line_parts[:]
    main_short = ''
    main_long = []
    if isinstance(command, dict):
        to_loop = command[None].option_spec.items()
    else:
        to_loop = command.option_spec.items()
    for k, opt in to_loop:
        for options in opt.get('options', []):
            if options.startswith('--'):
                add = opt.get('metavar') and '=' or ''
                main_long.append(options[2:]+add)
            elif options.startswith('-'):
                add = opt.get('metavar') and ':' or ''
                main_short += options[1:]+add
            else: 
                raise Exception('Invalid option %r'%options)
    log.debug('%r %r %r', new_cmd_line_parts, main_short, main_long)
    main_opts, cmd_args = getopt.getopt(
        new_cmd_line_parts, 
        main_short,
        main_long,
    )
    log.debug(
        'Getopt processing for %r: opts: %r args: %r', 
        name, 
        main_opts, 
        cmd_args,
    )
    if name is None:
        main_args = []
        for parts in command.arg_spec:
            if not cmd_args:
                break
            main_args.append(cmd_args.pop(0))
        main_opts_used = False
        if main_opts:
            main_opts_used = True
        for k, v in main_opts:
            index = new_cmd_line_parts.index(k)
            # Remove the option
            new_cmd_line_parts.pop(index)
            # If this is an option with an argument, remove the argument
            if v:
                new_cmd_line_parts.pop(index)
        #for arg in main_args:
        #    import pdb; pdb.set_trace()
        #    new_cmd_line_parts.pop(new_cmd_line_parts.index(arg))
        log.debug(
            'Final processing for %r: opts: %r args: %r new_cmd: %r, main_opts_used: %r', 
            name,
            main_opts,
            main_args,
            new_cmd_line_parts,
            main_opts_used,
        )
        return main_args, main_opts, cmd_args, new_cmd_line_parts, main_opts_used
    else:
        return cmd_args, main_opts

help_option = dict(
    options = ['-h', '--help'],
    help = 'display this message'
)

class Cmd(object):

    #
    # Internal code
    #

    default_aliases = {}

    def __init__(self, name=None, aliases=None):
        self.name = name
        self.aliases = AttributeDict(self.default_aliases)
        if aliases:
            self.aliases.update(aliases)

    def on_initial_convert(self, service, option_spec, parsed_args, parsed_options):
        args = parsed_args
        processed = to_internal(option_spec, parsed_options)
        opts = processed.opts
        help_needed = opts.get('help') and True or False
        if not help_needed:
            if self.arg_spec:
                error = None
                if isinstance(self.arg_spec[-1][0], int):
                    min_args = len(self.arg_spec)-1+self.arg_spec[-1][0]
                    if len(args) < min_args:
                        # We might be able to get an error
                       # import pdb; pdb.set_trace()
                        if len(self.arg_spec[-1]) < 3:
                            error = 'Not enough arguments'
                        else:
                            error = self.arg_spec[-1][2]
                else:
                    if len(args) > len(self.arg_spec):
                        error = 'Unexpected argument %r'%args[len(self.arg_spec)-1]
                    elif len(args) < len(self.arg_spec):
                        if len(self.arg_spec[len(args)]) < 3:
                            error = 'Not enough arguments'
                        else:
                            error = self.arg_spec[len(args)][2]
                if error:
                    raise getopt.GetoptError(error)
            elif len(args) > 1:
                raise getopt.GetoptError(
                    'Unexpected arguments: %s'%(
                        ', '.join([str(arg) for arg in args])[:]
                    )
                )
            elif len(args):
                raise getopt.GetoptError('Unexpected argument %s'%(args[0]))
            self.on_config(service, args, opts, processed)
        return args, opts, help_needed

    def on_display_help(self, service, help):
        print help(service)

    #
    # Code the user should customize
    #

    arg_spec = []

    option_spec = {
        'help': help_option
    }

    help = {
        'summary': 'No help summary specified',
    }

    def on_run(self, service, args, opts):
        return 0

    def on_config(self, service, args, opts, processed):
        return 0

class LoggingCmd(Cmd):

    help = {
        'template': None,
        'summary': 'No help summary specified'
    }
    option_spec = {
        'help': dict(
            options = ['-h', '--help'],
            help = 'display this message'
        ),
        'verbose': dict(
            options = ['-v', '--verbose'],
            help = 'Print lots of information about what\'s going on',
        ),
        'quiet': dict(
            options = ['-q', '--quiet'],
            help = 'Only show really important messages',
        ),
        'logging': dict(
            options = ['-l', '--logging'],
            help = 'Specify a logging file',
            metavar='LOGGING_FILE',
        ),
    }

    def on_config(self, service, args, opts, processed):
        if opts.get('logging') and (opts.quiet or opts.verbose):
            raise getopt.GetoptError(
                'You cannot specify a LOGGING_FILE and also use the '
                '-q or -v options'
            )

    def on_run(self, service, args, opts):
        if opts.get('logging'):
            if not os.path.exists(opts.logging):
                raise getopt.GetoptError('No such file %r'%opts.logging)
            fileConfig(opts.logging)
        else:
            format="%(levelname)s: %(message)s"
            if opts.quiet:
                logging.basicConfig(level=logging.WARNING, format=format)
            elif opts.verbose:
                logging.basicConfig(level=logging.DEBUG, format=format)
            else:
                logging.basicConfig(level=logging.INFO, format=format)




def handle_command(commands, cmd_line_parts=None, program=None, service=None, cmd=None):
    # Prepare the cmd object to have the args and opts set
    if cmd is None:
        cmd = AttributeDict(args=None, opts=None, chain=[])
    else:
        cmd.chain.append(AttributeDict(args=cmd.args, opts=cmd.opts))
	cmd['args'] = None
        cmd['opts'] = None
    if program is None:
        program = sys.argv[0]
        if os.sep in sys.argv[0]:
            program = program.split(os.sep)[-1]
    if cmd_line_parts is None:
        cmd_line_parts = sys.argv[1:]
    for name, command in commands.items():
        check_command(name, command)
    if None not in commands:
        commands[None] = Cmd()
    sub_command = None
    try:
        # Run the main service
        main_args, main_opts, args, new_cmd_line_parts, main_opts_used = process_command(
            cmd_line_parts,
            None, 
            commands[None],
        )
        k, p, h = commands[None].on_initial_convert(
            service, 
            commands[None].option_spec, 
            main_args, 
            main_opts,
        )
        if h:
            help = assemble_help(commands, None, program)
            commands[None].on_display_help(service, help)
            return 0
        # Need to be smarter here, want to call the inner functions in the scope of the outer.
        cmd['args'] = k
        cmd['opts'] = p
        if hasattr(commands[None], 'run'):
            result = commands[None].run(service, cmd)
        else:
            # Backwards compatibility
            result = commands[None].on_run(service, k, p)
        if result:
            return result
        # Now try to run the sub-command
        if not args:
            raise getopt.GetoptError('No command specified')
        sub_command = args.pop(0)
        if not sub_command in commands:
            error = 'No such command `%s\''%sub_command
            sub_command = None
            raise getopt.GetoptError(error)
        if isinstance(commands[sub_command], dict):
            return handle_command(commands[sub_command], cmd_line_parts=args, program='%s %s'%(program, sub_command), service=service, cmd=cmd)
        sub_args, sub_opts = process_command(
            args,#new_cmd_line_parts, 
            sub_command, 
            commands[sub_command],
        )
        if not hasattr(commands[sub_command], 'on_initial_convert'):
            raise Exception('The command for %r has no %r attribute'%(sub_command, 'on_initial_convert'))
        k, p, h = commands[sub_command].on_initial_convert(
            service, 
            commands[sub_command].option_spec, 
            sub_args, 
            sub_opts,
        )
        if h:
            help = assemble_help(
                commands, 
                sub_command, 
                program, 
            )
            commands[None].on_display_help(service, help)
            return 0
        cmd.chain.append(AttributeDict(args=cmd.args, opts=cmd.opts))
	cmd['args'] = None
        cmd['opts'] = None
        cmd['args'] = k
        cmd['opts'] = p
        if hasattr(commands[sub_command], 'run'):
            result = commands[sub_command].run(service, cmd)
        else:
            # Backwards compatibility
            result = commands[sub_command].on_run(service, k, p)
    except getopt.GetoptError, err:
        print 'Error:', str(err)
        if sub_command:
            args = commands[None].arg_spec and ' %s'%(' '.join([arg[0] for arg in commands[None].arg_spec]))
            if args == []:
                args = ''
            print (
                "Try `%(program)s%(args)s %(sub_command)s --help' for more "
                "information."
            ) % {
                'program': program,
                'sub_command': sub_command,
                'args': args,
            }
            return 1
        else:
            print "Try `%(program)s --help' for more information." % {
                'program': program,
            }
            return 1
    return result or 0

