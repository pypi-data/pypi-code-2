# -*- coding: utf-8 -*-

import grokcore.view as grok
from zope.interface import Interface
from dolmen.widget.tinymce import JqueryTinyMCE
from zeam.form.ztk.widgets import text
from zeam.form.base.widgets import DisplayFieldWidget
from zeam.form.base.markers import ModeMarker

grok.templatedir('templates')

TINYMCE_INPUT = ModeMarker('TINYMCE.INPUT')
TINYMCE_DISPLAY = ModeMarker('TINYMCE.DISPLAY', extractable=False)


class TinyMCEWidget(text.TextFieldWidget):
    """A textarea widget with a tinyMCE editor.
    """
    grok.name(str(TINYMCE_INPUT))
    grok.template('input')
    grok.adapts(text.TextSchemaField, Interface, Interface)

    @property
    def script(self):
        JqueryTinyMCE.need()
        return """<script type="text/javascript">
          $(document).ready(function(){
          $('textarea[name="%s"]').tinymce();
        });
        </script>""" % self.identifier


class RichWidgetDisplay(DisplayFieldWidget):
    grok.name(str(TINYMCE_DISPLAY))
    grok.template('display')
    grok.adapts(text.TextSchemaField, Interface, Interface)
