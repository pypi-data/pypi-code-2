#
# This file is part of python-cli. python-cli is free software that is
# made available under the MIT license. Consult the file "LICENSE" that
# is distributed together with this file for the exact licensing terms.
#
# python-cli is copyright (c) 2011 by the python-cli authors. See the
# file "AUTHORS" for a complete overview.

import sys

from StringIO import StringIO
from subprocess import Popen, PIPE

from cli.error import ParseError, CommandError
from cli.object import create
from cli.settings import Settings
from cli.parser import Parser
from cli.platform import Terminal
from cli.command import *


class ExecutionContext(object):
    """A CLI execution context."""

    STATUS_OK = 0
    STATUS_ERR_SYNTAX = 1
    STATUS_ERR_COMMAND = 2

    welcome = None
    goodbye = None

    def __init__(self, settings):
        self.settings = settings
        self.parser = create(Parser)
        self.terminal = create(Terminal)
        self.commands = []
        self.register_commands()
        self.status = None

    def register_commands(self):
        """Register the default commands. Override in a subclass to change the
        default list."""
        self.register_command(SetCommand)
        self.register_command(ShowCommand)
        self.register_command(HelpCommand)
        self.register_command(StatusCommand)
        self.register_command(CdCommand)
        self.register_command(ClearCommand)
        self.register_command(PwdCommand)
        self.register_command(ExitCommand)

    def register_command(self, command):
        """Register an additional command. `command' must implement the
        Command interface."""
        self.commands.append(command)

    def get_command(self, name):
        """Return the command class for `name' or None."""
        for cls in self.commands:
            if cls.name == name:
                return cls
            if name in cls.aliases:
                return cls

    def _interactive(self):
        """INTERNAL: return True if this is an interactive context."""
        return self.terminal.stdin.isatty() and self.terminal.stdout.isatty()

    def command_loop(self, finput):
        """Run a read/parse/execute loop until EOF."""
        if isinstance(finput, str):
            finput = file(finput, 'r')
        elif not hasattr(finput, 'read'):
            raise TypeError, 'finput: expecing file name or file object'
        stdout = self.terminal.stdout
        stderr = self.terminal.stderr
        interactive = self._interactive()
        if interactive and self.welcome:
            stdout.write('%s\n' % self.welcome)
        self._stop = False
        while not self._stop:
            try:
                parsed = self._parse_command(finput)
            except EOFError:
                # CTRL-D pressed
                stdout.write('\n')
                break
            except ParseError, e:
                self.status = self.STATUS_ERR_SYNTAX
                stderr.write('error: %s\n' % str(e))
                continue
            except KeyboardInterrupt:
                # CTRL-C pressed
                stdout.write('\n')
                continue
            if len(parsed) == 0:
                continue  # empty line or comment
            try:
                self._execute_command(parsed[0])
            except CommandError, e:
                self.status = e.status
                stderr.write('error: %s\n' % str(e))
                if e.command:
                    stderr.write('try \'help %s\' for help\n' % e.command)
            except KeyboardInterrupt:
                stdout.write('\n')
                continue
            except Exception, e:
                self.status = self.STATUS_ERR_COMMAND
                stderr.write('uncaught exception: %s\n' % str(e))
            else:
                self.status = self.STATUS_OK
        if interactive and self.goodbye:
            stdout.write('%s\n' % self.goodbye)

    def execute_command(self, command):
        """Execute one command only."""
        command += '\n'
        terminal = self.terminal
        stdout = self.terminal.stdout
        stderr = self.terminal.stderr
        try:
            parsed = self.parser.parse(command)
        except EOFError:
            stderr.write('error: incomplete command')
            return
        except ParseError, e:
            self.status = self.STATUS_ERR_SYNTAX
            stderr.write('error: %s\n' % str(e))
            return
        try:
            self._execute_command(parsed[0])
        except CommandError, e:
            self.status = e.status
            stderr.write('error: %s\n' % str(e))
            if e.command:
                stderr.write('try \'help %s\' for help\n' % e.command)
        except KeyboardInterrupt:
            self.status = self.STATUS_OK
            stdout.write('\n')
        except Exception, e:
            self.status = self.STATUS_ERR_COMMAND
            stderr.write('uncaught exception: %s\n' % str(e))
        else:
            self.status = self.STATUS_OK

    def exit_loop(self):
        """Exit the loop in command_loop()."""
        self._stop = True

    def _parse_command(self, finput):
        """INTERNAL: parse one command from `finput' and return its parsed
        representation."""
        prompt = self.settings['ps1']
        terminal = self.terminal
        interactive = self._interactive()
        command = ''
        while True:
            if interactive:
                terminal.stdout.write(prompt)
                terminal.stdout.flush()
            line = finput.readline()
            if not line:
                raise EOFError
            command += line
            try:
                parsed = self.parser.parse(command)
            except EOFError:
                prompt = self.settings['ps2']
                continue
            else:
                break
        return parsed

    def _execute_command(self, parsed):
        """INTERNAL: execute one command."""
        if parsed[0] == '!':
            self._execute_shell_command(parsed[1])
            return
        name, args, opts, redirections, pipeline = parsed
        command = self._create_command(name, args, opts)
        self._setup_pipeline(pipeline)
        self._setup_io_streams(redirections)
        command.execute(self)
        self._restore_io_streams()
        self._execute_pipeline()

    def _execute_shell_command(self, command):
        """INTERNAL: execute a shell command."""
        shell = Popen(command, shell=True)
        retcode = shell.wait()
        if retcode != 0:
            m = 'shell command exited with error'
            raise CommandError(m, status=retcode)

    def _create_command(self, name, args, opts):
        """INTERNAL: instantiate a new command."""
        cls = self.get_command(name)
        if cls is None:
            raise CommandError, 'unknown command: %s' % name
        return cls(args, opts)

    def _setup_pipeline(self, pipeline):
        """INTERNAL: set up the pipeline, if any."""
        if not pipeline:
            self._pipeline = None
            return
        self._pipeline = Popen(pipeline, stdin=PIPE, stderr=PIPE, shell=True)
        self._pipeinput = StringIO()
        self.terminal.stdout = self._pipeinput

    def _setup_io_streams(self, redirections=[]):
        """INTERNAL: set up standard input/output/error."""
        for type, arg in redirections:
            if type == '<':
                self.terminal.stdin = file(arg)
            elif type == '<<':
                self.terminal.stdin = StringIO(arg)
            elif type == '>':
                self.terminal.stdout = file(arg, 'w')
            elif type == '>>':
                self.terminal.stdout = file(arg, 'a')

    def _restore_io_streams(self):
        """INTERNAL: reset IO streams."""
        self.terminal.stdin = sys.stdin
        self.terminal.stdout = sys.stdout
        self.terminal.stderr = sys.stderr

    def _execute_pipeline(self):
        """INTERNAL: execute the command pipleine (if any)."""
        if not self._pipeline:
            return
        pipeinput = self._pipeinput.getvalue()
        dummy, stderr = self._pipeline.communicate(pipeinput)
        retcode = self._pipeline.returncode
        if retcode != 0:
            raise CommandError, stderr.rstrip()
            
