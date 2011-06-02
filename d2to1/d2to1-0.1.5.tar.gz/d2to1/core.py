import os
import warnings

from distutils import log
from distutils.core import Distribution as _Distribution
from distutils.errors import DistutilsFileError, DistutilsSetupError, \
                             DistutilsOptionError, DistutilsModuleError
from setuptools import Command
from setuptools.dist import _get_unpatched

from d2to1.util import cfg_to_args, resolve_name


_Distribution = _get_unpatched(_Distribution)


def d2to1(dist, attr, value):
    """Implements the actual d2to1 setup() keyword.  When used, this should be
    the only keyword in your setup() aside from `setup_requires`.

    If given as a string, the value of d2to1 is assumed to be the relative path
    to the setup.cfg file to use.  Otherwise, if it evaluates to true, it
    simply assumes that d2to1 should be used, and the default 'setup.cfg' is
    used.

    This works by reading the setup.cfg file, parsing out the supported
    metadata and command options, and using them to rebuild the
    `DistributionMetadata` object and set the newly added command options.

    The reason for doing things this way is that a custom `Distribution` class
    will not play nicely with setup_requires; however, this implementation may
    not work well with distributions that do use a `Distribution` subclass.
    """

    if not value:
        return
    if isinstance(value, basestring):
        path = os.path.abspath(value)
    else:
        path = os.path.abspath('setup.cfg')
    if not os.path.exists(path):
        raise DistutilsFileError(
            'The setup.cfg file %s does not exist.' % path)

    # Converts the setup.cfg file to setup() arguments
    try:
        attrs = cfg_to_args(path)
    except Exception, e:
        raise DistutilsSetupError(
                'Error parsing %s: %s: %s' % (path, e.__class__.__name__,
                                              unicode(e)))

    # Repeat some of the Distribution initialization code with the newly
    # provided attrs
    if attrs:
        # Skips 'options' and 'licence' support which are rarely used; may add
        # back in later if demanded
        for key, val in attrs.iteritems():
            if hasattr(dist.metadata, 'set_' + key):
                getattr(dist.metadata, 'set_' + key)(val)
            elif hasattr(dist.metadata, key):
                setattr(dist.metadata, key, val)
            elif hasattr(dist, key):
                setattr(dist, key, val)
            else:
                msg = 'Unknown distribution option: %s' % repr(key)
                warnings.warn(msg)

    # Re-finalize the underlying Distribution
    _Distribution.finalize_options(dist)

    # This bit comes out of distribute/setuptools
    if isinstance(dist.metadata.version, (int, long, float)):
        # Some people apparently take "version number" too literally :)
        dist.metadata.version = str(dist.metadata.version)

    # Evil patching to enable command hooks
    # Adding these class attributes is the easiest way for 'pre_hook' and
    # 'post_hook' to be counted as valid options
    Command.pre_hook = None
    Command.post_hook = None

    # Patch _set_command_options to add parsing for hooks--this seems like the
    # only place that this can be done reliably
    __set_command_options = _Distribution._set_command_options
    def _set_command_options(self, command_obj, option_dict=None):
        command_name = command_obj.get_command_name()
        if option_dict is None:
            option_dict = self.get_option_dict(command_name)

        for opt, val in option_dict.items():
            filename, val = val
            if opt.startswith('pre_hook.') or opt.startswith('post_hook.'):
                hook_type, alias = opt.split('.', 1)
                hook_dict = option_dict.setdefault(
                        hook_type, (filename, {}))[1]
                hook_dict[alias] = val
                del option_dict[opt]

        __set_command_options(self, command_obj, option_dict)
    _Distribution._set_command_options = _set_command_options

    # Patch run_command to run the hooks before and after the command
    def run_command(self, command):
        if self.have_run.get(command):
            return

        cmd_obj = self.get_command_obj(command)
        cmd_obj.ensure_finalized()
        self.run_command_hooks(cmd_obj, 'pre_hook')
        log.info("running %s", command)
        cmd_obj.run()
        self.run_command_hooks(cmd_obj, 'post_hook')
        self.have_run[command] = 1
    _Distribution.run_command = run_command

    def run_command_hooks(self, cmd_obj, hook_kind):
        """Run hooks registered for that command and phase.

        *cmd_obj* is a finalized command object; *hook_kind* is either
        'pre_hook' or 'post_hook'.
        """

        if hook_kind not in ('pre_hook', 'post_hook'):
            raise ValueError('invalid hook kind: %r' % hook_kind)

        hooks = getattr(cmd_obj, hook_kind, None)

        if hooks is None:
            return

        for hook in hooks.values():
            if isinstance(hook, str):
                try:
                    hook_obj = resolve_name(hook)
                except ImportError, e:
                    raise DistutilsModuleError(e)
            else:
                hook_obj = hook

            if not hasattr(hook_obj, '__call__'):
                raise DistutilsOptionError('hook %r is not callable' % hook)

            log.info('running %s %s for command %s',
                     hook_kind, hook, cmd_obj.get_command_name())
            hook_obj(cmd_obj)
    _Distribution.run_command_hooks = run_command_hooks
