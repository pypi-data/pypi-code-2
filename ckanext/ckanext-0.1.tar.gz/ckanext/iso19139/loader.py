from ckanclient.loaders.base import CkanLoader
from ckanext.iso19139.reader import Iso19139Reader

class Iso19139Loader(CkanLoader):
    """
    Obtains CKAN packages from an ISO 19139 source.
    """

    def __init__(self):
        """Sets up an ISO 19139 source reader."""
        super(Iso19139Loader, self).__init__()
        self.reader = Iso19139Reader(self.options)

    def add_options(self, parser):
        """Adds options for accessing ISO 19139 source."""
        super(Iso19139Loader, self).add_options(parser)
        parser.add_option(
            '--source-location',
            dest='source_location',
            help="""The URI of the source data.""")
        parser.add_option(
            '--style-location',
            dest='style_location',
            help="""The URI of the stylesheet.""")

    def obtain_packages(self):
        rdf_str = self.reader.read_as_rdf()
        print rdf_str
        import libxml2
        dom = libxml2.parseDoc(rdf_str)
        root = dom.getRootElement()
        for data_set in self.get_elements_by_tag_name(root, 'DataSet'):
            self.handle_data_set(data_set)
        dom.freeDoc()

    def get_element_by_tag_name(self, elem, name):
        elems = self.get_elements_by_tag_name(elem, name)
        if elems:
            return elems[0]
        else:
            return None

    def get_elements_by_tag_name(self, elem, name):
        elements = []
        child = elem.children
        while child is not None:
            if child.name == name:
                elements.append(child)
            child = child.next
        return elements

    def handle_data_set(self, data_set):
        # Package title.
        title = self.get_element_by_tag_name(data_set, 'title').content
        # Package name.
        import string
        name = title.translate(string.maketrans("",""), string.punctuation + string.whitespace)
        # Package notes.
        notes = self.get_element_by_tag_name(data_set, 'abstract').content
        # Package maintainer.
        contact = self.get_element_by_tag_name(data_set, 'contact')
        person = self.get_element_by_tag_name(contact, 'Person')
        if person:
            maintainer = self.get_element_by_tag_name(person, 'name').content
            # Package maintainer email.
            maintainer_email = self.get_element_by_tag_name(person, 'mbox').content
        organisation = self.get_element_by_tag_name(contact, 'Organisation')
        if organisation:
            maintainer = self.get_element_by_tag_name(organisation, 'name').content
            # Package maintainer email.
            maintainer_email = self.get_element_by_tag_name(organisation, 'mbox').content

        # Package extras.
        spatial = self.get_element_by_tag_name(data_set, 'spatial').content
        extras = {'spatial': spatial}
        # Package tags.
        tags = ['ordnance-survey', 'test']
        # Package license.
        license_id = 'ukcrown-withrights'
        package = self.create_package(name=name, title=title, notes=notes, maintainer=maintainer, maintainer_email=maintainer_email, author=maintainer, author_email=maintainer_email, extras=extras, tags=tags, license_id=license_id)
        self.packages.append(package)

