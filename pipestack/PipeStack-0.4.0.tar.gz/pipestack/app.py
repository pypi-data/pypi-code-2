"""\
Contains the ``App`` class for creating an application using a stack of pipes.
"""

import getopt
import os
import logging 
import types  # The types line can eventually be removed
import warnings

from bn import AttributeDict
from commandtool import handle_command, Cmd, LoggingCmd
from configconvert.service import parse_and_split_options_change_dir
from configconvert.internal import eval_import

log = logging.getLogger(__name__)

class PipeError(Exception):
    pass

def pipe(name, object, aliases=None, **p):
    return (name, (object, aliases, p))

def command(name, object, aliases=None, **p):
    return (name, (object, aliases, p))

def make_default_pipeline(pipes, exclude):
    for item in exclude:
        found = False
        for pipe in pipes:
            if item == pipe[0]:
                found = True
                break
        if not found:
            raise Exception('Pipe %r specified in `exclude\' does not exist'%item)
    pipeline = [pipe[0] for pipe in pipes]
    for item in exclude:
        if item in pipeline:
            pipeline.pop(pipeline.index(item))
    return pipeline

class AppCmd(LoggingCmd):
    help = dict(summary='Run a PipeStack command')
    option_spec = LoggingCmd.option_spec.copy()
    option_spec.update({'config': dict(
            options = ['-d', '--config'],
            help = 'The config file',
            metavar='CONFIG_FILE',
        ),
    })

    def on_run(self, app, args, opts):
        LoggingCmd.on_run(self, app, args, opts)    
        if opts.get('config'):
            app.parse_config(opts.config)

reserved =  ['command', 'enter', 'app', 'interrupt_flow']

class App(object):
    pipes = []
    commands = []
    exclude = []
    api_version = (0,8,0)

    def __init__(self, option=None):
        self.pipes_by_name = {}
        for name, data in self.pipes:
            if name in reserved:
                raise PipeError('The name %r is reserved and cannot be used as a pipe name'%name)
            if name not in self.pipes_by_name:
                self.pipes_by_name[name] = data
            else:
                raise Exception(
                    "You cannot have two pipes named %s"%(name,)
                )
        names = []
        for name, data in self.commands:
            if name not in names:
                names.append(name)
            else:
                raise Exception(
                    "You cannot have two commands named %r"%(name,)
                )
        self.instantiated_pipes = {}
        self.config = AttributeDict()
        self.option = option
        self.check_loggers = True

    def _get_default_pipeline(self):
        return make_default_pipeline(self.pipes, getattr(self, 'exclude', ()))
    default_pipeline = property(_get_default_pipeline)

    def parse_config(self, filename):
        if self.option is None:
            self.option = {}
        self.option.update(
            parse_and_split_options_change_dir(self, filename)
        )

    def handle_command_line(self, cmd_line_parts=None):
        if not self.commands:
            raise Exception('No commands specified in the app')
        else:
            commands = {}
            for command in self.commands:
                arguments = command[1][2]
                if command[1][1]:
                    arguments['aliases'] = command[1][1]
                if isinstance(command[1][0], (str, unicode)):
                    command_class = eval_import(command[1][0])
                else:
                    command_class = command[1][0]
                commands[command[0]] = command_class(**arguments)
            commands[None] = AppCmd()
            handle_command(
                commands, 
                service=self, 
                cmd_line_parts=cmd_line_parts,
            )

    def start_flow(self, bag=None, ensure=[], run=None, enter_pipes=None):
        # enter_pipes is deprecated
        if enter_pipes:
            ensure = enter_pipes
        for name in ensure:
            if ensure.count(name)>1:
                raise Exception('The pipe %r is specified more than once'%name)
        if bag is None:
            bag = AttributeDict()
        else:
            for name in reserved:
                if bag.has_key(name):
                    raise Exception('Bags are not allowed to have a key named %r'%name)
            for name in reserved:
                if hasattr(bag, name):
                    raise Exception('Bags are not allowed to have an attribute named %r'%name)
        bag['app'] = self 

        _application_handled = []
        _error_handled = []
        pipes_to_leave = []
  
        def enter(name):
            if not isinstance(name, (unicode, str)):
                raise Exception(name)
            if name in pipes_to_leave:
                raise PipeError(
                    'The bag has already entered the %r pipe'%(name,)
                )
            if not self.pipes_by_name.has_key(name):
                raise PipeError('No such pipe %r'%(name,))
            if self.check_loggers and name not in logging.Logger.manager.loggerDict.keys():
                warnings.warn(
                    'The %r pipe does not have a logger set up'%(name,)
                )
            # Re-use an existing instance if one exists:
            if name in self.instantiated_pipes:
                pipe_instance = self.instantiated_pipes[name]
            else:
                log.debug("Instantiating pipe %r", name)
                pipe = self.pipes_by_name[name]
                #if isinstance(pipe[0], types.FunctionType):
                #    bag['name'] = name
                #    pipe_instance = pipe[0](bag)
                #    del bag['name']
                #elif isinstance(pipe[0], (unicode, str)):
                if isinstance(pipe[0], (unicode, str)):
                    pipe_instance = eval_import(pipe[0])(bag, name, aliases=pipe[1], **pipe[2])
                else:
                    pipe_instance = pipe[0](bag, name, aliases=pipe[1], **pipe[2])
                self.instantiated_pipes[name] = pipe_instance
            log.debug("Entering pipe %r", name)
            pipe_instance.enter(bag)
            pipes_to_leave.insert(0, name)
            log.debug('Added the %r pipe to the existing pipes to leave: %r', name, pipes_to_leave)

        def leave(name, error=False):
            log.debug("Stopping %r with error set to %r", name, error)
            instance = self.instantiated_pipes[name]
            if hasattr(instance, 'leave'): 
                instance.leave(bag, error)
                stopped = pipes_to_leave.pop(pipes_to_leave.index(name))
                log.debug('Stopped %r', stopped)
    
        def interrupt_flow(**p):
            if p.has_key('error_handled'):
                _error_handled.append(p['error_handled'])
            elif p.has_key('application_handled'):
                _application_handled.append(p['application_handled'])
            else:
                raise Exception('Unknown interrupt %r'%p.keys())

        # Add our new helpers to the service dictionary
        bag['enter'] = enter
        def raise_deprecated(*k, **p):
            raise Exception('Start and stop are deprecated')
        bag['start'] = bag['stop'] = raise_deprecated
        #bag['leave'] = leave
        bag['interrupt_flow'] = interrupt_flow

        # Run the initial services
        for name in ensure:
            if _application_handled:
                break
            if _error_handled:
                raise PipeError('No error occurred, but _error_handled is True')
            try:
                enter(name)
            except:
                for name in pipes_to_leave[:]:
                    # Check that one of the other services hasn't stopped them
                    leave(name, error=True)
                if not _error_handled:
                    raise
                else:
                    log.error('Error occurred but was handled')
                    return
        if run:
            log.debug('Running the run() function %r', run)
            run(bag)
        log.debug('Need to leave these pipes: %r', pipes_to_leave)
        # We need a copy of the pipes to leave because this object gets changed as each pipe is left.
        for name in pipes_to_leave[:]:
            # Check that one of the other services hasn't stopped them
            log.debug('Leaving pipe %r', name)
            leave(name, error=False)

