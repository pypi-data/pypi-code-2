from pyf.services.model import DBSession, Tube, Dispatch
from pyjon.utils.main import create_function

import tg
import logging

from operator import itemgetter

from tw.forms import (InputField, SingleSelectField,
                      TableForm, HiddenField, TableFieldSet,
                      CalendarDatePicker, FileField, CheckBox)

logger = logging.getLogger()

class Launcher(object):
    @property
    def variant_names(self):
        return self.tube.get_variant_names(show_inactive=False)

    def get_widgets(self, module):
        widgets = [self.get_single_widget(info)\
                   for info in\
                   sorted(self.tube.get_parameters().values(),
                          key=itemgetter('order'))]
        variant_names = self.variant_names
        if variant_names:
            widgets.insert(0, SingleSelectField('variant',
                                options=[('no_variant', '--')] + variant_names))

        widgets.append(HiddenField('%s_id' % module, default=getattr(self, '%s_id' % module)))

        return widgets

    def get_single_widget(self, info):
        widget_type = info.get('type', 'input')

        if widget_type == "input":
            return self.get_input_widget(info)

        elif widget_type == "date":
            return self.get_date_widget(info)

        elif widget_type == "input_range":
            return self.get_input_range_widget(info)

        elif widget_type == "date_range":
            return self.get_date_range_widget(info)

        elif widget_type == "boolean":
            return self.get_boolean_widget(info)

        else:
            logger.warning('Widget type %s not supported' % widget_type)
            if widget_type.endswith('_range'):
                return self.get_input_range_widget(info)

            return self.get_input_widget(info)

    def get_default_widget_info(self, widget_info):
        return dict(label_text=widget_info.get('name'),
                    help_text=widget_info.get('description'),
                    default=widget_info.get('default'))

    def get_input_widget(self, widget_info, widget=None):
        if widget is None:
            widget = InputField

        return widget(widget_info.get('key'),
                      **self.get_default_widget_info(widget_info))

    def get_input_range_widget(self, widget_info, widget=None):
        if widget is None:
            widget = InputField

        from_widget = widget(widget_info.get('from_key'),
                             label_text=widget_info.get('from_label',
                                                        'From'),
                             default=widget_info.get('from_default'),
                             attrs={'name': widget_info.get('from_key')})

        to_widget = widget(widget_info.get('to_key'),
                           label_text=widget_info.get('to_label',
                                                      'To'),
                           default=widget_info.get('to_default'),
                           attrs={'name': widget_info.get('to_key')})

        return TableFieldSet(widget_info.get('key'),
                             label_text='',
                             legend=widget_info.get('name'),
                             help_text=widget_info.get('description'),
                             children=[from_widget, to_widget])

    def get_date_widget(self, widget_info):
        widget_callable = create_function(
                            CalendarDatePicker,
                            caller_args_count=1,
                            kwargs=dict(date_format=widget_info.get('format')))

        return self.get_input_widget(widget_info,
                                     widget=widget_callable)

    def get_date_range_widget(self, widget_info):
        widget_callable = create_function(
                            CalendarDatePicker,
                            caller_args_count=1,
                            kwargs=dict(date_format=widget_info.get('format')))

        return self.get_input_range_widget(widget_info,
                                           widget=widget_callable)

    def get_boolean_widget(self, widget_info, widget=None):
        if widget is None:
            widget = CheckBox

        return widget(widget_info.get('key'),
                      **self.get_default_widget_info(widget_info))


class DispatchLauncher(Launcher):
    module = 'dispatch'

    def __init__(self, dispatch_id):
        self.dispatch_id = dispatch_id
        self.form = self.get_form()

    @property
    def dispatch(self):
        return DBSession.query(Dispatch).get(self.dispatch_id)

    @property
    def tube(self):
        return self.dispatch.tube

    def get_widgets(self, module):
        widgets = super(DispatchLauncher, self).get_widgets(module)

        # dispatch are not tubes: they need a source file and its encoding
        encoding_info = dict(
                key="encoding",
                name="Encoding:",
                description="The source file encoding",
                default=self.dispatch.descriptor.default_encoding,
                )
        source_file_info = dict(
                key="doc",
                name="File:",
                description="",
                )

        widgets.append(self.get_input_widget(encoding_info))
        widgets.append(self.get_input_widget(source_file_info, widget=FileField))

        return widgets

    def get_form(self):
        return TableForm('launch_dispatch_%s' % self.dispatch.name,
                        action=tg.url('/dispatchs/upload'),
                        children=self.get_widgets(self.module))

class TubeLauncher(Launcher):
    module = 'tube'

    def __init__(self, tube_id):
        self.tube_id = tube_id
        self.form = self.get_form()

    @property
    def tube(self):
        return DBSession.query(Tube).get(self.tube_id)

    def get_widgets(self, module):
        widgets = super(TubeLauncher, self).get_widgets(module)

        return widgets

    def get_form(self):
        return TableForm('launch_tube_%s' % self.tube.name,
                        action=tg.url('/tubes/launch'),
                        children=self.get_widgets(self.module))

