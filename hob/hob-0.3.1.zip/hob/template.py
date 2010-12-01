import os
import sys
from hob.utils import tempdir
from hob.proto import Package, Service, Message, Field, Enum
from hob import proto
import hob
from mako.lookup import TemplateLookup
from mako.template import Template

__all__ = ("Generator", "TextGenerator",
           )

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Generator(object):
    def __init__(self, level=4, subdir="proto", lookup_args={}):
        self.level = level
        self.directories = [os.path.join(root, 'hob/templates'),
                            os.path.join(root, 'templates'),
                            os.path.join(sys.prefix, 'share/hob/templates')]
        self.lookup = TemplateLookup(directories=self.directories,
                                     module_directory=tempdir(["mako", subdir]),
                                     **lookup_args)

    def findFile(self, relpath):
        for path in self.directories:
            path = os.path.join(path, relpath)
            if os.path.exists(path):
                return path
        raise IOError("Could not find file %s" % relpath)

    def generate(self, template, indent, template_data):
        t = self.lookup.get_template(template)
        template_data["proto"] = proto
        text = t.render_unicode(g=self, hob=hob, **template_data)
        return "".join([(" " * indent + l) for l in text.splitlines(True)])

class TextGenerator(Generator):
    def __init__(self, level=4, doc=True, syntax="proto2"):
        super(TextGenerator, self).__init__(level)
        self.doc = doc
        self.syntax = syntax
        self.messageOptionExcludes = []

    def blockOptions(self, owner, options, indent=0, export=[]):
        return self.generate("proto/block_options.mako", indent,
                             dict(owner=owner, options=options, export=export))

    def inlineOptions(self, owner, options, indent=0, export=[]):
        return self.generate("proto/inline_options.mako", indent,
                             dict(owner=owner, options=options, export=export))

    def package(self, package, indent=0, export=[]):
        return self.generate("proto/package.mako", indent,
                             dict(package=package, export=export))

    def message(self, message, indent=0, export=[]):
        return self.generate("proto/message.mako", indent,
                             dict(message=message, export=export))

    def field(self, field, indent=0, export=[]):
        return self.generate("proto/field.mako", indent,
                             dict(field=field, export=export))

    def service(self, service, indent=0, export=[]):
        return self.generate("proto/service.mako", indent,
                             dict(service=service, export=export))

    def enum(self, enum, indent=0, export=[]):
        return self.generate("proto/enum.mako", indent,
                             dict(enum=enum, export=export))

    def item(self, item, indent=0, export=[]):
        map = {Package: self.package,
               Message: self.message,
               Service: self.service,
               Field:   self.field,
               Enum:    self.enum}
        kind = type(item)
        if map.get(kind, None):
            return map[kind](item, indent=indent, export=export)
        raise TypeError("Cannot export item of type %r" % kind)
