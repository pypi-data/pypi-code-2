import os
import codecs
import textwrap
from hob._js import protoHTMLClass
from hob.proto import *
from hob.template import Generator, TextGenerator

class RstGenerator(Generator):
    def __init__(self, syntax="scope", **kwargs):
        super(RstGenerator, self).__init__(lookup_args=dict(default_filters=['decode.utf8']),
                                           **kwargs)
        self.syntax = syntax

    def proto(self, **kwargs):
        return TextGenerator(syntax=self.syntax, **kwargs)

    def package(self, package, indent=0):
        return self.generate('rst-doc/package.mako', indent,
                             dict(package=package))

    def serviceindex(self, service_name, services, indent=0):
        return self.generate('rst-doc/rst-doc-service-index.mako', indent,
                             dict(service_name=service_name,
                                  services=services))

    def service(self, service, indent=0):
        return self.generate('rst-doc/rst-doc-service.mako', indent,
                             dict(service=service))

    def commands(self, service, indent=0):
        return self.generate('rst-doc/rst-proto-defs.mako', indent,
                             dict(service=service))

    def message(self, message, indent=0):
        return self.generate('js/js-message-definition.mako', indent,
                              dict(message=message,
                                   indent_level=1,
                                   protoHTMLClass=protoHTMLClass))

def generate_rst(ui, target, service_names, out_dir="rst-doc", syntax="scope"):
    from hob.proto import PackageManager, iterProtoFiles
    rst_doc_service_index = []
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if not service_names:
        service_names = list(target.services())
    from collections import defaultdict
    service_index = defaultdict(list)
    for path in service_names:
        manager = PackageManager()
        if os.path.isfile(path):
            package = manager.loadFile(path)
        else:
            package = target.findPackage(path)
        if not package:
            ui.warnl("No protocol buffer definitions found in file %s" % path)
        for service in package.services:
            rst_doc_service_index.append(service)
            gen = RstGenerator(syntax=syntax)
            text = gen.package(package)
            version = '_'.join(service.options["version"].value.split('.')[:2])
            service_index[service.name].append(service)
            fname = os.path.join(out_dir, service.name, "%s_%s.rst" % (service.name, version))
            if not os.path.exists(os.path.dirname(fname)):
                os.makedirs(os.path.dirname(fname))
            outfile = open(fname, "w").write(text.encode('utf-8'))
            ui.outl("Wrote service %s to '%s'" % (service.name, fname))
    for service_name, services in service_index.iteritems():
        gen = RstGenerator(syntax=syntax)
        text = gen.serviceindex(service_name, services)
        fname = os.path.join(out_dir, "%s.rst" % service_name)
        outfile = open(fname, "w").write(text.encode('utf-8'))
        ui.outl("Wrote service index %s to '%s'" % (service_name, fname))
