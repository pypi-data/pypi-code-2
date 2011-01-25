import sys
import os
from copy import copy
import shutil

from hob.proto import OperaValidator, ValidationError, PackageManager, ErrorType, iterTree, Config, ConfigError, Target, defaultPath
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

def showVersion(version):
    "Returns an argparse Action for showing the program version"
    class ShowVersion(argparse.Action):
        def __init__(self, **kwargs):
            kwargs.update(
                dict(
                    dest=argparse.SUPPRESS,
                    default=argparse.SUPPRESS,
                    nargs=0,
                )
            )
            super(ShowVersion, self).__init__(**kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            parser.exit(message=version)

    return ShowVersion

global_options = [
    ('v', 'verbose', False,
     _('increase verbosity')),
    ('', 'version', False,
     _("show program's version number and exit"),
     showVersion(__version__),
    ),
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
    hob._rst.generate_rst(ui, ui.config.currentTarget(), services, out_dir, syntax)

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
    hob._js.generate_services(ui, ui.config.currentTarget(), services, out_dir, test_framework or js_test_framework, console_logger_tutorial)

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
    parser = argparse.ArgumentParser(prog=__program__)
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
