import sys
import os
from copy import copy
import shutil

from hob.proto import OperaValidator, ValidationError, PackageManager, ErrorType, iterTree, Config, ConfigError, Target, defaultPath, Message, Enum, Quantifier
from hob.template import TextGenerator
from hob.cmd import CommandTable, ProgramError, argparse
from hob.utils import _
from hob.ui import UserInterface
from hob import extension, __version__, __program__

__all__ = ("run_exit", "main",
           )

_exts = extension.Manager()
cmds = CommandTable()

warnings = ["all"] + ErrorType.warnings
class WarningAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        for value in values:
            if value not in warnings:
                parser.error("Warning value %r for option %s is not valid, valid warnings are: %s" % (value, option_string, ", ".join(warnings)))
            getattr(namespace, "warning", []).append(value)

global_settings = {
    "pdb": False,
}

global_options = [
    ('', 'verbose', False,
     _('increase verbosity')),
    ('', 'quiet', False,
     _('be silent')),
    ('c', 'config_file', '',
     _("use specific config file instead of system-wide/local config files")),
    ('t', 'target', None,
     _("specify target configuration to use (overrides config file).")),
    ('', 'project', None,
     _("specifies project name or file to use (hob.project)")),
    ('w', 'warning', [],
     _("enable a warning flag, pick from %s" % ", ".join(warnings)),
     WarningAction),
    ('', 'pdb', False,
     _('start python debugger on exceptions')),
    ('', ('profile', 'profile', 'FILE'), "",
     _('profile a command using the python profiler, writes result to specified file')),
     ]

@cmds.options(global_options)
def main_options(ui, verbose, quiet, config_file, target, project, warning, pdb, **kwargs):
    global_settings["pdb"] = ui.pdb = pdb
    if config_file:
        ui.config.reset()
        ui.config.reads("[hob]\ntarget=current\n")
        ui.config.read([config_file])
        ui.config.base = os.path.abspath(os.path.dirname(config_file))
    if target:
        ui.config[('hob', 'target')] = target
    if project:
        ui.config[('hob', 'project')] = project

    if ('hob', 'project') in ui.config:
        project = ui.config[('hob', 'project')]
        if ('projects', project) in ui.config:
            project_file = ui.config[('projects', project)]
            if not os.path.isfile(project_file):
                raise ProgramError("Project file '%s' in project '%s' does not point to a config file" % (project_file, project))
        elif os.path.isfile(project):
            project_file = project
        elif os.path.isdir(project) and os.path.isfile(os.path.join(project, "hob.conf")):
            project_file = os.path.join(project, "hob.conf")
        else:
            raise ProgramError("Could not locate project '%s' in hob.conf or in filesystem" % project)

        proj_conf = Config()
        proj_conf.read([project_file])

        path = proj_conf[('services', 'path')]
        if not os.path.isabs(path):
            path = os.path.abspath(os.path.join(os.path.dirname(project_file), path))
        ui.config[('services', 'path')] = path

        group = "target." + ui.config[('hob', 'target')]
        del ui.config[group]
        for key, value in proj_conf[group]:
            ui.config[(group, key)] = value

    PackageManager.validator_type = OperaValidator

    for w in warning:
        PackageManager.validator.enableWarning(w)

    if verbose:
        ui.verbose_level += 1
    if quiet:
        ui.verbose_level = 0

@cmds.add()
def extensions(ui, **kwargs):
    """Lists all enabled extensions
    """
    ui.outl("enabled extensions:")
    ui.outl()
    for ext in _exts:
        doc = ext.doc or ""
        doc = doc.splitlines()[0]
        ui.outl(" %s %s" % (ext.name.ljust(12), doc))

@cmds.add([
    ('', 'list_files', False,
     _("display which files was used to read configuration")),
    ],
    [])
def config(ui, list_files, **kwargs):
    """Displays the current config.
    This is the result of all loaded config and project files
    as well as overrides from the command-line.
    """
    if list_files:
        for fname in ui.config.files:
            ui.outl(fname)
    else:
        ui.out(ui.config.tostring())

@cmds.add([],
    [
    (('service', 'services'), [],
     _("name of the service to validate or a path to a definition file")),
     ])
def validate(ui, services=[], **kwargs):
    """Validates services, commands, events, messages and fields according to the style guide
    """
    from hob.proto import PackageManager
    if not services:
        services = list(ui.config.currentTarget().services())
    for path in services:
        manager = PackageManager(strict=False)
        if not os.path.isfile(path):
            path = ui.config.currentTarget().servicePath(path)
        ui.out("Scanning %s" % path)
        try:
            pkg = manager.loadFile(path, validate=False)
        except IOError, e:
            ui.outl()
            raise ProgramError("Cannot open proto file '%s': %s" % (path, e.strerror))
        if not pkg:
            ui.out("\nNo protocol buffer definitions found in file %s\n" % path)
        else:
            for service in pkg.services:
                validator = PackageManager.validator_type()
                validator.validateService(service, path=path)
                for message in iterTree(service.messages()):
                    validator.validateMessage(message, service=service, path=path)
                if validator.errors or validator.warnings:
                    ui.outl(" Error")
                    for error in validator.errors:
                        ui.warnl(error)
                    for warning in validator.warnings:
                        ui.warnl(warning)
                else:
                    ui.outl(" OK")

class RepoManager(object):
    def __init__(self, config, target=None, path=None):
        self.config = config
        self.target = target
        self.path = path
        self._packages = None
        self._services = None

    def packages(self):
        if self._packages == None:
            self._packages = {}
            if self.target:
                target = Target(self.target, self.config)
            else:
                target = self.config.currentTarget()
            base_path = None
            if self.path:
                base_path = os.path.dirname(self.path)
            names = target.services()
            for name in names:
                manager = PackageManager(strict=False)
                path = target.servicePath(name)
                if base_path:
                    path = os.path.abspath(os.path.join(base_path, path))
                try:
                    pkg = manager.loadFile(path, validate=False)
                except IOError, e:
                    raise ProgramError("Cannot open proto file '%s': %s" % (path, e.strerror))
                if not pkg:
                    raise ProgramError("No package could be loaded from path %s" % path)
                self._packages[name] = pkg
        return self._packages

    def services(self):
        if self._services == None:
            self._services = {}
            packages = self.packages()
            for pkg in packages.itervalues():
                for service in pkg.services:
                    if service.name not in self._services:
                        self._services[service.name] = {}
                    version = tuple(map(int, service.options["version"].value.split(".")[0:2]))
                    if version[0] not in self._services[service.name]:
                        self._services[service.name][version[0]] = {}
                    self._services[service.name][version[0]][version[1]] = service
        return self._services

class ReleaseManager(object):
    def __init__(self, local, remote):
        self.local = local
        self.remote = remote
        self.ignore = ["ScopeService", "TestService"]

    def compare(self):
        remote = self.remote.services()
        local = self.local.services()
        for name in local:
            if name in self.ignore:
                continue
            if name not in remote:
                print "Unreleased service %s" % name
            else:
                for major in local[name]:
                    if major not in remote[name]:
                        print "Unreleased major version %d of service %s" % (major, name)
                    else:
                        for minor in local[name][major]:
                            if minor not in remote[name][major]:
                                print "Unreleased version %d.%d of service %s" % (major, minor, name)
                            else:
                                self.compareService(local[name][major][minor], remote[name][major][minor])

    def compareService(self, local, remote):
        local_names = {}
        local_numbers = {}
        remote_names = {}
        remote_numbers = {}
        version = ".".join(local.options["version"].value.split(".")[0:2])
        manager = ServiceManager(local, remote)

        # TODO: Check events
        for cmd in local.commands:
            local_names[cmd.name] = cmd
            local_numbers[cmd.id] = cmd
        for cmd in remote.commands:
            remote_names[cmd.name] = cmd
            remote_numbers[cmd.id] = cmd
        for name, cmd in local_names.iteritems():
            if name not in remote_names:
                if cmd.id in remote_numbers:
                    print "%s - %s: Error: Command %s = %d conflicts with remote command %s = %d" % (local.name, version, cmd.name, cmd.id, remote_numbers[cmd.id].name, cmd.id)
                else:
                    print "%s - %s: Info: New command %s = %d" % (local.name, version, cmd.name, cmd.id)
            else:
                manager.compareCommand(cmd, remote_names[name])
        for name, cmd in remote_names.iteritems():
            if name not in local_names:
                print "%s - %s: Error: Remote command %s = %d does not exist locally" % (local.name, version, cmd.name, cmd.id)

MESSAGE_SAME = 1
MESSAGE_EXTENDED = 2
MESSAGE_CONFLICT = 3
class ServiceManager(object):
    def __init__(self, local, remote):
        self.local = local
        self.remote = remote
        self.version = ".".join(local.options["version"].value.split(".")[0:2])

    def compareCommand(self, local, remote):
        if local.id != remote.id:
            print "Error: %s - %s: Command %s = %d conflicts with remote command %s = %d" % (self.local.name, self.version, local.name, local.id, remote.name, remote.id)
        if not self.isCompatibleMessage(local.message, remote.message):
            print "Error: %s - %s: Command %s = %d uses a message structure that conflicts with remote command" % (self.local.name, self.version, local.name, local.id)
        if local.response or remote.response:
            if not self.isCompatibleMessage(local.response, remote.response):
                print "Error: %s - %s: Command %s = %d uses a response structure (%s) that conflicts with remote command (%s)" % (self.local.name, self.version, local.name, local.id, ".".join(local.response.path()), ".".join(remote.response.path()))

    def isCompatibleMessage(self, original, other):
        manager = MessageManager(self.local, self.remote)
        result = manager.compareMessage(original, other)
        return result in (MESSAGE_SAME, MESSAGE_EXTENDED)

class MessageManager(object):
    def __init__(self, local, remote):
        self.local = local
        self.remote = remote
        self.version = ".".join(local.options["version"].value.split(".")[0:2])
        self._checked = {}

    def compareMessage(self, original, other):
        if original == None and other == None:
            return MESSAGE_SAME
        if original == None or other == None:
            return MESSAGE_CONFLICT
        self._checked[original] = True
        #names = dict([(field.name, field) for field in other.fields])
        #numbers = dict([(field.number, field) for field in other.fields])
        result = MESSAGE_SAME
        if len(other.fields) > len(original.fields):
            return MESSAGE_CONFLICT
        messages = []
        enums = []
        for org_field, other_field in zip(original.fields, other.fields):
            if org_field.name != other_field.name:
                return MESSAGE_CONFLICT
            if org_field.number != other_field.number:
                return MESSAGE_CONFLICT
            if org_field.q != other_field.q:
                return MESSAGE_CONFLICT
            # TODO: Some types might be possible to convert to another
            if org_field.type != other_field.type:
                return MESSAGE_CONFLICT
            if org_field.message != None or other_field.message != None:
                if other_field.message != None:
                    for element_type in (Message, Enum, None):
                        if element_type == None:
                            return MESSAGE_CONFLICT
                        if isinstance(org_field.message, element_type):
                            if not isinstance(other_field.message, element_type):
                                return MESSAGE_CONFLICT
                            break
                    if isinstance(org_field.message, Message):
                        if org_field.message.path() != other_field.message.path():
                            return MESSAGE_CONFLICT
                        messages.append((org_field.message, other_field.message))
                    elif isinstance(org_field.message, Enum):
                        if org_field.message.path() != other_field.message.path():
                            return MESSAGE_CONFLICT
                        enums.append((org_field.message, other_field.message))
        # Check extra fields
        for field in original.fields[len(other.fields):]:
            # New fields must either be optional or repeated
            if field.q == Quantifier.Required:
                return MESSAGE_CONFLICT
        for org_message, other_message in messages:
            if org_message in self._checked:
                continue
            sub_result = self.compareMessage(org_message, other_message)
            if sub_result == MESSAGE_CONFLICT:
                return MESSAGE_CONFLICT
            elif sub_result == MESSAGE_EXTENDED:
                result = MESSAGE_EXTENDED
        for org_enum, other_enum in enums:
            if org_enum in self._checked:
                continue
            sub_result = self.compareEnum(org_enum, other_enum)
            if sub_result == MESSAGE_CONFLICT:
                return MESSAGE_CONFLICT
            elif sub_result == MESSAGE_EXTENDED:
                result = MESSAGE_EXTENDED
        return result

    def compareEnum(self, original, other):
        return MESSAGE_SAME

@cmds.add([
    ('', ('service', 'services'), [],
     _("only release specified services")),
     ],
    [
    ('path', None,
     _("location where services should be released, can point to a directory or a config file")),
     ])
def release(ui, path, **kwargs):
    services = ui.config.currentTarget().services()

    remote = Config()
    if os.path.isdir(path):
        conf_path = os.path.join(path, "hob.conf")
        if not os.path.exists(path):
            raise ProgramError("No hob.conf file found in path %s" % path)
    else:
        conf_path = path
    remote.read([conf_path])
    remote = RepoManager(remote, path=conf_path, target="all")
    local = RepoManager(ui.config)
    manager = ReleaseManager(local, remote)
    manager.compare()

    # remote_services = remote.currentTarget().services()
    # print "local:"
    # for name in services:
        # manager = PackageManager(strict=False)
        # path = ui.config.currentTarget().servicePath(name)
        # try:
           # pkg = manager.loadFile(path, validate=False)
        # except IOError, e:
           # raise ProgramError("Cannot open proto file '%s': %s" % (path, e.strerror))
        # if not pkg:
           # raise ProgramError("No package could be loaded from path %s" % path)
        # for service in pkg.services:
            # print " " + service.name + " - " + service.options["version"].value
    # print "remote: " + conf_path
    # remote_base = os.path.dirname(conf_path)
    # for name in remote_services:
        # manager = PackageManager(strict=False)
        # path = remote.currentTarget().servicePath(name)
        # path = os.path.abspath(os.path.join(remote_base, path))
        # try:
           # pkg = manager.loadFile(path, validate=False)
        # except IOError, e:
           # raise ProgramError("Cannot open proto file '%s': %s" % (path, e.strerror))
        # if not pkg:
           # raise ProgramError("No package could be loaded from path %s" % path)
        # for service in pkg.services:
            # print " " + service.name + " - " + service.options["version"].value


@cmds.add([
    ('', 'out_file', None,
     _("write generated code to specified file")),
    ('', 'out_dir', None,
     _("write generated code to specified directory, one file is generated per service")),
    ('t', ('type', 'types'), [],
     _("types to export, default is to export all types. choose from package, service, message and enum, or use 'all' to export all types")),
    ('s', 'syntax', "proto2",
     _("syntax to use in export. --syntax=scope will enable a syntax specific to the scope protocol, services descriptions are quite different from normal protobuf syntax. "
       "syntax=proto2 (the default) will export syntax compatible with Google Protocol Buffer, this will remove 'service' from the export type (--type)")),
     ],
    [
    (('service', 'services'), [],
     _("name of the service to generate definitions for or a path to a definition file")),
     ])
def proto(ui, services, out_file, out_dir, types, syntax, **kwargs):
    """Generate Protocol Buffer definitions
    """
    from hob.proto import PackageManager
    f = sys.stdout
    if out_dir:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    elif out_file:
        f = open(out_file, "w")
    if not services:
        services = list(ui.config.currentTarget().services())

    if not types:
        if syntax == "proto2":
            # proto2 does not support our service definitions, remove them
            types = ["package", "message", "enum"]
        else:
            types = ["package", "service", "message", "enum"]
    else:
        if "all" in types:
            types = ["package", "service", "message", "enum"]

    if services:
        if out_dir:
            for extra_file, extra_dir in (('proto/scope_descriptor.proto', 'opera/scope'), ('proto/google/protobuf/descriptor.proto', 'google/protobuf')):
                extra_dir = os.path.normpath(os.path.join(out_dir, extra_dir))
                if not os.path.exists(extra_dir):
                    os.makedirs(extra_dir)
                root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                fname = os.path.join(extra_dir, os.path.basename(extra_file))
                shutil.copyfile(os.path.join(root, "templates", extra_file), fname)
                ui.outl("Coped %s to '%s'" % (extra_file, fname))
    text = ""
    for fname in services:
        try:
            if os.path.isfile(fname):
                manager = PackageManager()
                package = manager.loadFile(fname)
            else:
                package = ui.config.currentTarget().findPackage(fname)
        except IOError, e:
            raise ProgramError("Cannot open proto file '%s': %s" % (fname, e.strerror))

        gen = TextGenerator(syntax=syntax)
        text = gen.package(package, export=types)
        if out_dir:
            if package.services:
                out_name = package.services[0].name
            elif package.name:
                out_name = package.name
            else:
                out_name = fname
            fname = os.path.join(out_dir, out_name + ".proto")
            outfile = open(fname, "w").write(text)
            ui.outl("Wrote service %s to '%s'" % (out_name, fname))
        else:
            f.write(text)

@cmds.add(
    [
    ('', 'out_file', None,
     _("write generated code to specified file")),
    ('', 'out_dir', None,
     _("write generated code to specified directory, one file is generated per service")),
    ('', 'compact', False,
     _("Write compact XML for machine use")),
     ],
    [(('service', 'services'), [],
      _("name of the service to generate definitions for or a path to a definition file")),
    ])
def xml(ui, services, out_file, out_dir, compact, **kwargs):
    """Generate XML structures of protocol definitions
    """
    from hob.proto import PackageManager
    from hob._xmlgen import createDocument, createServiceNode, generateXML

    xmlfunc = "toprettyxml"
    if compact:
        xmlfunc = "toxml"

    f = sys.stdout
    if out_dir:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    elif out_file:
        f = open(out_file, "w")
    if not services:
        services = list(ui.config.currentTarget().services())
    if not out_dir:
        doc = createDocument()
    for fname in services:
        if out_dir:
            doc = createDocument()
        if os.path.isfile(fname):
            manager = PackageManager()
            package = manager.loadFile(fname)
            if not package:
                print >> sys.stderr, "No protocol buffer definitions found in file %s" % fname
        else:
            package = ui.config.currentTarget().findPackage(fname)
        node = doc.documentElement
        generateXML(package, node)
        if out_dir:
            text = getattr(doc, xmlfunc)()
            fname = os.path.join(out_dir, service.name + ".xml")
            outfile = open(fname, "w").write(text)
            print "Wrote service %s to '%s'" % (service.name, fname)
    if not out_dir:
        text = getattr(doc, xmlfunc)()
        f.write(text)

@cmds.add(
    [
    ('', 'out_dir', "rst-doc",
      _("write generated rst-docs to specified directory, one file is generated per service. Default is 'rst-doc'")),
    ('s', 'syntax', "scope",
     _("syntax to use in export. --syntax=scope (the default) will enable a syntax specific to the scope protocol, services descriptions are quite different from normal protobuf syntax. "
       "syntax=proto2 will export syntax compatible with Google Protocol Buffer, events will placed in comments as they are not supported by this syntax")),
    ],
    [(('service', 'services'), [],
      _("name of the service to generate code for or a path to a definition file")),
      ])
def rst_doc(ui, services, out_dir, syntax, **kwargs):
    """Create reST documentation of selected services.
    If no files are specified all services are added.
    """
    import hob._rst
    hob._rst.generate_rst(ui.config.currentTarget(), services, out_dir, syntax)

@cmds.add(
    [('', 'out_dir', 'js-out',
      _("write generated JS files to specified directory, one file is generated per service. Default is 'js-out'.")),
     ('', 'test_framework', False,
      _("create a test framework")),
     ('', 'js_test_framework', False,
      _("alias for --test-framework")),
     ('', 'console_logger_tutorial', False,
      _("create the files of the console logger tutorial")),
      ],
    [(('service', 'services'), [],
      _("name of the service to generate code for or a path to a definition file")),
      ])
def js(ui, services, out_dir, test_framework, js_test_framework, console_logger_tutorial, **kwargs):
    """Create service interfaces for JavaScript.
    If no files are specified, the following files
    will be added in the 'service' folder:
    console_logger.py,
    http_logger.py,
    scope.py,
    window_manager.py,
    ecmascript_debugger.py.
    Files can also be specified with the service name,
    e.g. just ecmascript-debugger.
    scope.py and window_manager.py will always be added."""
    import hob._js
    hob._js.generate_services(ui.config.currentTarget(), services, out_dir, test_framework or js_test_framework, console_logger_tutorial)

def main(args=None):
    try:
        from mako.template import Template
    except ImportError:
        raise ProgramError("Python package `mako` is not installed, without this code-generation is not possible.\nGet it from http://www.makotemplates.org/")

    ui = UserInterface(_exts, cmds)
    ui.config.read([os.path.expanduser('~/.hob.conf'), os.path.expanduser('~/hob.conf')])
    if os.path.exists("hob.conf") or os.path.exists("hob_private.conf"):
        if ("hob", "project") in ui.config:
            del ui.config[("hob", "project")]  # The global project entry should not be used if a hob file is read from cwd
    if os.path.exists("hob.conf"):
        ui.config.read(["hob.conf"])
    if os.path.exists("hob_private.conf"):
        ui.config.read(["hob_private.conf"])
    ui.config.reads("[hob]\ntarget=current\n")
    _exts.setup(ui, cmds)
    parser = argparse.ArgumentParser(version=__version__, prog=__program__)
    cmds.setup(parser)
    opts = parser.parse_args(args)
    cmds.loadconfig(ui.config, opts)
    if opts.profile:
        cmds.profile_filename = opts.profile
    return cmds.process(ui, opts)

def run_exit(args=None):
    try:
        sys.exit(main(args))
    except (ProgramError, ValidationError, ConfigError), e:
        print >> sys.stderr, e
        sys.exit(1)
    except KeyboardInterrupt:
        print >> sys.stderr, "Aborted"
        sys.exit(1)
    except Exception, e:
        if global_settings["pdb"]:
            import traceback
            traceback.print_exc(e)
            import pdb
            pdb.post_mortem()
        else:
            print >> sys.stderr, e
        sys.exit(1)

if __name__ == "__main__":
    run_exit()
