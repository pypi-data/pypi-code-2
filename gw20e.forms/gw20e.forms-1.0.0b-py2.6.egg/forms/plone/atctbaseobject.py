class ATCTBaseObject:

    """ Base class for using gw20e.forms as editing front-end for your
    ATCT content. For your specific implementation, make sure to
    register an adapter for your type that provides an IForm instance.
    TODO: maybe we should cache the form?
    """

    def __init__(self, form):
        
        try:
            self.form.submission.retrieve(form, self)
        except:
            pass


    def render(self):

        action = "%s/@@save" % self.absolute_url()

        return self.form.view.render(self.form, action=action)


    def Title(self):

        """ Return title or id """

        return self.getFieldValue('title', self.getId())


    def setFieldValue(self, name, value):

        """ Set the field value, if the form actually holds that
        field. Else, ignore. """

        if self.form.data.has_key(name):
            self.form.data[name] = value


    def getFieldValue(self, name, default=None, val=None, lexical=False, view=None):
        
        """ Get the data field value or default if lexical is
        something true-ish """

        if not lexical:
            try:
                val = val or self.form.data[name]

                return self.form.model.convert(name, val)
            except:
                return None
        else:
            try:
                view = view or self.form.view
                val = val or self.form.data[name] or default

                val = self.form.model.convert(name, val)
                
                return view.getRenderableByBind(name).lexVal(val)
            except:
                return default
