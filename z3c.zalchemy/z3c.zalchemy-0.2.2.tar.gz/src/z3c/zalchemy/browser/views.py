
from zope.formlib import form
from z3c.zalchemy.interfaces import IAlchemyEngineUtility


class EditView(form.EditForm):
    form_fields = form.Fields(IAlchemyEngineUtility)

