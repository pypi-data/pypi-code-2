"""
.. autoclass:: Fresnel
   :show-inheritance:
"""

__all__ = ["Fresnel", "Lens"]

try:
    from xml.etree import ElementTree as ET
except:
    from elementtree import ElementTree as ET
from urllib import urlencode
from ordf.collection import Collection
from ordf.graph import Graph
from ordf.namespace import *
from ordf.term import Literal, URIRef, BNode
from datetime import datetime

log = __import__("logging").getLogger(__name__)

class Lens(Graph):
    """
    """
    def __init__(self, fresnel, identifier):
        super(Lens, self).__init__(identifier=identifier)
        self.fresnel = fresnel
        self.group = None
        self.stylesheets = None

    def properties(self, graph, resource):
        properties = []
        for properties in self.objects(self.identifier, FRESNEL["showProperties"]):
            properties = Collection(self, properties)
            properties = list(properties)
            break
        hideProperties = []
        for hideProperties in self.objects(self.identifier, FRESNEL["hideProperties"]):
            hideProperties = Collection(self, hideProperties)
            hideProperties = list(hideProperties)
            break
        subProperties = []
        for prop in properties:
            if isinstance(prop, BNode) and self.one((prop, RDF["type"], FRESNEL["PropertyDescription"])):
                x = self.one((prop, FRESNEL["sublens"], None))
                if x:
                    lens = self.fresnel.lenses.get(x[2])
                else:
                    lens = None
                for prop in self.objects(prop, FRESNEL["property"]):
                    if prop not in hideProperties:
                        yield prop, lens, self.group.formats.get(prop, Format())
                    subProperties.append(prop)
            elif prop == FRESNEL["allProperties"]:
                for prop in graph.distinct_predicates(resource, None):
                    if prop not in hideProperties and prop not in subProperties and prop not in properties:
                        yield prop, None, self.group.formats.get(prop, Format())
            else:
                if prop not in hideProperties:
                    yield prop, None, self.group.formats.get(prop, Format())

    def formatResource(self, graph, resource):
        if self.group:
            stylesheets = set(self.group.stylesheets)
        else:
            stylesheets = set

        elem = ET.Element("div")
        css = ["fresnel_resource"]

        if isinstance(resource, URIRef):
            elem.set("about", resource)
        elif isinstance(resource, BNode):
            elem.set("about", "[_:%s]" % resource)

        log.debug("    Resource: %s" % resource)
        if isinstance(resource, URIRef):
            uri = ET.Element("div")
            uri.set("class", "fresnel_resource_uri")
            a = ET.Element("a")
            a.set("href", resource)

            a.text = resource
            try:
                qname = self.namespace_manager.qname(resource)
                if not qname.startswith("_"):
                    a.text = qname
            except:
                pass
            uri.append(a)
            elem.append(uri)

        properties = self.properties(graph, resource)
        for property, lens, format in properties:
            styles, prop = self.formatProperty(graph, lens, format, resource, property)
            if prop:
                elem.append(prop)
                [stylesheets.add(x) for x in styles]
        elem.set("class", " ".join(css))
        return stylesheets, elem

    def formatProperty(self, graph, lens, format, resource, property):
        log.debug("      Property: %s" % property)
        log.debug("      Format: %s" % format)

        elem = ET.Element("div")

        css, styles = format.propertyStyles
        css = ["fresnel_property"] + css
        elem.set("class", " ".join(css))
        if styles: elem.set("style", " ".join(styles))

        label = format.label(property)
        if label is not None:
            span = ET.Element("span")
            span.set("class", "fresnel_label")
            a = ET.Element("a")
            a.set("href", property)
            a.text = label
            span.append(a)
            elem.append(span)

        values = [
            self.formatValue(graph, lens, format, resource, property, v)
            for v in graph.objects(resource, property)
        ]

        stylesheets = set()
        if values:
            container = ET.Element("div")
            container.set("class", "fresnel_container")
            [([stylesheets.add(s) for s in sheets], container.append(value)) 
             for (sheets, value) in values]
            elem.append(container)
            elem.set("class", " ".join(css))
        else:
            elem = None
        return stylesheets, elem

    def rst(self, span, value):
        try:
            from docutils import core
            parts = core.publish_parts(source=value, writer_name="html")
            doc = u'<?xml version="1.0" encoding="utf-8"?>\n' + \
                u'<html>\n' + parts["body"] + u"</html>\n"
            elem = ET.XML(doc.encode("utf-8"))
            for c in elem.getchildren():
                span.append(c)
        except ImportError:
            span.text = value

    def formatValue(self, graph, lens, format, resource, property, value):
        elem = ET.Element("div")
        css, styles = format.valueStyles
        css = ["fresnel_value"] + css
        elem.set("class", " ".join(css))
        if styles: elem.set("style", " ".join(styles))

        if format.group:
            stylesheets = set(format.group.stylesheets)
        else:
            stylesheets = set()

        ns, uri, local = self.namespace_manager.compute_qname(property)
        if ns.startswith("_"):
            ns = "ns%s" % ns[1:]
        elem.set("xmlns:%s" % ns, uri)
        pcurie = "%s:%s" % (ns, local)

        if isinstance(value, Literal):
            elem.set("property", pcurie)
            elem.set("content", value)
            if value.language:
                sp = ET.Element("span")
                sp.set("class", "fresnel_object_language")
                sp.text = u" (%s) " % value.language
                elem.append(sp)
                self.rst(elem, value)
                elem.set("xml:lang", value.language)
            elif value.datatype:
                elem.set("xml:lang", "")
                if value.datatype == XSD["dateTime"]:
                    try:
                        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                        elem.text = dt.ctime()
                    except:
                        elem.text = value
                else:
                    elem.text = value
                elem.set("datatype", value.datatype)
            else:
                elem.set("xml:lang", "")
                self.rst(elem, value)
        elif isinstance(value, URIRef) or isinstance(value, BNode):
            elem.set("rel", pcurie)
            if isinstance(value, URIRef):
                elem.set("resource", value)
            else:
                elem.set("resource", "[_:%s]" % value)
            if lens:
                styles, rsrc = lens.formatResource(graph, value)
                [stylesheets.add(x) for x in styles]
                elem.append(rsrc)
            elif isinstance(value, BNode):
                lens = DefaultLens(self.fresnel, self.group)
                styles, rsrc = lens.formatResource(graph, value)
                [stylesheets.add(x) for x in styles]
                elem.append(rsrc)
            else:
                if isinstance(value, URIRef):
                    if format.one((format.identifier, FRESNEL["value"], FRESNEL["image"])):
                        a = ET.Element("img")
                        a.set("src", value)
                        try:
                            qname = self.namespace_manager.qname(property)
                            a.set("alt", "qname")
                        except:
                            a.set("alt", property)
                    else:
#                        if format.one((format.identifier, FRESNEL["value"], FRESNEL["externalLink"])):
                        a = ET.Element("a")
                        a.set("href", value)
                        try:
                            pfx, uri, rest = self.compute_qname(value)
                            if not pfx.startswith("_"):
                                value = u"%s:%s" % (pfx, rest)
                        except:
                            pass
                        a.text = value
                else:
                    a = ET.Element("span")
                    a.text = value
                elem.append(a)
        return stylesheets, elem

class DefaultLens(Lens):
    def __init__(self, fresnel, group):
        super(DefaultLens, self).__init__(fresnel, None)
        self.group = group
    def properties(self, graph, resource):
        for prop in graph.distinct_predicates(resource):
            yield prop, None, self.group.formats.get(prop, Format())

class Group(Graph):
    def __init__(self, *av, **kw):
        super(Group, self).__init__(*av, **kw)
        self.lenses = {}
        self.formats = {}
        
    @property
    def stylesheets(self):
        if not hasattr(self, "__stylesheets__"):
            self.__stylesheets__ = list(self.distinct_objects(self.identifier, FRESNEL["stylesheetLink"]))
        return self.__stylesheets__

class Format(Graph):
    def __init__(self, *av, **kw):
        super(Format, self).__init__(*av, **kw)
        self.group = None
    def label(self, property):
        # what spaghetti is this!
        for _s, _p, label in self.triples((self.identifier, FRESNEL["label"], None)):
            if label == FRESNEL["none"]:
                return None
            else:
                return label
        try:
            qname = self.namespace_manager.qname(property)
            if not qname.startswith("_"):
                return qname
        except:
            pass
        label = ":" + property.rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        return label

    def styles(self, predicate):
        css, styles = [], []
        for s in self.objects(self.identifier, predicate):
            if s.datatype == FRESNEL["stylingInstructions"]:
                styles.append(s)
            elif s.datatype == FRESNEL["styleClass"]:
                css.append(s)
        return css, styles

    @property
    def propertyStyles(self):
        return self.styles(FRESNEL["propertyStyle"])
    @property
    def valueStyles(self):
        return self.styles(FRESNEL["valueStyle"])

class Fresnel(Graph):
    """
    .. automethod:: format
    """
    __types__ = []
    def __init__(self, *av, **kw):
        super(Fresnel, self).__init__(*av, **kw)
        self.lenses = {}
        self.classLenses = {}
        self.instanceLenses = {}
        self.groups = {}
        self._compiled = False

    def compile(self):
        if self._compiled:
            return
        self._compiled = True

        for l in self.distinct_subjects(RDF["type"], FRESNEL["Lens"]):
            lens = Lens(fresnel=self, identifier=l) 
            lens += self.bnc((l, None, None))
            self.lenses[l] = lens
            for cls in lens.objects(l, FRESNEL["classLensDomain"]):
                self.classLenses[cls] = lens
            for cls in lens.objects(l, FRESNEL["instanceLensDomain"]):
                self.instanceLenses[cls] = lens
            for grp in lens.objects(l, FRESNEL["group"]):
                group = self.groups.get(grp)
                if group is None:
                    group = Group(identifier=grp)
                    group += self.bnc((grp, None, None))
                    self.groups[grp] = group
                group.lenses[l] = lens
                lens.group = group

        for fmt in self.distinct_subjects(RDF["type"], FRESNEL["Format"]):
            format = Format(identifier=fmt)
            format += self.bnc((fmt, None, None))
            for grp in format.objects(fmt, FRESNEL["group"]):
                group = self.groups.get(grp)
                if group is None:
                    group = Group(identifier=grp)
                    group += self.bnc((grp, None, None))
                    self.groups[grp] = group
                for dom in format.objects(fmt, FRESNEL["propertyFormatDomain"]):
                    group.formats[dom] = format
                format.group = group

    def format(self, graph, resource=None):
        """
        Format the given graph according to this set of fresnel instructions.

        :return: tuple (stylesheet list, elementtree document)
        """
        self.compile()
        stylesheets = set()
        root = ET.Element("div")
        root.set("class", "fresnel_container")

        _x = self.one((self.identifier, ORDF["lensList"], None))
        if _x: lenses = Collection(self, _x[2])
        else: lenses = self.lenses

        for lens_uri in lenses:
            log.debug("Lens: %s" % lens_uri)
            lens = self.lenses.get(lens_uri)
            if lens is None:
                continue
            for typ in lens.distinct_objects(lens.identifier, FRESNEL["classLensDomain"]):
                log.debug("    Type: %s" % typ)
                resources = list(graph.triples((resource, RDF["type"], typ)))
                resources.sort(lambda x,y: cmp(x[0], y[0]))
                for s, _p, _o in resources:
                    styles, element = lens.formatResource(graph, s)
                    [stylesheets.add(x) for x in styles]
                    root.append(element)

        return stylesheets, root

from ordf.command import Command
class Render(Command):
    parser = Command.StandardParser(usage="%prog [options]")
    parser.add_option("-t", "--template", 
                      dest="template",
                      help="HTML Template")
    parser.add_option("-r", "--resource",
                      dest="resource",
                      help="Resource to format")
    default_template = """\
<html>
<body>
<fresnel />
</body>
</html>"""
    def command(self):
        template = self.default_template
        if self.options.template:
            template = open(self.options.template).read()
        template = ET.fromstring(template)

        fresnel_uri, graph_uri = self.args
        tmp = self.handler.get(fresnel_uri)
        fresnel = Fresnel(store=tmp.store, identifier=tmp.identifier)
        graph = self.handler.get(graph_uri)
        stylesheets, tree = fresnel.format(graph, URIRef(self.options.resource) if self.options.resource else None)

        head = template.find("head")
        if head is None:
            head = ET.Element("head")
            template.insert(0, head)
        for sheet in stylesheets:
            link = ET.Element("link")
            link.set("rel", "stylesheet")
            link.set("href", sheet)
            link.set("type", "text/css")
            head.append(link)
        meta = ET.Element("meta")
        meta.set("http-equiv", "Content-Type")
        meta.set("content", "text/html; charset=utf-8")
        head.append(meta)

        # guess at a good title for the document
        resource = URIRef(self.options.resource) if self.options.resource else graph.identifier
        title = None
        for label in DC["title"], FOAF["name"], RDFS["label"]:
            for title in graph.distinct_objects(resource, label):
                break
            if title is not None:
                break
        if title is None:
            title = resource
        tt = ET.Element("title")
        tt.text = title
        head.append(tt)

        def find_fresnel(parent):
            index = 0
            for child in parent:
#                if child.tag == "{http://www.w3.org/1999/xhtml}fresnel":
                if child.tag == "fresnel":
                    return parent, child, index
                next = find_fresnel(child)
                if next is not None:
                    return next
                index += 1
        parent, replace, index = find_fresnel(template)
        parent.remove(replace)
        parent.insert(index, tree)

        doc = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML+RDFa 1.0//EN" "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd">'
        doc += '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">'
        for child in template:
            doc += ET.tostring(child, encoding="utf-8")
        doc += '</html>'

        print doc

    #    from xml.dom import minidom
    #    from StringIO import StringIO
    #    doc = minidom.parse(StringIO(doc))
    #    print doc.toprettyxml()

def render():
    Render().command()
