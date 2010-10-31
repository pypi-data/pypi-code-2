from zope import interface
from z3c.form import form, field, button
from zope import schema
from plone.z3cform.layout import wrap_form
from collective.z3cform.colorpicker.colorpicker import ColorpickerFieldWidget
from collective.z3cform.colorpicker.colorpickeralpha import ColorpickerAlphaFieldWidget


class IColorForm(interface.Interface):
    color = schema.TextLine(title=u"Color",
                               description=u"",
                               required=False)

    alphacolor = schema.TextLine(title=u"Color with alpha layer support",
                               description=u"",
                               required=False)


class Color(object):
    color = '#ff0000'
    alphacolor = 'ff0000cc'

    def __init__(self, context):
        self.context = context


class BaseForm(form.Form):
    """ example color picker form """
    fields = field.Fields(IColorForm)
    fields['color'].widgetFactory = ColorpickerFieldWidget
    fields['alphacolor'].widgetFactory = ColorpickerAlphaFieldWidget

    @button.buttonAndHandler(u'Save')
    def handleApply(self, action):
        data, errors = self.extractData()
        return 

ColorForm = wrap_form(BaseForm)
