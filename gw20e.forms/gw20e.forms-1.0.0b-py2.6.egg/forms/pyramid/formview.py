from gw20e.forms.form import FormValidationError
from gw20e.forms.rendering.control import File
from gw20e.forms.xml.factory import XMLFormFactory
from gw20e.forms.xml.factory import FormFile


class PyramidFile(File):
    
    """ File upload control """

    def __init__(self, *args, **kwargs):

        File.__init__(self, *args, **kwargs)
        self.type = "file"


    def processInput(self, data={}):

        """ File data is stored in value field """

        try:
            file = data[self.id]
            return file.value
        except:
            return ""


    def lexVal(self, value):

        return ""


class formview(object):
    
    """ Pyramid form view """
    
    def __init__(self, context, request, form):
    
        self.context = context
        self.request = request
        self.form = form

        try:
            data = self.form.submission.retrieve(form, context)
            self.form.data = data
        except:
            pass


    def renderform(self):
        
        """ Render the form.
        """

        return self.form.view.render(self.form)


    def __call__(self):

        errors = {}
        status = ''
        form = self.form

        if self.request.params.get("formprocess", None):

            self._process_data(form, form.view, self.request.params)
            status = 'processed'

            try:
                form.validate()
                form.submission.submit(form, self.context, self.request)
                status = 'stored'
            except FormValidationError, fve:
                errors = fve.errors
                status = 'error'

        return {'errors': errors, 'status': status}


    def _process_data(self, form, view, data={}):
        
        """ Get data form request and see what we can post...
        """

        for renderable in view.getRenderables():

            try:
                fld = form.data.getField(renderable.bind)
                val = renderable.processInput(data)
                fld.value = form.model.convert(renderable.bind, val)

            except:
                pass

            if hasattr(renderable, "getRenderables"):
                self._process_data(form, renderable, data)


class xmlformview(formview):

    """ View class taking an XML path as argument to create the form """

    def __init__(self, context, request, formfile):
        

        xmlff = XMLFormFactory(formfile.filename)
                
        form = xmlff.create_form(action="")

        formview.__init__(self, context, request, form)
