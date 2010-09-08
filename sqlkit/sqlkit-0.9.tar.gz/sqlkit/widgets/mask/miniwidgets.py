# Copyright (C) 2008-2010, Sandro Dentella <sandro@e-den.it>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Gtk Widgets
===========

widgets to be used by fields to display values and edit 
widgets only interpret gtk, while fields teat with real values and do validation

Colors
------

You can change default color for not nullable object globally:

  from sqlkit.widgets.mask import miniwidgets
  miniwidgets.NOT_NULL_COLOR = gtk.gdk.color_parse('green')

You can change the foreground of unsensitive widgets setting NOT_EDITABLE_COLOR

"""

import re
from decimal import Decimal
from datetime import timedelta, time

import gtk
import gobject

from sqlkit import debug as  dbg, _, exc
from sqlkit.widgets.common.completion import SimpleCompletion, FkeyCompletion

NOT_NULL_COLOR = gtk.gdk.color_parse('#f6ebba')
NOT_EDITABLE_COLOR = gtk.gdk.color_parse('#333')


class Widget(object):
    def __init__(self, gtkwidget, field):
        self.gtkwidget = gtkwidget
        self.field = field
        self.master = field.master
        self.field_name = field.field_name

        if not self.field.nullable:
            self.set_not_null_style(not self.field.nullable)
        self.gtkwidget.connect('destroy', self.destroy)
        self.set_editable(self.field.editable)

        self.set_text(state=gtk.STATE_INSENSITIVE, color=gtk.gdk.color_parse('#333'))

    def set_not_null_style(self, value):
        if value:
            if self.field.editable:
                self.set_bg(state=gtk.STATE_NORMAL, color=NOT_NULL_COLOR)
        else:
            style = gtk.Entry().get_style()
            color = style.base[gtk.STATE_NORMAL]
            self.set_bg(state=gtk.STATE_NORMAL, color=color)

    def set_bg(self, state, color):
        self.gtkwidget.modify_base(state, color)
        
    def set_text(self, state, color):
        self.gtkwidget.modify_text(state, color)
        
    def set_value(self, value, shown=False):
        """if shown is True, the displayed value is returned also in any
        case. The difference is only for ForeignKey
        The displayed value may be used for completion purpouses
        """
        pass

    def get_value(self):
        pass

    def get_entry(self):
        """
        return the entry on which you want to apply completion for this object
        """
        return self.gtkwidget

    def destroy(self, widget=None):
        for attr in ('field', 'master', 'completion',):
            try:
                delattr(self, attr)
            except AttributeError:
                pass

    def set_editable(self, editable):
        """
        set the widget editability
        if the fields is not editable, the widget cannot be editable
        """
        editable = self.field.editable and editable
        self.gtkwidget.set_property('sensitive', editable) 
        
    def __repr__(self):
        return "< %s - %s >" % (self.__class__.__name__, self.field_name)

class VarcharWidget(Widget):
    #  to prevent to change NULL to '' and viceversa
    #  we store the value when setting it 
    #  and compare it when getting

    def __init__(self, *args):

        Widget.__init__(self, *args)
        self.add_completion()
        self.gtkwidget.connect('key-press-event', self.on_key_press)
        
        if self.field.length:
            self.set_max_length(self.field.length)
 
    def on_key_press(self, widget, event):
        ksym = gtk.gdk.keyval_name(event.keyval)
        
        if not ksym == 'Return':
            return
        
        if event.state & (gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK):
            return

        self.master.run_hook('on_activate', self, field_name=self.field_name)

    def add_completion(self):
        """add completion bindings and liststore
        """
        self.completion = SimpleCompletion(self.master, self, self.field_name)
        self.completion.add_completion(self.gtkwidget)
        self.master.completions[self.field_name] = self.completion
        self.completion.add_callbacks(self.gtkwidget)

    def set_value(self, value):
        # Entry
        self.gtkwidget.set_text( str(value) )
        
    def get_value(self, shown=False):
        value = self.gtkwidget.get_text( )
        ## don't change from None to '' 
        return value

    def set_max_length(self, length=None):

        if length is None:
            length = self.field.length
        self.gtkwidget.set_max_length(length)
        
class ReadOnlyWidget(Widget):

    def __init__(self, *args):

        Widget.__init__(self, *args)
        self.gtkwidget.set_property('xpad', 0)
        self.gtkwidget.set_property('sensitive', True) 
        self.gtkwidget.set_property('selectable', True) 
        if self.master.is_fkey(self.field_name):
            self.completion = FkeyCompletion(self.master, self, self.field_name)
        else:
            self.completion = None

    def set_value(self, value, shown=True):

        self.gtkwidget.set_data('value', value)
        string_value = self.field.get_human_value(value)
#         if self.completion:
#             string_value = self.completion.lookup_value(value)
#         else:
#             string_value = str(self.field.format_value(value)) or ''

        self.set_label(string_value)

    def set_label(self, value):
        """
        this is meant to be overloaded for particular needs
        """
        self.gtkwidget.set_text(value or '')

    def get_value(self, shown=False):

        return self.field.initial_value

    def set_max_length(self, max):
        pass
    
class IntegerWidget(VarcharWidget):

    def __init__(self, *args):
        Widget.__init__(self, *args)
        self.gtkwidget.set_alignment(1)
        self.gtkwidget.connect('key-press-event', self.on_key_press)
        self.gtkwidget.connect('key-press-event', self.master.digits_check_input_cb  )
                
    def set_value(self, value):
        self.text_value = self.field.format_value(value)
        self.gtkwidget.set_text(self.text_value)
        
    def get_value(self, shown=False):
        text = self.gtkwidget.get_text( )
        return self.field.clean_value(text)

class FloatWidget(IntegerWidget):
    
    def get_value(self, shown=False):
        ## the representation of a float normally trims it, so, if I know I have not changed
        ## anything I return the old value

        text = self.gtkwidget.get_text( )

        if self.text_value == text:
            return self.field.initial_value

        return self.field.clean_value(text)

class DecimalWidget(IntegerWidget):
    pass

class DateWidget(Widget):

    def __init__(self, *args):
        Widget.__init__(self, *args)
        self.gtkwidget.connect('date-changed', self.date_changed_cb, )

    def wrong_format_cb(self, widget, date_string):
        self.invalid = date_string

    def date_changed_cb(self, widget):
        self.invalid = None

    def set_value(self, value):

        self.invalid = None
        self.gtkwidget.set_property('date', value)

    def get_value(self, shown=False):

        value = self.gtkwidget.get_property('date')
        if isinstance(value, basestring):
            raise exc.ValidationError(_("Wrong date format: %s") % value)
        else:
            return value

class TimeWidget(Widget):

    def set_value(self, value):
        self.gtkwidget.set_text(self.field.format_value(value))

    def get_value(self, shown=False):
        
        value = self.gtkwidget.get_text() 

        if not value:
            return None
        value = time(*[int(i) for i in re.split('[.:]', value)]) 
        return self.field.clean_value(value)

class TimeTZWidget(Widget):
    pass

class IntervalWidget(Widget):

    def set_value(self, value):
        if value and not isinstance(value, timedelta):
            msg = "value for %s must be a timedelta (now: %s)" % (self.field_name, value)
            raise AttributeError(msg)
        self.gtkwidget.set_property('interval', value)

    def get_value(self, shown=False):
        ## if all values are 0 and initial value is None, return None

        value = self.gtkwidget.get_property('interval') 
        if value == timedelta(0) and self.field.initial_value == None:
            return None
        return value

class DateTimeWidget(DateWidget):

    def __init__(self, *args):
        DateWidget.__init__(self, *args)
        self.gtkwidget.set_property('show-time', True)
        self.initial_delta = timedelta(0)
        
    def set_value(self, value):
        ## FIXME: datetime has only time?
        return self.gtkwidget.set_property('datetime', value)
        
    def get_value(self, shown=False):
        value = self.gtkwidget.get_property('datetime')
        value = self.field.clean_value(value, add_second=True, add_microsecond=True)
        return value 

class DateTimeTZWidget(DateTimeWidget):
    pass

class TextWidget(Widget):

    def __init__(self, *args):
        Widget.__init__(self, *args)
        self.gtkwidget.set_property('wrap-mode', gtk.WRAP_WORD)

    def set_value(self, value):
        buff = self.gtkwidget.get_buffer()
        buff.set_text( value)

    def get_value(self, shown=False):
        buff = self.gtkwidget.get_buffer()
        ts = buff.get_iter_at_offset(0)
        te = buff.get_iter_at_offset(-1)
        text = buff.get_text(ts, te)
        return text
        

class BooleanWidget(Widget):
    """
    Null value is not admittable

    A boolean widget can be represented via CheckButton (default) or radio
    button (just use r=field_name when setting layout). In the latter case
    you can safely group widgets toghether with normal gtk tools ``.set.group()``
    to gain a switch between different alternatives::

      m.SqlMask(..., layout='r=male, r=female')
      m.widgets['r=female'].set_group(m.widgets['r=male'])

    """

    def __init__(self, *args):
        Widget.__init__(self, *args)
        self.gtkwidget.connect_after('toggled', self.on_toggled_cb)

    def on_toggled_cb(self, widget):
        self.master.run_hook('on_activate', self, field_name=self.field_name)
        
    def set_value(self, value):
        self.gtkwidget.set_active(bool(value))

    def get_value(self, shown=False):
        return self.gtkwidget.get_active( )
        
class BooleanNullWidget(BooleanWidget):
    """
    This gtkwidget is placed in inconsinstent state to represent NULL
    """
    def __init__(self, *args):
        Widget.__init__(self, *args)
        self._clicked_id = self.gtkwidget.connect('clicked', self.on_clicked_cb)
        self.gtkwidget.connect_after('toggled', self.on_toggled_cb)

    def set_value(self, value):

        if value == None:
            self.gtkwidget.set_inconsistent(True)
        else:
            ## This is needed to work around the fact that set_active(...) triggers
            ## a clicked signal
            self.gtkwidget.handler_block(self._clicked_id)

            self.gtkwidget.set_inconsistent(False)
            self.gtkwidget.set_active(value)

            self.gtkwidget.handler_unblock(self._clicked_id)

    def get_value(self, shown=False):
        if self.gtkwidget.get_inconsistent():
            return None
        else:
            return self.gtkwidget.get_active( )
            
    def on_clicked_cb(self, button):
        """
        a toggle function that loops through inconsinstent state also
        """
        active = not button.get_active()
        null = button.get_inconsistent()

        ## -   -> True  -> False
        if null:  # - next is True
            button.set_active(True)
            button.set_inconsistent(False)
        else:
            if active == True:
                button.set_inconsistent(False)
                button.active = False
            else:
                button.active = True
                button.set_inconsistent(True)

        return True

class ForeignKeyComboboxWidget(Widget):
    """a ComboBoxEntry with 2 columns

    In any case for the moment we need to click on a choice from the completion
    (we cannot just write a correct value), since completion also retrieves the id
    """

    def __init__(self, *args):

        Widget.__init__(self, *args)
        ## see completion.append_to_model() to understand the meaning of these 4 columns
        # add to a model that has 4 cols:
        #       0: the value to be used as foreign key
        #       1: the value to be shown in the entry 
        #       2: data to be shown in the dropdown
        #       3: a dictionary of all fields in the returned row
        #          this can be used to set additional fields
                    

        self.model = gtk.ListStore(object, str, str, object)

#        self.gtkwidget.connect('changed', self.clean_real_value)
        self.gtkwidget.set_model(self.model)
        self.gtkwidget.set_text_column(2)

        self.gtkwidget.connect(
            'button-press-event', self.completion.pop_menu, self.field_name, 3)
        self.gtkwidget.connect(
            'key-press-event', self.completion.keypress_event_cb, self.field_name)
        self.entry = self.gtkwidget.child
        completion = self.completion.prepare_completion(self.field_name, mode='regexp',
                                                               match_col=2)
        completion.set_model(self.model)
        self.entry.set_completion(completion)
        self.gtkwidget.connect('notify::popup-shown', self.on_popup)        

    def on_popup(self, widget, params):
        """the popup should be empty. We force the completion instead
        """
        self.completion.show_possible_completion(self.gtkwidget, mode='regexp')
            
        return True

    def clean_real_value(self, *args):
        ## the EntryText has been changed. The value may no longe be  valid
        self.real_value = False

    def set_value(self, value):
        """We have a 'real_value' that is normally an id or a key and a 'display_value'
        that is the value we want to show
        """
        display_value = self.field.lookup_value(value)
        if value == None:
            if self.field.type == str:
                value = ''

        self.model.clear()
        self.model.append([value, display_value, display_value,''])
        self.gtkwidget.set_active(0)   # which column 
#        self.real_value = True  ?????

        #self.gtkwidget.set_text( str(value) )
        
    def get_value(self, shown=False):
        #dbg.write()

        if shown == True:
            ## this is for completion. The value needed is the value in the entry not in the model
            return self.entry.get_text()

        idx = self.gtkwidget.get_active()
        value, display_value, descr, obj_dict = self.model[idx]

        return  value

class ForeignKeyWidget(Widget):
    """a ComboBoxEntry with 2 columns

    In any case for the moment we need to click on a choice from the completion
    (we cannot just write a correct value), since completion also retrieves the id
    """

    def __init__(self, *args):

        Widget.__init__(self, *args)

        self.entry  = self.gtkwidget.entry
        self.button = self.gtkwidget.button
        self.add_completion()
        self.real_value = True
        self.master.completions[self.field_name] = self.completion
        self.value = None
        self.entry.connect('changed', self.on_entry_changed)

    def add_completion(self):
        """add completion bindings and liststore
        """
        self.completion = FkeyCompletion(self.master, self, self.field_name)
        self.completion.add_completion(self.entry)
        self.master.completions[self.field_name] = self.completion

        ## button connect
        self.button.connect('button-press-event', self.button_press_cb, self.field_name)
        #self.button.connect('clicked', self.on_button_clicked)

        ## entry connect
        self.completion.add_callbacks(self.entry)

    def button_press_cb(self, widget, event, field_name):
        """
        Double click -> mode enum
        Simple click <3> -> menu
        """

        if event.button == 3:
            self.completion.pop_menu(widget, event, self.field_name)

        elif event.button == 1:
            if event.type == gtk.gdk._2BUTTON_PRESS:
                # cancel reques by first simple click
                gobject.source_remove(self.idle_id)
                    
                mode = 'enum'
            else:
                mode = 'regexp'
        
            self.idle_id = gobject.idle_add(
                self.completion.show_possible_completion, self.entry, mode)
                
        return True


    def on_key_press(self, widget, event, when='press'):

        return self.completion.keypress_event_cb(self.entry, event, self.field_name, when)

    def on_entry_changed(self, editable):

        self.real_value = False

    def clean_real_value(self, *args):
        ## the EntryText has been changed. The value may no longe be  valid
        self.real_value = False

    def is_valid(self):
        return self.real_value

    def set_value(self, value, shown=False):
        """
        We have a real 'value' that is normally an id or a key and a 'display_value'
        that is the value we want to show
        shown: the passed value is a value to be shown.
               a shown value is not cleaned (e.g.: for completion)
        """
        if shown:
            display_value = value
            self.entry.set_text(display_value)
        else:
            self.value = value
            display_value = self.field.lookup_value(value)
            self.entry.set_text(display_value)
            self.real_value = True  # we can trust this value, has been set by procedures
            
    def get_value(self, shown=False):
        if shown:
            return self.entry.get_text() 
        if self.real_value:
            return self.value
        else:
            if self.entry.get_text():
                msg = _("'%s' may have an invalid value: try completion on that") % self.field_name
                raise exc.ValidationError(msg)
            else:
                return None

class CollectionWidget(Widget):
    """
    a SqlTable widget that represents a collection of records
    """
    def __init__(self, *args):
        
        Widget.__init__(self, *args)
        table = self.field.table

        from sqlkit.widgets import SqlTable
        loader_spec = self.master.laygen.loaders[self.field_name]

        direction = self.field.property.direction.name
        if direction  == 'MANYTOMANY':
            direction = "m2m"
        elif direction == 'ONETOMANY':
            direction = "o2m"

        self.table = SqlTable(
            table.name,
            geom = (-1, -1),
            rows = loader_spec.get('rows', 5),
            mapper = self.field.mapper,
            session=self.master.session,
            metadata=self.master.metadata,
            dbproxy=self.master.dbproxy,
            naked=True,
            mode=self.master.mode,
            format = filter_related(self.master._format_dict, self.field_name),
            col_width = filter_related(self.master.col_width, self.field_name),
            field_list = loader_spec.get('field_list', None),
            addto=self.gtkwidget,
            ignore_fields = [c.name for c in self.field.property.remote_side],
            dev = self.master.dev,
            relationship_leader = self.master,
            relationship_mode = direction,
            relationship_path = self.master.relationship_path + [self.field_name],
            label_map = self.prepare_label_map()
            )
        
        # We generally want a table to expand if possible        
        parent = self.gtkwidget.get_parent()
        if parent:
            prop_names = [prop.name for prop in parent.list_child_properties()]
            if 'y-options' in prop_names:
                parent.child_set_property(self.gtkwidget, 'y-options', gtk.EXPAND | gtk.FILL)
            if isinstance(parent, gtk.VBox):
                parent.child_set_property(self.gtkwidget, 'expand', True)

        self.master.related.add_element(self.field_name, self.table)

    def set_value(self, value):
        self.table.set_records(value)

    def get_value(self, shown=False):
        return self.table.records 

    def prepare_label_map(self):
        """
        Implement the possibility to specify a label key as::

           related_field.field_name

        so that related field can be personalized in different ways.
        As an example a project can have tho relations to the user table, one is under
        'staff' attribute and the second via 'manager'. Bothe these point to 'username'
        that should appear in the mask with staff and manager label.
        """

        from copy import copy
        label_map = copy(self.master.label_map)

        for key, value in label_map.items():
            if key.startswith('%s.' % self.field_name):
                key = key.replace('%s.' % self.field_name, '')
                label_map[key] = value

        return label_map


def filter_related(my_dict, relation):
    """
    filters a dict to use only width info for relation 'relation'
    e.g:
    a = {'ind.cap' : 5, 'username' : 7}
    >>> filter_related(a, 'ind')
    {'cap': 5}
    """

    new = {}
    strip = '%s.' % relation
    if my_dict:
        for key in my_dict:
            if key.startswith(strip):
                nkey = re.sub('^%s' % strip, '', key)
                new[nkey] = my_dict[key]

    return new





