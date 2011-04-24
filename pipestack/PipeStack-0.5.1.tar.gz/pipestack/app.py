"""\
Contains the ``App`` class for creating an application using a stack of pipes.
"""

import getopt
import os
import logging 
import sys
import types  # The types line can eventually be removed
import warnings

from bn import AttributeDict, uniform_path, OrderedDict
from commandtool import handle_command, Cmd, LoggingCmd
from configconvert import parse_and_split_options_change_dir, parse_config_string, split_options
from configconvert.internal import eval_import
from nestedrecord import encode
from pipestack import __version__
from pipestack.pipe import Pipe, Marble

log = logging.getLogger(__name__)

#
# Constants
#

reserved = ['command'] + ['enter', 'app', 'interrupt_flow'] + ['aliases', 'default_aliases', 'name']

#
# Exceptions
#

class PipeError(Exception):
    pass

class DuplicatePipeNameError(PipeError):
    pass

class DuplicateCommandNameError(PipeError):
    pass

class ReservedPipeNameError(PipeError):
    pass

class ReservedCommandNameError(PipeError):
    pass


#
# Pipe and command factories
#

def pipe(name, class_, aliases=None, **p):
    return AttributeDict(name=name, class_=class_, aliases=aliases, extras=p)

def command(name, class_, aliases=None, **p):
    return AttributeDict(name=name, class_=class_, aliases=aliases, extras=p)

#
# Commands
#

class AppCmd(Cmd):
    help = dict(summary='Run a PipeStack command')
    option_spec = LoggingCmd.option_spec.copy()
    option_spec.update({'config': dict(
            options = ['-d', '--config'],
            help = 'The config file',
            metavar='CONFIG_FILE',
        ),
        'verbose': dict(
            options = ['-v', '--verbose'],
            help = 'show all log messages',
        ),
        'quiet': dict(
            options = ['-q', '--quiet'],
            help = 'only show error and warning messages',
        ),
    })

    def run(self, cmd):
        return 0
        self.bag.app.parse_config(cmd.args, cmd.opts)
        self.bag.app.parse_logging(cmd.args, cmd.opts)

#
# Core classes
#

class Bag(AttributeDict):
    pass

class App(object):
    pipes = []
    commands = []
    exclude = []
    api_version = (0,8,0)

    def __init__(self, option=None):
        self._pipes_by_name = {}
        self._plugins = {}
        self._commands_structure = OrderedDict()
        self._instantiated_pipes = {}
        self.config = AttributeDict()
        self.config_file = None
        if isinstance(option, (str, unicode)):
            self.option = split_options(parse_config_string(option))
        else:
            self.option = option
        self.plugins = {}

        pipes = self.pipes[:]
        self.pipes = []
        for pipe in pipes:
            self.pipe(pipe)
        commands = self.commands[:]
        self.commands = []
        for command in commands:
            self.command(command)
        
    def pipe(self, pipe):
        if pipe.name in reserved:
            raise ReservedPipeNameError(
                'The name %r is reserved and cannot be used as a pipe '
                'name'%(
                    pipe.name
                )
            )
        if pipe.name not in self._pipes_by_name:
            self._pipes_by_name[pipe.name] = pipe
        else:
            raise DuplicatePipeNameError(
                "You cannot have two pipes named %s"%(pipe.name,)
            )
        log.debug('Adding pipe %r', pipe)
        self.pipes.append(pipe)
    
    def command(self, command):
        if command.name in []:
            raise ReservedCommandNameError(
                'The command name %r is reserved'%(command.name,)
            )
        if command.name in self._commands_structure:
            raise DuplicateCommandNameError(
                "You cannot have two commands named %r"%(command.name,)
            )
        if isinstance(command.class_, (str, unicode)):
            command['class_'] = eval_import(command.class_)
        elif isinstance(command.class_, (tuple, list)):
            command['class_'] = OrderedDict(command.class_)
        self._commands_structure[command.name] = command
 
    def _get_default_pipeline(self):
        exclude = getattr(self, 'exclude', ())
        for item in exclude:
            if not self._pipes_by_name.has_key(item):
                raise PipeError('Pipe %r specified in `exclude\' does not exist'%(item,))
        pipeline = [pipe.name for pipe in self.pipes]
        for item in exclude:
            if item in pipeline:
                pipeline.pop(pipeline.index(item))
        return pipeline
    default_pipeline = property(_get_default_pipeline)

    def handle_command_line(self, cmd_line_parts=None, program=None, exit=sys.exit, service=None):
        if not self._commands_structure:
            raise Exception('No commands specified in the app')
        else:
            result = []
            def run(bag):
                def initialise_branch(bag, command_tree, command_structure):
                    # Iterate through the entire structure to initialise each one
                    for name, command in command_structure.items():
                        if hasattr(command, 'class_'):
                            if isinstance(command.class_, dict):
                                command_tree[name] = OrderedDict()
                                initialise_branch(bag, command_tree[name], command.class_)
                            else:
                                command_tree[name] = command.class_(bag=bag, name=name, aliases=command.aliases)
                        else:
                            if hasattr(command, 'class_'):
                                command_tree[name] = OrderedDict()
                                initialise_branch(bag, command_tree[name], command)
                            elif isinstance(command, Cmd):
                                # Already initialised
                                command_tree[name] = command
                            else:# isinstance(command, Cmd):
                                command_tree[name] = command(bag=bag, name=name)
                            #else:
                            #    raise Exception('Unknown command type %r'%command)
                command_tree = OrderedDict([(None, AppCmd(bag))])
                initialise_branch(bag, command_tree, self._commands_structure)
                result.append(handle_command(
                    command_tree,
                    program=program,
                    service=service,
                    cmd_line_parts=cmd_line_parts,
                ))
            self.start_flow(bag=None, ensure=[], run=run)
            exit(result[0])

    def start_flow(self, bag=None, ensure=[], run=None):
        for name in ensure:
            if ensure.count(name)>1:
                raise DuplicatePipeNameError('The pipe %r is specified more than once in the ensure argument'%name)
        if bag is None:
            bag = Bag()
        else:
            for name in reserved:
                if bag.has_key(name):
                    raise ReservedPipeNameError('Bags are not allowed to have a key named %r'%name)
            for name in reserved:
                if hasattr(bag, name):
                    raise ReservedPipeNameError('Bags are not allowed to have an attribute named %r'%name)
        bag['app'] = self 

        _application_handled = []
        _error_handled = []
        _error_occurred = []
        pipes_to_leave = []

        def enter(name):
            if not isinstance(name, (unicode, str)):
                raise Exception(name)
            if name in pipes_to_leave:
                raise PipeError(
                    'The bag has already entered the %r pipe'%(name,)
                )
            if not self._pipes_by_name.has_key(name):
                raise PipeError('No such pipe %r'%(name,))
            if name not in logging.Logger.manager.loggerDict.keys():
                warnings.warn(
                    'The %r pipe does not have a logger set up'%(name,)
                )
            # Re-use an existing instance if one exists:
            if name in self._instantiated_pipes:
                pipe_instance = self._instantiated_pipes[name]
            else:
                log.debug("Instantiating pipe %r", name)
                pipe = self._pipes_by_name[name]
                if pipe.extras:
                    raise Exception("Pipe extras are deprectated (pipe %s)"%name)
                if isinstance(pipe.class_, (unicode, str)):
                    pipe_instance = eval_import(pipe.class_)(bag, name, aliases=pipe.aliases, **pipe.extras)
                else:
                    pipe_instance = pipe.class_(bag, name, aliases=pipe.aliases, **pipe.extras)
                self._instantiated_pipes[name] = pipe_instance
            log.debug("Entering pipe %r", name)
            pipe_instance.enter(bag)
            pipes_to_leave.insert(0, name)
            log.debug('Added the %r pipe to the existing pipes to leave: %r', name, pipes_to_leave)

        def leave(name, error=False):
            log.debug("Stopping %r with error set to %r", name, error)
            instance = self._instantiated_pipes[name]
            if hasattr(instance, 'leave'): 
                instance.leave(bag, error)
                stopped = pipes_to_leave.pop(pipes_to_leave.index(name))
                log.debug('Stopped %r', stopped)
    
        def interrupt_flow(error_handled=False, **p):
            if p:
                warnings.warn(
                    'The use of %r is deprecated, use error=True or error=False'%(p.keys()[0],)
                )
                if p.has_key('error_handled'):
                    if not _error_occurred:
                        raise Exception('Error said to be handled, but no error occurred')
                    _error_handled.append(p['error_handled'])
                elif p.has_key('application_handled'):
                    _application_handled.append(p['application_handled'])
                else:
                    raise Exception('Unknown interrupt %r'%p.keys())
            else:
                if error_handled:
                    if not _error_occurred:
                        raise Exception('Error said to be handled, but no error occurred')
                    _error_handled.append(True)
                else:
                    _application_handled.append(True)

        # Add our new helpers to the service dictionary
        bag['enter'] = enter
        bag['interrupt_flow'] = interrupt_flow

        # Run the initial services
        for name in ensure:
            if _application_handled:
                break
            # Not possible to interrupt a flow to trigger this condition now
            #if _error_handled:
            #    raise PipeError('No error occurred, but _error_handled is True')
            if not bag.has_key(name):
                try:
                    enter(name)
                except:
                    _error_occurred.append(True)
                    for name in pipes_to_leave[:]:
                        # Check that one of the other services hasn't stopped them
                        leave(name, error=True)
                    if not _error_handled:
                        raise
                    else:
                        log.error('Error occurred but was handled')
                        return
        if run and not _application_handled and not _error_occurred:
            log.debug('Running the run() function %r', run)
            # You can't interrupt the flow at the end of the pipeline, but it doesn't do any harm either.
            # del bag.interrupt_flow
            try:
                run(bag)
            except:
                _error_occurred.append(True)
                for name in pipes_to_leave[:]:
                    # Check that one of the other services hasn't stopped them
                    leave(name, error=True)
                if not _error_handled:
                    raise
                else:
                    log.error('Error occurred but was handled')
                    return
        log.debug('Need to leave these pipes: %r', pipes_to_leave)
        # We need a copy of the pipes to leave because this object gets changed as each pipe is left.
        for name in pipes_to_leave[:]:
            # Check that one of the other services hasn't stopped them
            log.debug('Leaving pipe %r', name)
            leave(name, error=False)

    def parse_config(self, args, opts):
        self.config_file = opts.get('config')
        if self.option is None:
            self.option = {}
        if self.config_file:
            self.option.update(
                parse_and_split_options_change_dir(None, opts.get('config'))
            )
        if self.option.has_key('app'):
            plugins = self.option['app'].get('plugin', '')
            self._plugins = import_plugin(plugins)

    def parse_logging(self, args, opts):
        format="%(levelname)s: %(message)s"
        if opts.quiet:
            level = logging.WARNING
        elif opts.verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(level=level, format=format)

    def get_plugins(self, interface_path):
        return self._plugins.get(interface_path, [])

    def fetch_plugins(self, pipe, plugin):
        interface_path = '%s:%s'%(pipe, plugin)
        if not self.plugins.has_key(interface_path):
            to_fire = self.get_plugins(interface_path)
            modules = []
            for plugin in to_fire:
                modules.append(eval_import(plugin))
            self.plugins[interface_path] = modules
        return self.plugins[interface_path]

def import_plugin(string):
    plugins = {}
    counter = 0
    for line in string.split('\n'):
        counter += 1 
        line = line.strip()
        if line:
            parts = line.split(' ')
            if not len(parts) == 2:
                raise Exception('Expected exaclty one space on line %s of the plugins specification'%counter)
            if not parts[0].count(':') == 1:
                raise Exception("Expected exaclty one ':' in the interface path on line %s of the plugins specification"%counter)
            if not parts[1].count(':') == 1:
                raise Exception("Expected exaclty one ':' in the implementation path on line %s of the plugins specification"%counter)
            if plugins.has_key(parts[0]):
                plugins[parts[0]].append(parts[1])
            else:
                plugins[parts[0]] = [parts[1]]
    return plugins

