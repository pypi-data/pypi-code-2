from xml.dom.minidom import parseString
from xml.dom.minidom import Document
from xml.parsers.expat import ExpatError
from collections import Mapping

from pywapa.AbstractParser import AbstractParser
from pywapa.AbstractParser import ParserError

class TwoDocumentElement(ParserError):
    pass

class XmlParser(AbstractParser):

    extensions = ['xml', 'text/xml', 'application/xml']
    '''
    extensions accepted by JsonParser : [xml, text/xml, application/xml]
    '''

    def parse(self, file_content):
        try:
            parsed = parseString(file_content)
        except ExpatError as e:
            raise ParserError(e.args)
        if parsed.firstChild.nodeName == 'configuration':
            rootNode = parsed.firstChild
        else:
            rootNode = parsed
        return self._xml_to_dic(rootNode)

    def dump(self, content):
        document = Document()
        if len(content) > 1:
            rootNode = document.createElement('configuration')
            document.appendChild(rootNode)
            for key in content.keys():
                for node in self._dic_to_xml(key, content[key]):
                    rootNode.appendChild(node)
        else:
            (uniqKey,) = content.keys()
            for node in self._dic_to_xml(uniqKey, content[uniqKey]):
                document.appendChild(node)
        return document.toprettyxml(indent="    ")

    def _xml_to_dic(self, node):
        dic = {}

        for child in node.childNodes:
            if child.nodeType == 1:
                child_child = child.childNodes[0]
                if child_child.nodeType == 3 and child_child.nodeValue.strip() != '':
                    value = str(child_child.nodeValue).strip(' \n')
                else:
                    value = self._xml_to_dic(child)

                if str(child.nodeName) in dic and not hasattr(dic[child.nodeName], '__setitem__'):
                    oldValue = dic[child.nodeName]
                    dic[child.nodeName] = []
                    dic[child.nodeName].append(oldValue)

                if str(child.nodeName) in dic:
                    dic[child.nodeName].append(value)
                else:
                    dic[str(child.nodeName)] = value
        return dic

    def _dic_to_xml(self, name, element):
        doc = Document()
        if isinstance(element, Mapping):
            node = doc.createElement(name)
            for key in element.keys():
                for nodes in self._dic_to_xml(key, element[key]):
                    node.appendChild(nodes)
        elif hasattr(element, '__setitem__'):
            nodes = []
            for value in element:
                for childNode in self._dic_to_xml(name, value):
                    nodes.append(childNode)
            return nodes
        else:
            node = doc.createElement(name)
            textNode = doc.createTextNode(str(element))
            node.appendChild(textNode)
        return [node]

