from Acquisition import aq_chain
from zope.interface import implements
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope import schema
from five import grok
from plone.directives import form
from plone.directives import dexterity
from plone.app.dexterity.behaviors.metadata import IBasic
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from htmllaundry.z3cform import HtmlText
from euphorie.content.fti import ConditionalDexterityFTI
from euphorie.content.fti import IConstructionFilter
from euphorie.content.behaviour.richdescription import IRichDescription
from euphorie.content.interfaces import IQuestionContainer
from euphorie.content import MessageFactory as _
from euphorie.content.risk import IRisk
from euphorie.content.utils import StripMarkup
from plone.namedfile import field as filefield
from plonetheme.nuplone.skin.interfaces import NuPloneSkin
from plone.indexer import indexer

grok.templatedir("templates")

class IModule(form.Schema, IRichDescription, IBasic):
    """Survey Module.

    A module is (hierarchical) grouping in a survey.
    """

    description = HtmlText(
            title = _("label_module_description", u"Description"),
            description = _("help_module_description",
                default=u"Include any relevant information that may be "
                        u"helpful for users."),
            required = True)
    form.widget(description=WysiwygFieldWidget)
    form.order_after(description="title")

    optional = schema.Bool(
            title = _("label_module_optional", default=u"This module is optional"),
            description = _("help_module_optional",
                default=u"Allow users to skip this module and "
                        u"everything inside it."),
            required = False,
            default = False)

    question = schema.TextLine(
            title = _("label_module_question", default=u"Question"),
            description = _("help_module_question",
                default=u"The question to ask users if this module is "
                        u"optional. This has to be a yes/no question."),
            required = False)

    image = filefield.NamedBlobImage(
            title = _("label_image", default=u"Image"),
            required = False)

    solution_direction = HtmlText(
            title = _("label_solution_direction", default=u"Introduction action plan"),
            description = _("help_solution_direction", 
                default=u"This information will be shown to users when "
                        u"they enter this module while working on the "
                        u"action plan."),
            required = False)
    form.widget(solution_direction=WysiwygFieldWidget)



class Module(dexterity.Container):
    implements(IModule, IQuestionContainer)

    image = None



@indexer(IModule)
def SearchableTextIndexer(obj):
    return " ".join([obj.title,
                     StripMarkup(obj.problem_description),
                     StripMarkup(obj.question),
                     StripMarkup(obj.solution_direction)])



class View(grok.View):
    grok.context(IModule)
    grok.require("zope2.View")
    grok.layer(NuPloneSkin)
    grok.template("module_view")
    grok.name("nuplone-view")

    def _morph(self, child):
        state=getMultiAdapter((child, self.request), name="plone_context_state")
        return dict(id=child.id,
                    title=child.title,
                    url=state.view_url())

    def update(self):
        self.modules=[self._morph(child) for child in self.context.values()
                      if IModule.providedBy(child)]
        self.risks=[self._morph(child) for child in self.context.values()
                    if IRisk.providedBy(child)]




class ConstructionFilter(grok.MultiAdapter):
    """FTI construction filter for :py:class:`Module` objects. This filter
    does two things: it restricts the maximum depth at which a module can
    be created, and it prevents creating of modules if the current container
    already contains a risk.

    This multi adapter requires the use of the conditional FTI as implemented
    by :py:class:`euphorie.content.fti.ConditionalDexterityFTI`.
    """

    grok.adapts(ConditionalDexterityFTI, Interface)
    grok.implements(IConstructionFilter)
    grok.name("euphorie.module")

    maxdepth = 3

    def __init__(self, fti, container):
        self.fti=fti
        self.container=container

    def checkDepth(self):
        """Check if creating a new module would create a too deeply nested
        structure.
        """
        from euphorie.content.survey import ISurvey
        depth=1
        for position in aq_chain(self.container):
            if ISurvey.providedBy(position):
                break
            depth+=1
        else:
            return True

        return depth<=self.maxdepth


    def checkForRisks(self):
        """Check if the container already contains a risk. If so refuse to
        allow creation of a module.
        """
        for key in self.container:
            pt=self.container[key].portal_type
            if pt=="euphorie.risk":
                return False
        else:
            return True

    def allowed(self):
        return self.checkDepth() and self.checkForRisks()

