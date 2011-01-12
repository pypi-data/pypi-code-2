from submission import DATA_ATTR_NAME
from gw20e.forms.interfaces import IForm


class ATCTBaseObject:

    """ Base class for ATCT. For your specific implementation,
    make sure to register an adapter for your type that provides
    an IForm instance.
    TODO: maybe we should cache the form?
    """

    def __init__(self):
        
        self.form = IForm(self)


    def render(self):

        action = "%s/@@save" % self.absolute_url()

        return self.form.view.render(self.form, action=action)


    def Title(self):

        """ Return title or id """

        return self.getFieldValue('title', self.getId())


    def getFieldValue(self, name, default=None, val=None, lexical=False, view=None):
        
        """ Get the data field value or default if lexical is
        something true-ish """

        if not lexical:
            try:
                val = val or self[DATA_ATTR_NAME][name]

                return self.form.model.convert(name, val)
            except:
                return None
        else:
            try:
                view = view or self.form.view
                val = val or self[DATA_ATTR_NAME][name] or default

                val = self.form.model.convert(name, val)
                
                return view.getRenderableByBind(name).lexVal(val)
            except:
                return default
