"""
.. autoclass:: Fresnel
   :show-inheritance:
"""

__all__ = ["Fresnel", "Lens"]

try:
    from xml.etree import ElementTree as ET
except ImportError:
    from elementtree import ElementTree as ET
from urllib import urlencode
from ordf.collection import Collection
from ordf.graph import Graph
from ordf.namespace import *
from ordf.term import Literal, URIRef, BNode
from datetime import datetime

class Lens(Graph):
    """
    """
    __types__ = [FRESNEL["Lens"]]
    def __init__(self, fresnel, identifier):
        super(Lens, self).__init__(identifier=identifier)
        self.fresnel = fresnel
        self.group = None
        self.__stylesheets__ = {}

    @property
    def stylesheets(self):
        return self.group.stylesheets + self.__stylesheets__.keys()

    def addStylesheet(self, sheet):
        self.__stylesheets__[sheet] = True

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
        elem = ET.Element("div")
        css = ["fresnel_resource"]

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
            prop = self.formatProperty(graph, lens, format, resource, property)
            if prop:
                elem.append(prop)
        elem.set("class", " ".join(css))
        return self.stylesheets, elem

    def formatProperty(self, graph, lens, format, resource, property):
        elem = ET.Element("div")

        css, styles = format.propertyStyles
        css = ["fresnel_property"] + css
        elem.set("class", " ".join(css))
        if styles: elem.set("style", " ".join(styles))

        label = format.label(property)
        if label is not None:
            span = ET.Element("span")
            span.set("class", "fresnel_label")
            span.text = label
            elem.append(span)

        values = [
            self.formatValue(graph, lens, format, resource, property, v)
            for v in graph.objects(resource, property)
        ]

        if values:
            container = ET.Element("div")
            container.set("class", "fresnel_container")
            [container.append(value) for value in values]
            elem.append(container)
            elem.set("class", " ".join(css))
            return elem

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

        if isinstance(value, Literal):
            p = ET.Element("span")

            if value.language:
                sp = ET.Element("span")
                sp.set("class", "fresnel_object_language")
                sp.text = u" (%s) " % value.language
                p.append(sp)
                self.rst(p, value)
            elif value.datatype:
                if value.datatype == XSD["dateTime"]:
                    try:
                        dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                        p.text = dt.ctime()
                    except:
                        p.text = value
                else:
                    p.text = value
            else:
                self.rst(p, value)
            elem.append(p)
        elif isinstance(value, URIRef) or isinstance(value, BNode):
            if lens:
                styles, rsrc = lens.formatResource(graph, value)
                [self.addStylesheet(x) for x in styles]
                elem.append(rsrc)
            else:
                if isinstance(value, URIRef):
                    if format.one((format.identifier, FRESNEL["value"], FRESNEL["image"])):
                        a = ET.Element("img")
                        a.set("src", value)
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
        return elem

class Group(Graph):
    __types__ = [FRESNEL["Group"]]

    def __init__(self, *av, **kw):
        super(Group, self).__init__(*av, **kw)
        self.lenses = {}
        self.formats = {}
    @property
    def stylesheets(self):
        stylesheets = list(self.distinct_objects(self.identifier, FRESNEL["stylesheetLink"]))
        return stylesheets

class Format(Graph):
    __types__ = [FRESNEL["Format"]]
    def __init__(self, *av, **kw):
        super(Format, self).__init__(*av, **kw)
        self.group = None
    def label(self, property):
        for _s, _p, label in self.triples((self.identifier, FRESNEL["label"], None)):
            if label == FRESNEL["none"]:
                return None
            else:
                return label
        label = property.rsplit("/", 1)[-1].rsplit("#", 1)[-1]
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

    def format(self, graph):
        """
        Format the given graph according to this set of fresnel instructions.

        :return: tuple (stylesheet list, elementtree document)
        """
        self.compile()
        stylesheets = {}
        root = ET.Element("div")
        root.set("class", "fresnel_container")

        _x = self.one((self.identifier, ORDF["lensList"], None))
        if _x: lenses = Collection(self, _x[2])
        else: lenses = self.lenses

        for lens_uri in lenses:
            lens = self.lenses.get(lens_uri)
            if lens is None:
                continue
            for typ in lens.distinct_objects(lens.identifier, FRESNEL["classLensDomain"]):
                resources = list(graph.distinct_subjects(RDF["type"], typ))
                resources.sort()
                for resource in resources:
                    styles, element = lens.formatResource(graph, resource)
                    [stylesheets.setdefault(x, None) for x in styles]
                    root.append(element)

        return stylesheets, ET.tostring(root, encoding="utf-8")
