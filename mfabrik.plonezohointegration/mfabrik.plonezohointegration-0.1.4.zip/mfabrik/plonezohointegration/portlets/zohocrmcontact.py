"""

    


"""

__copyright__ = "2010 mFabrik Research Oy"
__author__ = "Mikko Ohtamaa <mikko@mfabrik.com>"
__license__ = "GPL"
__docformat__ = "Epytext"

from zope.interface import Interface
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from mfabrik.plonezohointegration import _

from mfabrik.plonezohointegration.views import ZohoContactForm

class IZohoCRMContact(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # some_field = schema.TextLine(title=_(u"Some field"),
    #                              description=_(u"A field to use"),
    #                              required=True)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IZohoCRMContact)

    # TODO: Set default values for the configurable parameters here

    # some_field = u""

    # TODO: Add keyword parameters for configurable parameters here
    # def __init__(self, some_field=u"):
    #    self.some_field = some_field

    def __init__(self):
        pass

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _("Zoho Contact Form")


from plone.z3cform.layout import FormWrapper
class PortletFormView(FormWrapper):
     """ Form view which renders z3c.forms embedded in a portlet.
     
     Subclass FormWrapper so that we can use custom frame template. """
     
     index = ViewPageTemplateFile("portletform.pt")   
     
class Renderer(base.Renderer):
    """ z3c.form portlet renderer.

    Instiate form and wrap it to a special layout template 
    which will give the form suitable frame to be used in the portlet.
    
    We also set a form action attribute, so that 
    the browser goes to another page after the form has been submitted
    (we really don't know what kind of page the portlet is displayed
    and is it safe to submit forms there, so we do this to make sure).
    The action page points to a browser:page view where the same
    form is displayed as full-page form, giving the user to better
    user experience to fix validation errors.
    """

    render = ViewPageTemplateFile('zohocrmcontact.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self.form_wrapper = self.getForm()
        
    def getForm(self):
        """ Create a form instance. 
        
        @return: z3c.form wrapped for Plone 3 view
        """
        
        context = self.context.aq_inner
        
        returnURL = self.context.absolute_url()
        
        # Create a compact version of the contact form 
        # (not all fields visible)
        form = ZohoContactForm(context, self.request, returnURLHint=returnURL, full=True)
        
        # Wrap a form in Plone view
        view = PortletFormView(context, self.request)
        view = view.__of__(context) # Make sure acquisition chain is respected
        view.form_instance = form
        
        return view
    
    def getContactFormURL(self):
        """ For rendering the form link at the bottom of the portlet.
        
        @return: URL leading to the full contact form
        """
        return self.form_wrapper.form_instance.action
        

# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IZohoCRMContact)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IZohoCRMContact)
