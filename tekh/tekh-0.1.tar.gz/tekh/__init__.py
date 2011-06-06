from paste.util.template import paste_script_template_renderer
from pyramid.paster import PyramidTemplate

class TekhProjectTemplate(PyramidTemplate):
    _template_dir = 'tekh'
    summary = 'pyramid Tekh starter project'
    template_renderer = staticmethod(paste_script_template_renderer)