from __future__ import with_statement
import os
import codecs
import shutil
from hob import proto
from hob.proto import *
from hob.proto import ServiceManager, iterProtoFiles  # fixme: presuambly redundant. runeh
from hob.utils import dashed_name, DIST_ROOT, tempdir, strquote
from hob.cmd import ProgramError
from hob.template import Generator
from mako.template import Template
from mako.lookup import TemplateLookup

LIB_DIR = "lib"
DOC_DIR = "doc"
DOC_ROOT_URL = "http://dragonfly.opera.com/app/scope-interface/"

class Javascript(object):
    up2date_count = 0

javascript = Javascript()

WRITE_NONE = 0  # File already contain data, nothing is written
WRITE_UPDATED = 1  # File already exists but with different data, file was updated
WRITE_CREATED = 2  # File did not exist, file created

def updateFile(fname, content, mode="wb", rmode="rb"):
    """Updates file content of `fname` if needed and returns the result
    Returns WRITE_NONE if the file already contained the content.
    Returns WRITE_UPDATED if the file existed but was updated with new content.
    Returns WRITE_CREATED if the file did not exist but was created with new content.
    """
    result = WRITE_CREATED
    if os.path.exists(fname):
        f = open(fname, rmode)
        orig_content = f.read()
        if content == orig_content:
            return WRITE_NONE
        f.close()
        result = WRITE_UPDATED
    with open(fname, mode) as f:
        f.write(content)
    return result

def protoHTMLClass(field):
    ptypes = {Proto.Message: "message",
              Proto.Int32: "number",
              Proto.Uint32: "number",
              Proto.Sint32: "number",
              Proto.Fixed32: "number",
              Proto.Sfixed32: "number",
              Proto.Int64: "number",
              Proto.Uint64: "number",
              Proto.Sint64: "number",
              Proto.Fixed64: "number",
              Proto.Sfixed64: "number",
              Proto.Bool: "bool",
              Proto.String: "string",
              Proto.Bytes: "bytes",
              Proto.Float: "number",
              Proto.Double: "number",
             }
    return ptypes[field.type]

class TemplateEnv(object):
    def __init__(self, lookup, out_dir, js_test_framework, console_logger_tutorial):
        self.lookup = lookup
        self.out_dir = out_dir
        self.js_test_framework = js_test_framework
        self.console_logger_tutorial = console_logger_tutorial

def const_id(field, name=""):
    return dashed_name(field.message and name or field.name, '_').upper()

def generate_service_implementation(ui, service, template_env):
    version = '_'.join(service.options["version"].value.split('.')[:2])
    service_name = dashed_name(service.name, dash="_")
    fname = "%s_%s.js" % (service_name, version)
    short_fpath = os.path.join(service_name == "scope" and LIB_DIR or DOC_DIR, fname)
    fpath = os.path.join(template_env.out_dir, short_fpath)
    template = template_env.lookup.get_template("js/js-service-implementation.mako")
    text = template.render_unicode(
        service=service,
        dashed_name=dashed_name,
        create_test_framework=template_env.js_test_framework,
        lookup=template_env.lookup,
        generate_field_consts=generate_field_consts,
        const_id=const_id,
        console_logger_tutorial=template_env.console_logger_tutorial,
        doc_rot_url=DOC_ROOT_URL,
        ).encode('utf-8')
    res = updateFile(fpath, codecs.BOM_UTF8 + text, mode="wb")
    if res in (WRITE_UPDATED, WRITE_CREATED):
        ui.outl("Wrote service-implementation %s to '%s'" % (service.name, short_fpath))
    else:
        javascript.up2date_count += 1

def generate_file(services, lookup, template_name, create_test_framework=False,
            console_logger_tutorial=False, lib_dir="", doc_dir="", language_context='js'):
    from hob import proto
    return lookup.get_template(template_name).render_unicode(
        services=services,
        dashed_name=dashed_name,
        strquote=strquote,
        create_test_framework=create_test_framework,
        console_logger_tutorial=console_logger_tutorial,
        lookup=lookup,
        generate_field_consts=generate_field_consts,
        const_id=const_id,
        lib_dir=lib_dir,
        doc_dir=doc_dir,
        language_context=language_context,
        proto=proto,
        )

def generate_proto_defs(
        message,
        lookup,
        create_test_framework=False,
        classes=True,
        indent_level=0,
        comments=["/** \n", " * ", " */"],
        ):
    from hob import proto
    return lookup.get_template('js/js-message-definition.mako').render_unicode(
        message=message,
        protoHTMLClass=protoHTMLClass,
        classes=classes,
        indent_level=indent_level,
        comments=comments,
        proto=proto,
        )

def generate_message_classes(service, message, lookup, create_test_framework=False):
    return lookup.get_template('js/js-message-classes.mako').render_unicode(
        service=service,
        message=message,
        proto=proto,
        )

def generate_field_consts(
        message,
        lookup,
        create_test_framework=False,
        indent='  ',
        ):
    from hob import proto
    return lookup.get_template('js/js-field-consts.mako').render_unicode(
        message=message,
        create_test_framework=create_test_framework,
        dashed_name=dashed_name,
        indent=indent,
        const_id=const_id,
        proto=proto,
        )

def generate_services(ui, target, args, out_dir="js-out", js_test_framework=False, console_logger_tutorial=False):
    gen = Generator(subdir="js", lookup_args=dict(default_filters=['decode.utf8']))
    lookup = gen.lookup
    # lookup = TemplateLookup(
        # directories=[
            # os.path.join(DIST_ROOT, 'templates'),
            # os.path.join(DIST_ROOT, 'templates', 'js'),
            # os.path.join(DIST_ROOT, 'templates', 'py'),
            # ],
        # module_directory=tempdir(["mako", "js"]),
        # default_filters=['decode.utf8'],
        # )
    service_list = []
    tasks = [generate_service_implementation]
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    for repo in [LIB_DIR, DOC_DIR]:
        if not os.path.exists(os.path.join(out_dir, repo)):
            os.makedirs(os.path.join(out_dir, repo))
    template_env = TemplateEnv(lookup, out_dir, js_test_framework, console_logger_tutorial)

    for path in iterProtoFiles(target.selectServiceFiles(args)):
        manager = PackageManager()
        package = manager.loadFile(path)
        if not package:
            ui.warnl("No protocol buffer definitions found in file %s" % path)

        for service in package.services:  # TODO: Should generate for package instead?
            if "version" not in service.options:
                raise Exception("Option 'version' is not set on service %s" % service.name)
            service_list.append(service)
            for task in tasks:
                task(ui, service, template_env)
    dependencies = {"Scope": False,
                    "WindowManager": False}
    for service in service_list:
        if service.name in ("Scope", "WindowManager"):
            dependencies[service.name] = True
    if not all(dependencies.itervalues()):
        required = [k for k, v in dependencies.iteritems() if not v]
        raise ProgramError("The following services must be included for the generated code to work: %s" % ", ".join(required))
    sources = [
        ('client.js', 'js/js-client.mako', ''),
        ('client.html', 'js/js-client-html.mako', ''),
        ('service_base.js', 'js/js-service-base.mako', LIB_DIR),
        ('http_interface.js', 'js/js-http-interface.mako', LIB_DIR),
        ('stp_0_wrapper.js', 'js/js-stp-0-wrapper.mako', LIB_DIR),
        ('build_application.js', 'js/js-build_application.mako', ''),
        ]
    if js_test_framework:
        sources += [
            ('runtimes.js', 'js/js-runtimes.mako', ''),
            ('dom.js', 'js/js-DOM.mako', ''),
            ('windows.js', 'js/js-windows.mako', ''),
            ]

    for file_name, template, rep in sources:
        text = generate_file(
                    service_list,
                    lookup,
                    template,
                    create_test_framework=js_test_framework,
                    console_logger_tutorial=console_logger_tutorial,
                    lib_dir=LIB_DIR,
                    doc_dir=DOC_DIR,
                    language_context='js',
                    )
        short_path = os.path.join(rep, file_name)
        path = os.path.join(out_dir, short_path)
        res = updateFile(path, codecs.BOM_UTF8 + text.encode('utf-8'), mode="wb")
        if res in (WRITE_UPDATED, WRITE_CREATED):
            ui.outl("Wrote '%s'" % short_path)
        else:
            javascript.up2date_count += 1

    if js_test_framework:
        for repo in ['defs', 'classes']:
            def_path = os.path.join(out_dir, repo)
            if not os.path.exists(def_path):
                os.mkdir(def_path)
        message_defs = []
        for service in service_list:
            version = ".".join(service.options["version"].value.split('.')[:2])
            for command in service.itercommands():
                message_defs.append((
                    "defs", 
                    "%s.%s.%s.%s.def" % (service.name, version, 'commands', command.name),
                    generate_proto_defs(command.message, lookup, js_test_framework)
                ))
                message_defs.append((
                    "defs", 
                    "%s.%s.%s.%s.def" % (service.name, version, 'responses', command.name),
                    generate_proto_defs(command.response, lookup, js_test_framework)
                ))
                message_defs.append((
                    "classes", 
                    ("%s.%s.%s.%s.js" % (service.name, version, 'responses', command.name)).lower(),
                    generate_message_classes(service, command.response, lookup, js_test_framework)
                ))
            for event in service.iterevents():
                message_defs.append((
                    "defs", 
                    "%s.%s.%s.%s.def" % (service.name, version, 'events', event.name),
                    generate_proto_defs(event.message, lookup, js_test_framework)
                ))
                message_defs.append((
                    "classes", 
                    ("%s.%s.%s.%s.js" % (service.name, version, 'events', event.name)).lower(),
                    generate_message_classes(service, event.message, lookup, js_test_framework)
                ))
        for repo, file_name, text in message_defs:
            short_path = os.path.join(repo, file_name)
            path = os.path.join(out_dir, short_path)
            res = updateFile(path, text, mode="wb")
            if res in (WRITE_UPDATED, WRITE_CREATED):
                ui.outl("Wrote '%s'" % short_path)
            else:
                javascript.up2date_count += 1
    sources = [
        ('clientlib_async.js', LIB_DIR),
        ('tag_manager.js', LIB_DIR),
        ('json.js', LIB_DIR),
        ('namespace.js', LIB_DIR),
        ('messagemixin.js', LIB_DIR),
        ('messagebroker.js', LIB_DIR),
        ('message_maps.js', LIB_DIR),
        ('get_message_maps.js', LIB_DIR),
        ]
    if js_test_framework:
        sources += [
            ('style.css', ''),
            ('test_framework.js', ''),
            ('logger.js', ''),
            ('utils.js', LIB_DIR),
            ]
    if console_logger_tutorial:
        sources += [
            ('simpleconsolelogger.js', ''),
            ]
    for file_name, repo in sources:
        short_source_path = gen.findFile(os.path.join('js', file_name))
        source_path = os.path.join(DIST_ROOT, short_source_path)
        out_path = os.path.join(out_dir, repo)
        out_file = os.path.join(out_path, os.path.basename(source_path))
        with open(source_path, "rb") as f:
            orig = f.read()
        needs_copy = True
        if os.path.exists(out_file):
            with open(out_file, "rb") as f:
                if f.read() == orig:
                    needs_copy = False
        if needs_copy:
            shutil.copy(source_path, out_path)
            ui.outl("Copied %s" % short_source_path)
        else:
            javascript.up2date_count += 1

    if javascript.up2date_count > 0:
        ui.outl("%d files was already up-to-date" % javascript.up2date_count)
