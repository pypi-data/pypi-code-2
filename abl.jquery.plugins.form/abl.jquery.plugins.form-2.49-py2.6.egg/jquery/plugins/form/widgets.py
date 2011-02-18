"""
abl.jquery.plugin.form widgets

"""

from tw.api import Widget, js_callback

from abl.jquery.core import jQuery
from abl.jquery.core.widgets import update_content_js
from abl.jquery.plugins.form.resources import (
    form_widget_js,
)


class AjaxFormMixin(Widget):
    """
    A mixin for a form to submit the data
    via Ajax.

    More info here:
    http://jquery.malsup.com/form
    """
    javascript = [form_widget_js]
    params = dict(config="""A dictionary that configures the jQuery form plugin.
                            Per default the response target (config['target'])
                            is the form element so the form gets replaced by the response.""")
    config = dict()
    default_config = dict()

    def update_params(self, d):
        super(AjaxFormMixin, self).update_params(d)
        config = self.default_config.copy()
        config.update(d.config)
        self.add_call(jQuery('#%s' % d.id).ajax_form(config))


class AjaxFormUpdateMixin(AjaxFormMixin):
    """
    Like AjaxFormMixin but instead of only updating itself
    it can update multiple containers on success
    """
    javascript = [form_widget_js,
                  update_content_js]
    params = dict(config="""A dictionary that configures the jQuery form plugin.
                            The success callback is update_content from
                            from abl.jquery.core.widgets.AjaxUpdateContentWidget.""")
    config = dict()
    default_config = dict(success=js_callback('submit_success'),
                          target=None)



