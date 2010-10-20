from Products.Archetypes.Widget import TypesWidget
from Products.Archetypes.Registry import registerWidget

from AccessControl import ClassSecurityInfo

class MultiFileWidget(TypesWidget):
    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro' : "widget_multifile",
        'show_content_type' : True,
        'helper_js' : ('multifile.js',),
        'helper_css' : ('multifile.css',),
        })

    security = ClassSecurityInfo()

    # XXX
    security.declarePublic('process_form')
    def process_form(self, instance, field, form, empty_marker=None,
                     emptyReturnsMarker=False):
        """form processing that deals with binary data"""
        value = None
        
        fileobjs = form.get('%s_f' % field.getName(), empty_marker)
        delobjs = form.get('%s_d' % field.getName(), False)

        args = {}
        if delobjs:
            args['DELETE'] = delobjs

        if fileobjs is empty_marker: return empty_marker

        if fileobjs:
            value = fileobjs

        if not value: return None

        return value, args

registerWidget(MultiFileWidget,
               title='Multiple File Widget',
               description=('Accepts multiple files.'),
               used_for=('archetypes.multifile.MultiFileField.MultipleFileField',)
               )
