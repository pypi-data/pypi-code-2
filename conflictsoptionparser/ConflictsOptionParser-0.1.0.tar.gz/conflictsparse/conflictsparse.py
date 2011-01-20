#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright (c) 2011 Christopher D. Lasher
#
# This software is released under the MIT License. Please see
# LICENSE.txt for details.


"""A command line interface that recognizes conflicting options given as
arguments.

"""

__all__ = ['ConflictingParsedOptionsError', 'ConflictsOptionParser']

import optparse


class ConflictingParsedOptionsError(optparse.OptParseError):
    """Raised when the arguments contain options denoted as
    conflicting.

    """
    def __init__(self, conflicting_options, msg=None):
        """Create a new instance.

        :Parameters:
        - `conflicting_options`: an iterable of `Option` instances

        """
        self.conflicting_options = conflicting_options
        self.msg = msg


    def _make_default_conflict_message(self, conflicting_options):
        opt_strings = ", ".join(opt.get_opt_string() for opt in
                self.conflicting_options)
        message = opt_strings + " are incompatible options."
        return message


    def __str__(self):
        if self.msg is None:
            self.msg = self._make_default_conflict_message(
                    self.conflicting_options)
        return self.msg


class ConflictsOptionParser(optparse.OptionParser, object):
    def __init__(self, *args, **kwds):
        super(ConflictsOptionParser, self).__init__(*args, **kwds)
        # _option_conflicts contains `frozenset`s of conflicting options
        # as keys, and error messages as values.
        self._option_conflicts = {}


    # The next two methods are almost verbatim from
    # `optparse.OptionParser`, however we must make a slight change to
    # register the options seen, denoted in the comments.

    def _process_long_opt(self, rargs, values):
        arg = rargs.pop(0)

        # Value explicitly attached to arg?  Pretend it's the next
        # argument.
        if "=" in arg:
            (opt, next_arg) = arg.split("=", 1)
            rargs.insert(0, next_arg)
            had_explicit_value = True
        else:
            opt = arg
            had_explicit_value = False

        opt = self._match_long_opt(opt)
        option = self._long_opt[opt]
        if option.takes_value():
            nargs = option.nargs
            if len(rargs) < nargs:
                if nargs == 1:
                    self.error(_("%s option requires an argument") % opt)
                else:
                    self.error(_("%s option requires %d arguments")
                               % (opt, nargs))
            elif nargs == 1:
                value = rargs.pop(0)
            else:
                value = tuple(rargs[0:nargs])
                del rargs[0:nargs]

        elif had_explicit_value:
            self.error(_("%s option does not take a value") % opt)

        else:
            value = None

        # Addition is here, where we denote the option as having been
        # "seen" in the arguments.
        self._seen_options.add(option)

        option.process(opt, value, values, self)


    def _process_short_opts(self, rargs, values):
        arg = rargs.pop(0)
        stop = False
        i = 1
        for ch in arg[1:]:
            opt = "-" + ch
            option = self._short_opt.get(opt)
            i += 1                      # we have consumed a character

            if not option:
                raise BadOptionError(opt)
            if option.takes_value():
                # Any characters left in arg?  Pretend they're the
                # next arg, and stop consuming characters of arg.
                if i < len(arg):
                    rargs.insert(0, arg[i:])
                    stop = True

                nargs = option.nargs
                if len(rargs) < nargs:
                    if nargs == 1:
                        self.error(_("%s option requires an argument") % opt)
                    else:
                        self.error(_("%s option requires %d arguments")
                                   % (opt, nargs))
                elif nargs == 1:
                    value = rargs.pop(0)
                else:
                    value = tuple(rargs[0:nargs])
                    del rargs[0:nargs]

            else:                       # option doesn't take a value
                value = None

            # Addition is here, where we denote the option as having been
            # "seen" in the arguments.
            self._seen_options.add(option)

            option.process(opt, value, values, self)

            if stop:
                break


    def opts_to_option_instances(self, options):
        """Ensures that options are converted into appropriate
        `optparse.Option` instances.

        :Parameters:
        - `options`: an iterable of `Option` instances or option strings

        """
        opts = []
        for option in options:
            if isinstance(option, (str, unicode)):
                opt = self.get_option(option)
                if opt is None:
                    raise ValueError("unrecognized option: %s" % option)
            else:
                opt = option
            opts.append(opt)
        return opts


    def register_conflict(self, options, message=None):
        """Sets a collection of options as conflicting.

        :Parameters:
        - `options`: an iterable of `Option` instances or option strings
        - `message`: a string message for the error

        """
        opts = frozenset(self.opts_to_option_instances(options))
        self._option_conflicts[opts] = message


    def unregister_conflict(self, options):
        """Removes a collection of options from those noted as
        conflicting.

        NOTE: ``options`` must match the complete combination of
        conflicting options registered; partial or non-registered
        combinations will raise a `KeyError`.

        :Parameters:
        - `options`: an iterable of `Option` instances
        - `message`: a string message for the error

        """
        opts = frozenset(self.opts_to_option_instances(options))
        del self._option_conflicts[opts]


    def _check_parsed_options_conflicts(self):
        """Checks the options parsed from the arguments for
        conflicts.

        """
        for conflicting_options, message in self._option_conflicts.items():
            obs_conflicting_options = conflicting_options.intersection(
                    self._seen_options)
            if len(obs_conflicting_options) > 1:
                raise ConflictingParsedOptionsError(conflicting_options,
                        message)


    def parse_args(self, *args, **kwds):
        self._seen_options = set()
        options, args = super(ConflictsOptionParser,
                self).parse_args(*args, **kwds)
        try:
            self._check_parsed_options_conflicts()
        except ConflictingParsedOptionsError, err:
            self.error(str(err))
        return options, args

