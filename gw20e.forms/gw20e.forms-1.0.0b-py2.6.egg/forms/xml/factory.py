""" Factory class to generate forms from XML """

from lxml import etree
from gw20e.forms.formdata import FormData
from gw20e.forms.formview import FormView
from gw20e.forms.formmodel import FormModel
from gw20e.forms.form import Form
from gw20e.forms.data.field import Field
from gw20e.forms.model.fieldproperties import FieldProperties
from gw20e.forms.rendering.control import *
from gw20e.forms.rendering.group import *
from gw20e.forms.rendering.renderables import *
from gw20e.forms.submission.attrstorage import AttrStorage
from gw20e.forms.submission.none import NoSubmission
from gw20e.forms.submission.emailsubmission import EmailSubmission
from gw20e.forms.interfaces import IFormFactory
from formfile import FormFile
from zope.interface import implements
import os


SUBMISSION_TYPES = {'attrstorage': AttrStorage,
                    'email': EmailSubmission,
                    'none': NoSubmission}

RENDERING_TYPES = {
    'input': Input,
    'select': Select,
    'flowgroup': FlowGroup,
    'text': Text,
    'submit': Submit
}


class XMLFormFactory:

    """ The XMLFormFactory uses lxml to generate a form from an XML
    definition.
    """

    implements(IFormFactory)

    # Define specific element/class mappings here 
    controlClasses = {}


    def __init__(self, xml, **kwargs):

        self.xml = xml
        self.opts = kwargs


    def create_form(self, **opts):

        """ Create form based on XML
        TODO: make view type configurable
        """

        tree = None
        root = None

        # Try parsing as string first, then go for other options...
        try:
            root = etree.fromstring(self.xml)
        except:
            tree = etree.parse(self.xml)
            root = tree.getroot()

        data = self.create_data(root.find("data"))

        model = self.create_model(root.find("model"))

        view = self.create_view(root.find("view"))

        submission = self.create_submission(root.find("submission"))

        return Form(root.get("id"), data, model, view, submission)


    def create_data(self, root):

        """ Create FormData instance """

        data = FormData()

        for child in root.getchildren():

            field = Field(child.tag, child.get("value"))
            
            data.addField(field)

        return data


    def create_model(self, root):

        """ Create the form model. """

        model = FormModel()

        for child in root.getchildren():

            bind = []

            for elt in child.xpath("./bind"):
                bind.append(elt.text)

            kwargs = {}

            for elt in ["required", "relevant", "readonly", 
                        "calculate", "datatype", "constraint"]:
                if child.xpath("./%s" % elt):
                    kwargs[elt] = child.xpath("./%s" % elt)[0].text

            prop = FieldProperties(child.get("id"), bind, **kwargs)
            model.addFieldProperties(prop)

        return model


    def create_view(self, root):

        """ Create renderable part """

        view = FormView()

        for child in root.getchildren():
            
            self._create_renderables(child, view)

        return view


    def _create_renderables(self, child, view):

        cls = ""

        if XMLFormFactory.controlClasses.has_key(child.tag):
            cls = XMLFormFactory.controlClasses[child.tag]
        elif RENDERING_TYPES.has_key(child.tag):
            cls = RENDERING_TYPES[child.tag] 
        else:
            cls = eval(child.tag.capitalize())

        kwargs = {}

        for elt in child.xpath("./property"):
            kwargs[elt.get("name")] = elt.text

        for elt in ["hint", "help"]:
            if child.xpath("./%s" % elt):
                kwargs[elt] = child.xpath("./%s" % elt)[0].text

        if cls == Text:
            ctrl = cls(child.get("id"),
                       child.text,
                       **kwargs)

        elif cls == Submit:

            ctrl = cls(child.get("id"),
                       child.find("label").text,
                       **kwargs)
        elif cls == Group:
            cls = eval("%sGroup" % child.get("layout", "flow").capitalize())
            ctrl = cls(child.get("id"),
                       child.find("label").text,
                       **kwargs)                
        else:
            ctrl = cls(child.get("id"), child.get("bind"), 
                       child.find("label").text,
                       **kwargs)

        view.addRenderable(ctrl)

        for subchild in child.xpath("|".join(RENDERING_TYPES.keys())):

            self._create_renderables(subchild, ctrl)



    def create_submission(self, root):

        cls = SUBMISSION_TYPES.get(root.get("type"), None)

        if not cls:
            return None

        kwargs = {}
        
        for prop in root.getchildren():
            kwargs[prop.get("name")] = prop.text

        submission = cls(**kwargs)

        return submission
