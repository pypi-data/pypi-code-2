from zope.component import createObject
from zope.formlib import form

from plone.app.form import base
from plone.app.form.widgets.uberselectionwidget import UberMultiSelectionWidget

from Acquisition import aq_inner

from borg.project.interfaces import IProject
from borg.project import ProjectMessageFactory as _

from borg.project.utils import default_addable_types
        
project_form_fields = form.Fields(IProject)
project_form_fields['managers'].custom_widget = UberMultiSelectionWidget
project_form_fields['members'].custom_widget = UberMultiSelectionWidget
project_form_fields['groups'].custom_widget = UberMultiSelectionWidget
        
class ProjectAddForm(base.AddForm):
    """Add form for projects
    """
    
    form_fields = project_form_fields
    
    label = _(u"Add Project")
    form_name = _(u"Project settings")
    
    def setUpWidgets(self, ignore_request=False):
        default_addable = default_addable_types(aq_inner(self.context))
        
        self.widgets = form.setUpWidgets(
            self.form_fields, self.prefix, self.context, self.request,
            data=dict(addable_types=default_addable),
            ignore_request=ignore_request)
    
    def create(self, data):
        project = createObject(u"borg.project.Project")
        form.applyChanges(project, self.form_fields, data)
        return project
    
class ProjectEditForm(base.EditForm):
    """Edit form for projects
    """
    
    form_fields = project_form_fields
    
    label = _(u"Edit Project")
    form_name = _(u"Project settings")
