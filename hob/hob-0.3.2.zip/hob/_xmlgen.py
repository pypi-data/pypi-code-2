import random
import re
from xml.dom.minidom import getDOMImplementation

# TODO: Change include_tag to be a STP version check instead

from hob import utils
from hob.proto import Proto, Quantifier, Event, Command, Request, Event, Service, Package

tag_comment = "<!-- `tag` is used for syncronization of request/response and is always the first XML sub-node, not part of content -->"

def xml_name(name):
    return utils.dashed_name(name)

class XMLSchemaMessageGenerator(object):
    message = None
    name = None

    # Generated text
    text = None

    def __init__(self, message, name, include_tag=False):
        self.message = message
        self.name = name
        self.include_tag = include_tag
        self.generate()

    def generate(self):
        self.text = ""
        self.text += "<grammar xmlns=\"http://relaxng.org/ns/structure/1.0\" datatypeLibrary=\"http://www.w3.org/2001/XMLSchema-datatypes\">\n"
        messages = [self.message]
        tag_text = ""
        if self.include_tag:
            tag_text += "    <element name=\"tag\"><data type=\"int\"/></element> %s\n" % tag_comment
        defs = ["  <start>\n%s    <ref name=\"%s\"/>\n  </start>\n" % (tag_text, xml_name(self.name))]
        while messages:
            message = messages.pop(0)
            include_tag = False
            if message is self.message:
                name = self.name
            else:
                name = message.name
            text, newmessages = self.generateMessage(message, name)
            messages += newmessages
            text = "".join(["  " + l for l in text.splitlines(True)])
            defs.append(text)
        self.text += "\n".join(defs)
        self.text += "</grammar>\n"

    def generateMessage(self, message, message_name):
        def_name = xml_name(message_name)
        text  = "<define name=\"%s\">\n" % def_name
        messages = []
        for field in message.fields:
            if field.type == Proto.Message:  # and not field.message.is_global:
                messages.append(field.message)
            name = xml_name(field.name)
            if field.type == Proto.String:
                data_type = "<text/>"
            elif field.type == Proto.Bytes:
                data_type = "<attribute name=\"encoding\"><value>base64</value></attribute><text/>"
            elif field.type == Proto.Message:
                data_type = "<ref name=\"%s\"/>" % xml_name(field.message.name)
            else:  # Bool and ints
                data_type = "<data type=\"int\"/>"
            comment = ""
            if field.comment:
                comment = field.comment.replace("-->", "--\>")
                for f in message.fields:
                    comment = re.sub("`%s`" % re.escape(f.name), "`%s`" % xml_name(f.name), comment)
                comment = " <!-- " + comment + " -->"
            if field.q == Quantifier.Required:
                text += "  <element name=\"%s\">%s</element>%s\n" % (name, data_type, comment)
            elif field.q == Quantifier.Optional:
                text += "  <optional>%s\n    <element name=\"%s\">%s</element>\n  </optional>\n" % (comment, name, data_type)
            elif field.q == Quantifier.Repeated:
                text += "  <zeroOrMore>%s\n    <element name=\"%s\">%s</element>\n  </zeroOrMore>\n" % (comment, name, data_type)
            else:
                raise Exception("Unknown quantifier %r" % field.q)
        text += "</define> <!-- %s -->\n" % def_name
        return text, messages

class XMLOptionsGenerator(object):
    def __init__(self, options):
        self.options = options

    def generate(self, doc, node=None):
        if node == None:
            node = doc.createElement("options")
        options = self.options
        for opt_name, opt_value in options.iteritems():
            option = doc.createElement("option")
            option.setAttribute("name", opt_name)
            option.setAttribute("value", opt_value.value)
            node.appendChild(option)
        return node

class XMLMessageGenerator(object):
    message = None

    # Generated text
    text = None

    def __init__(self, message, name, include_tag=False):
        self.message = message
        self.name = name
        self.include_tag = include_tag
        random.seed(message.name + str(len(message.fields)))
        self.numbers = [1, 3, 5, 7, 10, 42]
        x = random.randint(0, len(self.numbers))
        self.numbers = self.numbers[x:] + self.numbers[:x]
        self.bools = [1, 0]
        x = random.randint(0, len(self.bools))
        self.bool = self.bools[x:] + self.bools[:x]
        self.strings = ["html", "dom", "node", "body", "size", "css"]
        x = random.randint(0, len(self.strings))
        self.strings = self.strings[x:] + self.strings[:x]
        self.bytes = ["yv66vg=="]
        x = random.randint(0, len(self.bytes))
        self.bytes = self.bytes[x:] + self.bytes[:x]
        self.repeats = [1, 3, 0]
        self.generate()

    def generate(self):
        self.text = ""
        self.text += self.generateMessage(self.message, self.name, self.include_tag)

    def generateMessage(self, message, message_name, include_tag):
        def_name = ""
        text = ""
        if message_name:
            def_name = xml_name(message_name)
            text += "<%s>\n" % def_name
        messages = []
        if include_tag:
            text += "  <tag>3</tag> %s\n" % tag_comment
        for field in message.fields:
            name = xml_name(field.name)
            repeat = 1
            if field.q == Quantifier.Repeated:
                repeat = self.repeats.pop(0)
                self.repeats.append(repeat)
            for idx in range(repeat):
                attributes = []
                if field.type == Proto.String:
                    data_type = self.strings.pop(0)
                    self.strings.append(data_type)
                elif field.type == Proto.Bytes:
                    data_type = self.bytes.pop(0)
                    self.bytes.append(data_type)
                    attributes.append("encoding=\"base64\"")
                elif field.type == Proto.Message:
                    data_type = self.generateMessage(field.message, False, False)
                    data_type = "".join(["  " + l for l in data_type.splitlines(True)])
                    name = xml_name(field.message.name)
                elif field.type == Proto.Bool:
                    data_type = self.bools.pop(0)
                    self.bools.append(data_type)
                    data_type = str(data_type)
                else:  # ints
                    data_type = self.numbers.pop(0)
                    self.numbers.append(data_type)
                    data_type = str(data_type)
                if attributes:
                    attributes = " " + " ".join(attributes)
                else:
                    attributes = ""
                if data_type.find("\n") != -1:
                    if data_type[-1] != "\n":
                        data_type += "\n"
                    text += "  <%s%s>\n%s  </%s>\n" % (name, attributes, data_type, name)
                else:
                    text += "  <%s%s>%s</%s>\n" % (name, attributes, data_type, name)
        if message_name:
            text += "</%s>\n" % def_name
        return text

class XMLServiceGenerator(object):
    service = None

    def __init__(self, service):
        self.service = service

    def generate(self, doc, node=None):
        if node == None:
            node = doc.createElement("service")
        service = self.service
        node.setAttribute("name", service.name)
        if service.doc:
            node.setAttribute("doc", service.doc.text)

        optionsNode = XMLOptionsGenerator(service.options).generate(doc)
        node.appendChild(optionsNode)

        for command in service.itercommands():
            is_event = isinstance(command, Event)
            if is_event:
                command_el = doc.createElement("event")
            else:
                command_el = doc.createElement("call")
            if command.doc:
                command_el.setAttribute("doc", command.doc.text)
            command_el.setAttribute("name", command.name)
            command_el.setAttribute("command-id", str(command.id))
            if is_event:
                command_el.setAttribute("out", ".".join(command.message.absPath()))
            else:
                command_el.setAttribute("in", ".".join(command.message.absPath()))
                command_el.setAttribute("out", ".".join(command.response.absPath()))
            node.appendChild(command_el)
        return node

class XMLPackageGenerator(object):
    package = None

    def __init__(self, package):
        self.package = package

    def generate(self, doc, node=None):
        if node == None:
            node = doc.createElement("package")
        package = self.package
        node.setAttribute("name", package.name)
        if package.doc:
            node.setAttribute("doc", package.doc)
        return node

def createDocument():
    impl = getDOMImplementation()
    return impl.createDocument(None, "scope", None)

def createServiceNode(doc):
    return doc.createElement("service")

def generateXML(package, node=None):
    if not node:
        node = createDocument()
    doc = node.ownerDocument

    package_gen = XMLPackageGenerator(package)
    package_node = package_gen.generate(doc)
    node.appendChild(package_node)

    item_types = [(Service, XMLServiceGenerator),
                  ]

    for item in package.items:
        for cls, gencls in item_types:
            if isinstance(item, cls):
                gen = gencls(item)
                sub_node = gen.generate(doc)
                package_node.appendChild(sub_node)

    return node
#    xml_gen = xml.XMLMessageListGenerator(service.commands, service.coreRelease, include_tag=include_tag)
#    text += "\n" + xml_gen.text
