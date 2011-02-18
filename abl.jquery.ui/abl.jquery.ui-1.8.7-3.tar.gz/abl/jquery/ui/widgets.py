# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from simplejson import dumps

from tw.api import (
    JSLink,
    js_callback,
    js_function,
    Widget)
from tw.forms import TextField


from abl.jquery.core import (
    jQuery,
    jquery_js)
from abl.utils.odict import OrderedDict
from abl.jquery.core.widgets import update_content_js
from abl.jquery.ui import (
    ui_autocomplete_js,
    ui_autocomplete_callbacks_js,
    ui_tabs_js,
    ui_dialog_js,
    effects_core_js)
from abl.jquery.plugins.form import form_widget_js


class JQueryUITabs(Widget):
    """
    A widget which displays a number of tabs, each of which can be a
    widget on its own. Additionally, one more widget can be given,
    which will be displayed on each tab.

    Note: There might be problems using a widget id here when using
          Ajax features because the children ids are composed with
          the parent id. On an Ajax request the child widget may
          called without tabs and this will change the client id
          Therefore the tabs_id is used here.
          So you can still give the widget an id but its not used
          in the HTML presentation.

    Usage:
    from tw.forms import TextField #use your widget here instead
    from abl.jquery.ui.widgets import JQueryUITabs

    w1 = TextField('example_1')
    w2 = TextField('example_2')
    dw = TextField('default')

    tabs_widget = JQueryUITabs('tabs',
                               tabs_id="example_tabs",
                               children=[w1, w2],
                               title_list=['first tab', 'last tab'],
                               default_field=dw)

    tabs_widget.display(dict(value_list=['hello', 'world'],
                             default_field_data='jQuery says:'))
    """

    engine_name = "genshi"
    template = "abl.jquery.ui.templates.jquery_ui_tabs"
    javascript = [ui_tabs_js]
    params = dict(tabs_id = "HTML id of the tabs container. Default is 'tabs'",
                  title_list = "To give each widget a tab name. If not given or incomplete, the tabs named 'Tab <index>'",
                  default_field = "A optional widget which is displayed on all tabs.",
                  tabs_options = "A dictionary with extra option for jQuery tabs. See http://docs.jquery.com/UI/Tabs")
    tabs_id = "tabs"
    tabs_options = dict()
    default_field = None
    title_list = []


    def update_params(self, d):
        super(JQueryUITabs, self).update_params(d)
        tabs_id = d.tabs_id = self.tabs_id
        d.value_list = d.value["value_list"]
        d.default_field_data = d.value.get("default_field_data")
        if len(self.title_list) == len(self.children):
            d.title_list = self.title_list
        else:
            d.title_list = []
            title_list_len = len(self.title_list)
            for i in range(len(self.children)):
                if title_list_len > i:
                    d.title_list.append(self.title_list[i])
                else:
                    d.title_list.append('Tab %i' % i)

        self.add_call(jQuery("#%s" % d.tabs_id).tabs(self.tabs_options))


ui_dialog_content_js = JSLink(modname=__name__,
                              filename='static/javascript/ui.dialog.content.js',
                              javascript=[ui_dialog_js, effects_core_js])


class DialogContentWidget(Widget):
    """
    A widget that opens a dialog and displays
    content, like HTML or plain text, that is loaded
    from a given url.

    You have to create a clickable HTML element with a class
    of the same name like the widgets id. This element
    can have a href or/and title attribute. Otherwise
    the url can be passed to the widget directly and the
    title can be a key of the config.

    There are two ways how to use the widget:
    1. Widget defines url and/or title
    >>> my_dialog = DialogContentWidget('my_dialog',
                                        url='/path/to/content',
                                        title='foo bar')
    in the Template
    >>> <p class="my_dialog">click here to open the dialog</p>

    2. Link defines url and/or title
    >>> another_dialog = DialogContentWidget('another_dialog')
    in the Template
    >>> <a href="/path/to/content"
           title="foo bar"
           class="another_dialog">click here to open the dialog</a>

    In both cases there can be more then one link that uses the class.
    And if the Link defines the url and/or title the dialog widget
    can be reused for several situations.

    For config options see:
    http://docs.jquery.com/UI/Dialog
    """
    javascript = [ui_dialog_content_js,]
    params = dict(url="optional content url",
                  title="The header of the dialog, optional",
                  config="Configuration of the dialog, optional",)
    url = ''
    title = ''
    config = dict()
    default_config = dict(width=426,
                          resizable=False,
                          position=['center', 70])


    def update_params(self, d):
        super(DialogContentWidget, self).update_params(d)
        self.perform_call(d)


    @classmethod
    def _get_ordered_config(cls, config):
        """A helper function that returns the config as a string.
           We need this here to protect the order in the buttons dict
           Reason: simplejson does not care about the order, so this
           is basically a dirty replacement simplejson.dumps(config)
        """
        entries = []
        for key, value in config.iteritems():
            # this we need for lazystrings in pylons.i18n
            skey = dumps(key, default=lambda v: unicode(v))
            if key == 'buttons':
                value = cls._get_ordered_config(value)
            else:
                if isinstance(value, js_callback):
                    value = unicode(value)
                else:
                    # when simplejson bails out, try &
                    # simply use the unicode-value
                    try:
                        value = dumps(value)
                    except TypeError:
                        value = unicode(value)
                        value = dumps(value)

            entries.append(u"%s:%s" % (skey, value))
        return u"{%s}" % (u", ".join(entries))


    def perform_call(self, d):
        """
        Adds the jQuery call. A subclass should override this.
        """
        config = self.default_config.copy()
        config.update(d.config)
        if d.url:
            config['url'] = d.url
        if d.title:
            config['title'] = d.title
        #Typically we would do the following
        #self.add_call(jQuery(".%s" % d.id).dialog_content(config))
        #but this brakes the order of the button dict, if set
        #Therefore this call is little dirty.
        config = self._get_ordered_config(config)
        self.add_call("""
            $('.%s').dialog_content(%s)
        """ % (d.id, config))


ui_dialog_confirm_js = JSLink(modname=__name__,
                              filename='static/javascript/ui.dialog.confirm.js',
                              javascript=[ui_dialog_content_js,])


class DialogConfirmWidget(DialogContentWidget):
    """
    A specialized version of the DialogContentWidget that can
    perform an action after the user pressed the OK button.

    You can optionally define the buttons and there callback function.
    You also can provide your own config for buttons in the config
    dictionary.
    """
    javascript = [ui_dialog_confirm_js,]
    params = dict(action_url="URL that will be called when the user confirms. Its only used if confirm_callback is not defined.",
                  cancel_callback="optional define a js_callback. default closes the dialog",
                  cancel_button="Name of the Cancel button, default is Cancel",
                  confirm_callback="Optional define a js_callback. Default makes a 'window.location.href = action_url'",
                  confirm_button="Name of the confirm button, default is Ok")
    action_url = ''
    cancel_callback = js_callback("close")
    confirm_callback = ''
    cancel_button = "Cancel"
    confirm_button = "Ok"
    default_config = dict(modal=True,
                          width=426,
                          resizable=False,
                          position=['center', 70])


    def update_params(self, d):
        super(DialogConfirmWidget, self).update_params(d)


    def perform_call(self, d):
        if not d.config.has_key('buttons'):
            #using an ordered dict here to save the button order
            buttons=OrderedDict()
            if d.confirm_callback:
                buttons[d.confirm_button] = d.confirm_callback
            else:
                buttons[d.confirm_button] = js_callback(
                    "function() {abljqui_confirm('%s');}" % d.action_url)
            buttons[d.cancel_button] = d.cancel_callback
            d.config['buttons'] = buttons

        super(DialogConfirmWidget, self).perform_call(d)


ui_dialog_form_js = JSLink(modname=__name__,
                           filename='static/javascript/ui.dialog.form.js',
                           javascript=[form_widget_js,
                                       ui_dialog_content_js,
                                       update_content_js])


class DialogFormWidget(DialogContentWidget):
    """
    A specialized version of the DialogContentWidget
    that can load a page that contains a form. This
    form will be submited using jquery.form.js

    The default submit callback function can replace some
    content of a website like the
    abl.jquery.widgets.AjaxUpdateContentWidget
    But if the returning html is not like
    <div id="update_container">...</div>
    the dialog content will be replaced instead.
    This is typically the case if the form is returned
    and is displaying some errors.
    """

    javascript = [ui_dialog_form_js,]
    params = dict(cancel_callback="optional define a js_callback. default closes the dialog",
                  cancel_button="Name of the Cancel button, default is Cancel",
                  submit_callback="Optional define a js_callback. Default makes an ajax submit",
                  submit_button="Name of the confirm button, default is Submit")
    cancel_callback = js_callback("close")
    submit_callback = js_callback("submit")
    cancel_button = "Cancel"
    submit_button = "Submit"
    default_config = dict(modal=True,
                          width=426,
                          resizable=False,
                          position=['center', 70])


    def update_params(self, d):
        super(DialogFormWidget, self).update_params(d)


    def perform_call(self, d):
        if not d.config.has_key('buttons'):
            #using an ordered dict here to save the button order
            d.config['buttons'] = OrderedDict([(d.submit_button, d.submit_callback),
                                               (d.cancel_button, d.cancel_callback)])

        super(DialogFormWidget, self).perform_call(d)

MINLENGTH=3,
DELAY=1,
POSITION=dict(my="left top",
              at="left bottom",
              collision="none",
              offset="0, -1px;")

class AutoCompleteTextField(TextField):
    """
    Displays a autocomplete search result chooser under a text field.

    If it should work with a remote URL, pass the URL as options[source]
    The search term is requested as the param 'term'

    http://docs.jquery.com/UI/Autocomplete
    """

    params = dict(options="""A dictionary with options.""",
                  submit_on_select="""Auto-submit if a suggestion was selected by click or enter-key, Default is True""")
    submit_on_select = True
    options = dict()
    default_options = dict(source=[],
                           minLength=MINLENGTH,
                           position=POSITION,
                           delay=DELAY)
    javascript=[ui_autocomplete_js,
                ui_autocomplete_callbacks_js]

    select_callback=js_callback("autocomplete_select_callback")
    submit_on_enter_callback = js_callback("autocomplete_submit_on_enter_callback")


    def update_params(self, d):
        super(AutoCompleteTextField, self).update_params(d)

        if d.submit_on_select:
            self.default_options['select'] = self.select_callback
        options = self.default_options.copy()
        options.update(d.options)

        if d.submit_on_select:
            self.add_call(jQuery('#%s' % self.id).autocomplete(options).live('keydown', self.submit_on_enter_callback))
        else:
            self.add_call(jQuery('#%s' % self.id).autocomplete(options))


class InstantSearchTextField(AutoCompleteTextField):
    """
    Displays autocomplete suggestion and instant search results.
    """
    params = dict(options="""A dictionary with options.""",
                  instant_url="""The URL that retrieves both, suggestions and instant results. Default is ''""")
    instant_url=''
    source_callback=js_callback("autocomplete_source_callback")
    open_callback=js_callback("autocomplete_open_callback")
    close_callback=js_callback("autocomplete_close_callback")
    select_callback=js_callback("autocomplete_instantsearch_select_callback")
    default_options = dict(source=source_callback,
                           open=open_callback,
                           close=close_callback,
                           select=select_callback,
                           minLength=MINLENGTH,
                           position=POSITION,
                           delay=DELAY,
                           instant_url=instant_url)


    def update_params(self, d):
        super(AutoCompleteTextField, self).update_params(d)
        options = self.default_options.copy()
        options.update(d.options)
        self.add_call(jQuery('#%s' % self.id).autocomplete(options))



class MultipleValuesAutocompleteTextField(AutoCompleteTextField):
    """
    Displays multiple autocomplete suggestions.
    """

    params = dict(options="""A dictionary with options.""",
                  suggestion_list="""A list of strings used for local autocompletion""",
                  max_results="""The maximum amount of results displayed as suggestion. Works only or a suggestion_list not for remote suggestion. Default is 5""")
    options = dict()
    suggestion_list = None
    max_results = 5
    select_callback = js_callback("select_multiple_callback")
    focus_callback = js_callback("focus_multiple_callback")
    multiple_autocomplete_keydown_callback = js_callback("multiple_autocomplete_keydown_callback")
    default_options = dict(minLength=1,
                           position=POSITION,
                           delay=DELAY,
                           select=select_callback,
                           focus=focus_callback)


    def update_params(self, d):
        super(AutoCompleteTextField, self).update_params(d)
        if d.suggestion_list and not self.options.has_key('source'):
            self.default_options['source'] = js_callback(
                 """function(request, response) {
                      response($.ui.autocomplete.filter(%s,
                                                        multiple_autocomplete_extract_last(request.term)).slice(0, %i));
                    }""" % (dumps(d.suggestion_list),
                            d.max_results))

        options = self.default_options.copy()
        options.update(d.options)
        self.add_call(jQuery('#%s' % self.id).bind('keydown', self.multiple_autocomplete_keydown_callback).autocomplete(options))
