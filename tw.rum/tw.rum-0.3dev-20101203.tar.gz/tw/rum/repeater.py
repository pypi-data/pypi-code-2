# -*- coding: utf-8 -*-

import logging
from tw import forms
from tw.api import JSLink, js_function, lazystring as _, Link
from tw.dojo import dojo_js
log = logging.getLogger(__name__)

modname = 'tw.rum'




repeater_js = JSLink(
    modname = modname,
    filename = 'static/repeater.js',
    javascript=[dojo_js],
    )


class JSRepeater(forms.FormFieldRepeater):
    template = "genshi:tw.rum.templates.repeater"
    javascript = [repeater_js]
    repetitions = 1
    icons = {
        'cancel': Link(modname=modname, filename="static/cancel.png"),
        }
    params = ["add_text", "remove_text", "max_error_text", "error_class",
              "icons"]
    error_class = "fielderror"
    add_text = _("Add new")
    remove_text = _("Remove")
    max_error_text = _("Sorry, no more elements")

    def update_params(self, d):
        super(JSRepeater, self).update_params(d)
        log.debug("JSRepeater handling %r", d.value)
        first_id = self.children[0].id
        first_name = self.children[0].name
        #TODO: WidgetRepeater should update d.repetitions based on extra
        d.repetitions = max(d.repetitions, len(d.value) + d.extra)
        # remove trailing "-0" 
        d.add_link_id = first_id[:-2] + '_add_trigger'
        js_args = dict(
            add_link_id = d.add_link_id,
            first_id = first_id,
            first_name = first_name,
            max_repetitions = 1000,
            max_error_text = unicode(d.max_error_text),
            error_class = d.error_class,
            )
        if d.repetitions == 0:
            d.repetitions = 1
            js_args.update(clear_on_init=True)
        d.jscall = "dojo.addOnLoad(function() {"+\
            unicode(\
                js_function(\
                    "new JSRepeater")(\
                    js_args)) +"}); "
