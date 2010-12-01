import sys
import argparse

__all__ = ("CommandError", "ProgramError",
           "Command", "CommandTable",
           "argparse",
           )

class CommandError(Exception):
    pass

# Used to display end-user errors
class ProgramError(Exception):
    pass

class Command(object):
    """Contains definition of command-line command.
    It contains information on how to map argparse arguments to parameters of a callable.

    Once an ArgumentParser object is created the `setup` method should be called
    with the parser as parameter.

    attributes:
    name: The name of the command, used directly in CLI
    doc:  The documentation of the command, displayed among CLI help
    callee: The callable object that will be called when the command is used
    argnames: A list of tuples containing argname and parameter name, the argname is used in ArgumentParser objects.
    names: A list of all names which can be passed to callee.
    args: A list of dicts containing all the ArgumentParser info, data is passed to ArgumentParser.add_argument.
    arg_param: The name of the parameter that should receive the populated namespace, or None if it should not be sent.
    """
    name = None
    doc = ""
    callee = None

    def __init__(self, name, doc, callee, args=None):
        self.name = name
        self.doc = doc
        self.callee = callee
        if args == None:
            args = []
        self._args = args
        self.mutex = []
        self.parent = None

    def setPositionalArgs(self, posargs):
        args = Command.args(posargs)
        self._args.extend(args)

    def setOptions(self, opts):
        args = Command.options(opts)
        self._args.extend(args)

    def setMutexOptions(self, mutex):
        self.mutex.extend(mutex)

    @staticmethod
    def options(opts):
        args = []
        for opt in opts:
            short, name, default, doc = opt[0:4]
            action = None
            if len(opt) > 4:
                action = opt[4]
            names = []
            if short:
                names.append("-" + short)
            metavar = None
            if isinstance(name, (list, tuple)):
                if len(name) >= 3:
                    longname, name, metavar = name[0:3]
                else:
                    longname, name = name[0:2]
            else:
                longname = name
            names.append("--" + longname.replace("_", "-"))
            arg = {"names": names,
                   "dest":  name}
            if metavar or longname != name:
                arg["metavar"] = metavar or longname.upper()
            if doc:
                arg["help"] = doc
            kind = type(default)
            arg["kind"] = kind
            if kind in (tuple, list):
                arg["nargs"] = "*"
                arg["type"] = str
                if default != None:
                    arg["default"] = default
            else:
                if default != None:
                    arg["default"] = default
                    if kind != bool:
                        arg["type"] = kind
                if default == False:
                    arg["action"] = "store_true"
                elif default == True:
                    arg["action"] = "store_false"
            if action:
                arg["action"] = action
            args.append(arg)
        return args

    @staticmethod
    def args(posargs):
        args = []
        for posarg in posargs:
            singular, default, doc = posarg[0:4]
            if isinstance(singular, (list, tuple)):
                singular, plural = singular
            else:
                plural = singular
            action = None
            if len(posarg) > 4:
                action = posarg[4]
            arg = {"names": [plural],
                   "metavar": singular.lower()}
            if doc:
                arg["help"] = doc
            kind = type(default)
            arg["kind"] = kind
            if kind in (tuple, list):
                arg["nargs"] = "*"
                arg["type"] = str
                if default != None:
                    arg["default"] = default
            else:
                if default != None:
                    arg["default"] = default
                    arg["type"] = kind
                else:
                    arg["type"] = str
            if action:
                arg["action"] = action
            args.append(arg)
        return args

    def call(self, opts):
        values = self.extractArguments(opts)
        return self.callee(**values)

    def extractArguments(self, opts):
        values = {}
        if self.parent:
            values = self.parent.extractArguments(opts)
        for arg in self._args:
            dest = arg.get("dest", arg["names"][0])
            if hasattr(opts, dest):
                values[dest] = getattr(opts, dest)
        values["__opts"] = opts
        values["ui"] = opts.ui
        return values

    def setup(self, parser):
        mutex_args = {}
        for mutex_group in self.mutex:
            for argname in mutex_group:
                mutex_args[argname] = None
        for arg in self._args:
            arg = arg.copy()
            argname = arg.get("dest", arg["names"][0])
            if argname in mutex_args:
                mutex_args[argname] = arg
                continue
            names = arg["names"]
            del arg["names"]
            del arg["kind"]
            parser.add_argument(*names, **arg)
        for mutex_group in self.mutex:
            group = parser.add_mutually_exclusive_group()
            for argname in mutex_group:
                arg = mutex_args[argname]
                if arg == None:
                    raise CommandError("No option named %s" % argname)
                names = arg["names"]
                del arg["names"]
                del arg["kind"]
                group.add_argument(*names, **arg)

    def loadconfig(self, config, opts, group=None):
        group = group or "command." + self.name
        for arg in self._args:
            argname = arg.get("dest", arg["names"][0])
            names = arg["names"]
            for name in names:
                if name[0:2] == "--":
                    name = name[2:]
                elif name[0] == "-":
                    name = name[1:]
                if (group, name) in config:
                    if arg["kind"] == bool:
                        value = config.bool(group, name)
                    elif arg["kind"] in (list, tuple):
                        value = [item.strip() for item in config[(group, name)].split(",")]
                    else:
                        value = config[(group, name)].strip()
                    setattr(opts, argname, value)

    def __repr__(self):
        return "Command(%r,%r,%r,%r)" % (self.name, self.doc, self.callee, self._args)

class CommandTable(dict):
    """Contains a set of Command objects

    To add a new command the `add` method can be used as a decorator,
    for instance:
    >>> cmds = CommandTable()
    >>> @cmds.add()
    ... def cat(ui, **kwargs):
    ...     print "hi"

    Accessing the commands is done by the name of the command.
    Checking if a command exists can be done with the `in` operator.
    >>> "cat" in cmds
    True

    Accessing the command object is done with the subscript operator.
    >>> cmds["cat"].name
    'cat'

    To set global options use the `options` method as a decorator on
    a function. The function will be called like a normal command but
    is always called before the real command and can be used to initialize
    values based on the global options.
    >>> @cmds.options([('c', 'config', None, 'Set config file')])
    ... def options(ui, config, **kwargs):
    ...     print 'config file %s' % config
    """

    def __init__(self):
        self.profile_filename = None
        self._command = None

    def __iter__(self):
        """Iterates over all the command objects"""
        return self.itervalues()

    @staticmethod
    def parseFunction(func):
        """Extracts information from a function and creates a Command object for it.

        The name of function is used as the command name but underscores are replaced
        with dashes. The documentation of the function is used as the command help.

        >>> def copy_file(ui, **kwargs):
        ...     print "hi"
        >>> cmd = CommandTable.parseFunction(copy_file)
        >>> cmd.name
        'copy-file'
        """
        name = func.func_name.replace("_", "-")
        doc = func.func_doc
        return Command(name, doc, func)

    def process(self, ui, opts, *args, **kwargs):
        """Processes the arguments and calls the corresponding command object.

        ui: The Ui object which is passed to the command.
        opts: Contains all options and positional arguments, returned from ArgumentParser.

        Note: Global options are processed before the actual command is called.
        """
        opts.ui = ui
        if self._command:
            if self._command.callee:
                ret = self._command.call(opts, *args, **kwargs)
                if ret >= 1:
                    return ret
        if not hasattr(opts, "command"):
            raise CommandError("No command was specified")
        command = self[opts.command]

        if self.profile_filename:
            from cProfile import Profile
            p = Profile()

            def profiler_wrap():
                return command.call(opts, *args, **kwargs)
            try:
                ret = p.runcall(profiler_wrap)
            finally:
                p.dump_stats(self.profile_filename)
            return ret
        else:
            return command.call(opts, *args, **kwargs)

    def extractArguments(self, *args, **kwargs):
        """Extracts the options into a dictionary.

        See Command.extractArguments for more details.
        """
        if not self._command:
            return {}
        return self._command.extractArguments(*args, **kwargs)

    def setup(self, parser, *args, **kwargs):
        """Setup the parser by registering global options and registering sub-commands.
        """
        if self._command:
            self._command.setup(parser, *args, **kwargs)
        command_parser = parser.add_subparsers(dest="command")
        for command in self:
            sub_parser = command_parser.add_parser(command.name, help=command.doc)
            command.setup(sub_parser)

    def loadconfig(self, config, opts):
        """Load option values for each command from a config file.
        """
        if self._command:
            self._command.loadconfig(config, opts, group="global")
        for command in self:
            command.loadconfig(config, opts)

    def options(self, opts=None, **kwargs):
        """Decorator which registers global options.

        This returns a wrapper function, call this one with the actual function to handle options.
        >>> cmds = CommandTable()
        >>> @cmds.options()
        ... def global_options(ui, **kwargs):
        ...    print "handling options"

        See Command.setOptions for more details.
        """
        if opts == None:
            opts = []

        def process(func):
            cmd = self._command
            if not cmd:
                cmd = self.parseFunction(func)
            if not hasattr(func, "cmd"):
                func.cmd = cmd
            elif not self._command:
                raise CommandError("Command %s has already been registered with a different function" % cmd.name)
            if not self._command:
                self._command = cmd
            cmd.setOptions(opts)
            return func

        return process

    def add(self, opts=None, posargs=None, mutex=None):
        """Decorator which registers a new command.

        This returns a wrapper function, call this one with the actual function.
        >>> cmds = CommandTable()
        >>> @cmds.add()
        ... def move(ui, **kwargs):
        ...    print "move"

        `opts` are passed to Command.setOptions, `posargs` to Command.setPositionalArgs
        and `mutex` to Command.setMutexOptions.
        """
        if opts == None:
            opts = []

        def process(func):
            if not hasattr(func, "cmd"):
                cmd = self.parseFunction(func)
                cmd.parent = self
                if cmd.name in self:
                    raise CommandError("Command %s has already been registered with a different function" % cmd.name)
                self[cmd.name] = cmd
                func.cmd = cmd
            else:
                cmd = func.cmd
            if cmd.name not in self:
                self[cmd.name] = cmd

            func.cmd.setOptions(opts)
            if mutex:
                func.cmd.setMutexOptions(mutex)
            if posargs:
                func.cmd.setPositionalArgs(posargs)
            return func

        return process

    def update(self, cmds):
        for cmd in cmds:
            cmd.parent = self
            self[cmd.name] = cmd
