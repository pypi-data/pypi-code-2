import elementtree.ElementTree as ET

class ArborealExporter(object):
    
    def __init__(self, arboreal, path='arboreal.xml'):
        self.arboreal = arboreal
        self.path = path

    def _exportTreeMgrToXML(self, node, xml_node):
        """Helper method, to be called recursively on treemanager nodes """
        for (id, child) in node.objectItems():
            xml_sub_node = ET.SubElement(xml_node, 'arborealnode', id=id, title=child.Title())
            self._exportTreeMgrToXML(child, xml_sub_node)
        
    def exportToXML(self):
        """Exports the whole tree to xml. Encoding is Latin, because it seems that elementtree can only parse that format correctly."""

        root = ET.Element('arboreal')
        for id, tm in self.arboreal.objectItems():
            tm_node = ET.SubElement(root, 'treemanager', id=id, title=tm.Title())
            self._exportTreeMgrToXML(tm, tm_node)
        tree = ET.ElementTree(root)
        tree.write(self.path, encoding='utf-8')
        return '%s written' % self.path

class ArborealImporter(object):

    def __init__(self, arboreal, path='arboreal.xml'):
        self.arboreal = arboreal
        self.path = path


    def _importTreeMgrFromXML(self, xml_node, node, preserve_ids=True):
        """Helper method."""
        xml_sub_nodes = xml_node.findall('arborealnode')
        for xml_sub_node in xml_sub_nodes:
            id = preserve_ids and xml_sub_node.get('id') or None
            sub_node_id = node.addChild(xml_sub_node.get('title', u'no title'), id)
            sub_node = node[sub_node_id]
            self._importTreeMgrFromXML(xml_sub_node, sub_node, preserve_ids)

    def importFromXML(self, preserve_ids=True):
        """Import from xml file"""
        tree = ET.parse(self.path)
        root = tree.getroot()
        tm_nodes = root.findall('treemanager')
        for tm_node in tm_nodes:
            tm = self.arboreal.getTree(tm_node.get('id'))
            self._importTreeMgrFromXML(tm_node, tm, preserve_ids)
        return '%s imported' % self.path



