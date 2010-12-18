# -*- coding: utf-8 -*-
# Copyright (C) 2008-2009-2010, Sandro Dentella <sandro@e-den.it>
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
.. _fields:

=======
Fields
=======
Mask/Tables are collection of data that may belong to the database or not.
Each of the data represented in the GUI that needs to partecipate to any
updating/saving process should have it's own handler that is a Field.

A Field is an entity that knows how to handle a piece of data, be it on
the database (a field_name) or just in the GUI. It knows:

   - if it belongs to the database (attribute ``persisted`` is True) and in
     case how it is defined ( i.e.: sqlalchemy property/column)
   - if it is nullable/editable
   - which widget must be used to represent it (see below, not requested)
   - how to produce a formatted representation of the field.

It provides functions to

   - set/get value
   - get default value (but will not cope with server_side defaults)
   - tell if it changed from the default
   - clean value according to it's logic: i.e. return a value of the correct type
   - validate values (possibly according to other criteria)

Relation with the master sqlwidget
----------------------------------

Currently there are a number of operation that require that the field know wich
is the sqlwidget it is acting for. I'd like to loosen this connection in future
but at present it's used in the following situations:

* to keep updated the list of field_widgets
* to get default values (that can be local to a sqlwidget)
* for validation purposes: to issue master.run_hooks and NonNullableException
* FKey: to handle addition of related_obj when cascading policy requires it

In the meanwhile I add master to the Field via set_master() and add a widget
to the Field via set_widget()


Db attributes
-------------

The costructor can be passed a dict of field_attributes

   * field_name: the name of the field
   * nullable: True if field is nullable or False. The related widget will get a background color that
               reflects the fact that it is required (currently yellow). This can be set at any time.
   * editable: True if field is editable or False. The related widget will be set unsensitive. This can
               be set at any time.
   * length: the desired length in chars
   * default: a possible default option
   * type: the python type

   * mapper: defined as None for field that are mapped 
   * table: the SA Table object
   * column: the SA Column object
   * property: the SA Property - if any
   * fkey: the SA ForeignKey or None
   * pkey: True is field is a PRIMARY KEY or False
   
Other attributes
----------------

   * widget:  the widget used to represent it. May be sqlkit.widgets.mask.miniwidget or similar
   * format: the format used to represent the field (numeric or date/time)
   * locale: the locale to use to represent the field (numeric or date/time)
   * DecimalFields also have precision/scale
   * Varchar/TextFields also have blank=True/False (default: False). It determines if an empty string is
     a valid value. Empty strings are differerent from NULL values
     
future
-------
   This should provide a way to set the possible observers

   validation based on the type should live here

   possibly more validation may live here

formatting/locale
-----------------

   see decimal_ to have an intro on formatting numbers

.. _decimal: http://java.sun.com/docs/books/tutorial/i18n/format/decimalFormat.html

FieldChooser
===============

This class implements a way to decide which Field should be associated to
each field_name in a mapper (used in setup_field_validation so that it can
be easily overwritten).  It's important to understand that it already
receives a gtkwidget from layoutgenerator; that widget has been set by
introspection of the layout description and of the field in the database.

You can overwrite the decision of the field redefining the gui_field on a
derived sqlwidget or passing it as argument (see code snippet 34)::

  class Movie(SqlMask):
      gui_field_mapping = {'date_release' : VarcharField}

  t = Movie(table='movie', dbproxy=db, layout=lay)
  
It's up to the field defined in this way to be able to handle the type of data.
This setting can be used to add field constraints (eg: mail address
validation) or to completely change the widget that represent data.

Widgets
========

A Field does not create a gtk widget to represent data, that's -rarely- done
by sqlkit.widgets.mask.miniwiget.Widget. More tipically it is done by the
layout procedure and the Fields/Widget just takes its control and adds
completion capabilities.

A notable exception to this rule is represented by any m2m/o2m relation,
that in the layout is only present as a gtk.Alignment widget to which a
children is added by mask.Widget

Global variables
================

Varchar fields will try to cast an empty value to None unless blank_ok is set
in the field::

    t.gui_field.field_name.blank_ok = True

or globally:

    from sqlkit.widgets.common import fields
    fields.BLANK_OK = True

Default value for BLANK_OK is False.

This is only enforced for NEW records, for alreadu persisted records the default behaviour is
to let it as-is, to prevent a very annoying flood of dialog "do you want to save?" when you
just need to browse some data.


Available Fields
=================

.. autoclass:: Field
   :members: set_widget, set_value, get_value, clear_value, format_value, clean_value,
          has_changed, get_default, set_default, validate, get_human_value, persistent,
          nullable, editable

All other field inherit from Field

.. autoclass:: VarcharField
   :members: blank_ok
   
.. autoclass:: IntegerField
   :members: format

.. autoclass:: FloatField
   :members: format

.. autoclass:: DecimalField
   :members: format

.. autoclass:: TextField
.. autoclass:: DateField
   :members: format

.. autoclass:: TimeField
.. autoclass:: TimeTZField
.. autoclass:: IntervalField
.. autoclass:: DateTimeField
.. autoclass:: DateTimeTZField
.. autoclass:: BooleanField
.. autoclass:: BooleanNullField
.. autoclass:: ForeignKeyField
   :members: lookup_value, add_related_object
   
.. autoclass:: CollectionField

.. autofunction:: std_cleanup
"""
import re
import types
import warnings
from datetime import datetime, time, date, timedelta
from decimal import Decimal

import babel
from sqlalchemy.schema import ColumnDefault

from sqlkit import exc, _
from sqlkit.misc import localtimezone
from sqlkit.misc.babel_support import numbers, dates
from sqlkit.db import minspect

from sqlkit.exc import ValidationError, NotHandledField, NotHandledDefault
BLANK_OK = False

class FieldChooser(object):

    """here we wrap the gtk widget in a double layer:

        * field for validation
        * widget for edit

    w:           the widget dictionary retuner by Layout
        
    """

    def __init__(self, info, widgets=None, gui_field_mapping=None):
        """    
        info:        a InspectMapper objet
        widgets:     the widget dictionary retuned by Layout
        gui_field_mapping:  a dictionali-like store where to look for custom mapping of
                     field-name and fields. Used when the field cannot be devised
                     from the mapper as the fields are not persisted.
        """
        self.info = info
        self.widgets = widgets or {}
        self.gui_field_mapping = gui_field_mapping or {}

    def get_field(self, field_name, field_attrs=None, def_str=None, test=False):
        """
        return a field

        field_name:  the name of the field in the db
        field_attrs:     the dict for this field as worked out by InspectMapper
        def_str:     the definition string in the layout that determined
                     the gtk.Widget (eg.: c=married, e=first_name)
                     as extracted by layoutgen and set in laygen.fields_in_layout dictionary
        """        

        if field_name in self.gui_field_mapping:
            return self.gui_field_mapping.get(field_name)

        def_str = def_str or ''

        if self.info.is_fkey(field_name):
            return ForeignKeyField

        if self.info.is_loader(field_name):
            return CollectionField
        
        if self.info.is_integer(field_name):
            return IntegerField

        if self.info.is_float(field_name):
            return FloatField

        if self.info.is_numeric(field_name):
            return DecimalField

        if self.info.is_integer(field_name):
            return IntegerField

        if self.info.is_date(field_name):
            return DateField

        if self.info.is_boolean(field_name):
            if self.info.is_nullable(field_name):
                return BooleanNullField
            else:
                return BooleanField
            
        if self.info.is_interval(field_name):
            return IntervalField

        if self.info.is_time(field_name):
            if field_attrs['col'].type.timezone:
                return TimeField
            else:
                return TimeField

        if self.info.is_datetime(field_name):
            if field_attrs['col'].type.timezone:
                return DateTimeTZField
            else:
                return DateTimeField

        if (self.info.is_text(field_name) and not def_str.startswith('e=')) or (def_str.startswith('TX') ):
            return TextField
        
        if self.info.is_string(field_name):
            return VarcharField

        else:
            return VarcharField

#         raise NotHandledField("Field '%s' is not handled in any way: COL_SPEC: %s" %
#                               (field_name, filter_attr['col_spec']))

class Field(object):
    Widget = None
    default_def_string = 'ae'
    type = None
    
    def __init__(self, field_name, field_attrs=None):
        
        """
        :param field_name:  the name of the field in the db
        :param field_attrs:     the dict as worked out by InspectMapper. Can be created by hand: that is
                     usefull when field is not mapped in the database. These attributes may be
                     present:

                     :nullable: boolean. If True None is accepted as value
                     :editable: boolean. If True the value can be edited, if 'column'  is not passed
                                the field is tuned into not editable
                     :length:   used to determine how many chas are needed to represent it
                     :default:  a possible default value
                     :mapper:   the mapper the field is defined into, if any
                     :pkey:     true if this field is a primary key
                     :fkey:     a sqlalchemy ForeignKey ogject if this field is a foreign key
                     :property: the sqlalchemy property the field has in the mapper
                     :column:   the sqlalchemy column the field maps to
                     :table:    the table the field is defined in, if any
                     
        :param def_str:     the definition string in the layout that determined
                     the gtk.Widget (eg.: c=married, e=first_name)
        :param master:      the sqlkit widget: an instance of SqlMask or SqlTable
        """

        self.field_name = field_name
        self._add_info(field_attrs or {})
        self.initial_value = None

    def set_widget(self, gtkwidget=None, def_str=None, widget=None):
        """
        :param def_str:     the definition string in the layout that determined
                     the gtk.Widget (eg.: c=married, e=first_name)
        :param widget:      the miniwidget to be used. Defaults to class-defined self.Widget
                            the widget can be a string of a Widget derived from ``miniwidget.Widget``
        :param gtkwidget:   the gtk widget to be used (already created by Layout)
        
        """
        from sqlkit.widgets.mask import miniwidgets
        from sqlkit.widgets.table import tablewidgets

        ## widget can be a string in which case it it searched for in sqlkit.widgets.mask.miniwidgets
        ## tis avoids importing miniwidgets at import time and delayes it to this function
        if isinstance(widget, basestring):
            Widget = getattr(miniwidgets, widget)

        if def_str and  def_str.startswith('ro='):
            widget = miniwidgets.ReadOnlyWidget
            
        Widget = widget or getattr(miniwidgets, self.Widget)
        if gtkwidget:
            ## used in SqlMask
            self.widget = Widget(gtkwidget, self)
            gtkwidget.connect('destroy', self.destroy)
        else:
            ### used in SqlTable
            self.widget = tablewidgets.CellWidget(self)

    def destroy(self, widget):

        try:
            del self.widget
            del self.master
        except AttributeError:
            pass
            
    def set_master(self, master):
        """
        add a sqlwidget as master of this field. A master may be needed to

          * get defaults
          * validate
          * add related objects
        """
        self.master = master
        
    def set_nullable(self, value):
        self._nullable = value
        try:
            self.widget.set_not_null_style(value)
        except AttributeError:
            pass

    def get_nullable(self):
        return self._nullable

    nullable = property(get_nullable, set_nullable)
    
    def set_editable(self, value):
        self._editable = value
        try:
            self.widget.set_editable(value)
        except AttributeError:
            pass

    def get_editable(self):
        return self._editable

    editable = property(get_editable, set_editable)
    
    def _add_info(self, field_attrs):
        """
        read docs in __init__
        """
        self._nullable =  field_attrs.get('nullable', True)  # don't trigger now widget.set_bg()
        self._editable =  field_attrs.get('editable', 'property' in field_attrs and field_attrs['property'] or False)
        self.length   =  field_attrs.get('length', None)
        self.default  =  field_attrs.get('default', None)
        self.mapper   =  field_attrs.get('mapper', None)
        self.pkey     =  field_attrs.get('pkey', None)
        self.fkey     =  field_attrs.get('fkey', None)
        self.property =  field_attrs.get('property', None)
        self.column   =  field_attrs.get('col', None)
        self.table    =  field_attrs.get('table', None)
        if self.pkey:
            self._nullable = False

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        value = self.clean_value(value)
        if initial:
            self.initial_value = value
        if hasattr(self, 'widget') and update_widget:
            self.widget.set_value(value)
        if obj and not initial:
            setattr(obj, self.field_name, value)

    def get_value(self, shown=False):
        """
        Return the current value. Look for it in the widget and returns a cleaned value
        """
        if not hasattr(self, 'widget'):
            return exc.MissingWidget("%s has no defined 'widget' " % self)
        value = self.widget.get_value(shown=shown)
        return self.clean_value(value)

    def clear_value(self):
        """
        sets a value that clears the corresponding widget, can be None or []
        """
        self.set_value(None)

    def set_completion(self, regexp):
        pass

    def has_changed(self, verbose=False):
        """
        return True if field has changed after last set
        """
        if not self.editable:
            return False
        try:
            return not self.get_value() == self.initial_value
        except exc.ValidationError:
            # a validation error is a clear sign the values have been changed, but we propabli don't
            # want to cope with them now
            return True
    
    def get_default(self):
        """
        return the default value for this object
        """
        if hasattr(self, 'master'):
            value = self.master.defaults.get(self.field_name)
        else:
            value = None
            
        if not value:
            try:
                value = self.default
            except KeyError:
                pass
            if isinstance(value, ColumnDefault):
                if not callable(value.arg) and type(value.arg) == self.type:
                    return value.arg
                else:
                    ## FIXME: I'm not able to handle this now.
                    raise NotHandledDefault
        if not isinstance(value, self.type):
            return
        return value
        
    def set_default(self):
        self.set_value(self.get_default())
        
    def clean_value(self, value):
        """
        return a value of the correct type, if needed parse it with
        locale parsers (numbers, date...)

        :param value: the value to be cleaned (i.e. casted to correct type). It's the
                      attribute of a persisten object or **the object itself** for non
                      persisted fields. I.e.: if you create a custom field to count how many
                      movies has directed each director, the Director instance will be passed
                      as ``value``. 

        This function is used while sorting a column 

        """
        return value
   
    def format_value(self, value, format=None):
        """
        return a **string representation** of the value according to current
        locale value is a"cleaned" value

        :param value: the value to be formatted (must already be casted to correct type)
        """
        return value
    
    def validate(self, value, clean=False):
        """
        check if the current value is accepted and call
        :ref:`on_field__validation <on_field__validation>`
        on the master's hook.
        """
        if not clean:
            try:
                value = self.clean_value(value) 

            except Exception, e:
                msg = "Field %s could not validate value '%s': error was: %s" 
                raise exc.ValidationError(_(msg % (field_name, e) ))

        if value is None and not self.nullable and not self.default:
            raise exc.NotNullableFieldError(self.field_name, master=self.master)

        self.master.run_hook('on_field_validation', value, self, field_name=self.field_name)

        return True

    def get_human_value(self, value, format=None):
        """
        return the value or a translation in human readable for foreign key
        """
        return self.format_value(value, format=format)
        
    def _get_persistent(self):
        
        try:
            return self._persistent
        except AttributeError:
            self._persistent = hasattr(self, 'property') and self.property
            return self._persistent

    persistent = property(_get_persistent)
        
    def __repr__(self):
        return "<%s - %s >" % (self.__class__.__name__, self.field_name)

    @classmethod
    def std_cleanup(cls, fn):
        """
        A decorator that will handle standard cases: value is None, is a string
        or is already cleaned.

        This is handy when building new Fields as it allows to keep the
        ``.clean_value`` method as simple as possible, i.e.  no need to check for
        standard cases::

            class CountMovies(fields.IntegerField):
                '''
                A field that counts the movies
                '''
                @fields.std_cleanup
                def clean_value(self, value):
                    ## missing a field_name attribute on obj the object itselt is passed
                    return len(value.movies)

        """
        def new_func(self, value):
            ## standard cleanup: values can
            if isinstance(value, (basestring, types.NoneType, self.type)):
                return super(self.__class__, self).clean_value(value)
            ## custom one
            return fn(self, value)
        new_func.__doc__ = fn.__doc__
        return new_func
class VarcharField(Field):
    """
    The field to represent Strings

    """
    Widget = 'VarcharWidget'
    type = str
    blank_ok = None
    """
    The widget return an epty string on empty values. This variable determines if that value
    will be set NULL or left empty. Regardless of this value the value is left untouched if
    it already exists.
    """
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        self.blank_ok = BLANK_OK
        
    def clean_value(self, value):
        if value == '' and not self.blank_ok:
            if not self.initial_value == '':
                value = None
        return value

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        if initial:
            self.initial_value = value
        value = self.clean_value(value)

        if hasattr(self, 'widget') and update_widget:
            self.widget.set_value(value or '')

        if obj and not initial:
            setattr(obj, self.field_name, value)

    def get_value(self, shown=False):

        value = Field.get_value(self, shown)
        if value == '' and (self.initial_value is None or (
            ## it's very annoying that a db with '' value is turned into None if I don't do anything!
            ## self.blank_ok should only set behaviour of NEW objects
            self.blank_ok is False and not self.initial_value == '')):
            return None
        return value


##### Numbers
class IntegerField(Field):
    """
    The fields to handle interegers
    """
    Widget = 'IntegerWidget'
    type = int
    length = 8

    format = None
    """How to represent integers. Default: '#,###' """
    
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        self.format = "#,###"
        self.locale = babel.default_locale('LC_NUMERIC')
        
    def clean_value(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                if isinstance(value, basestring):
                    value = numbers.parse_number(value, locale=self.locale)
                elif isinstance(value, (int, long)):
                    value = int(value)
                else:
                    value = int(value)
            except Exception, e:
                raise exc.ValidationError(str(e))
            return value

    def format_value(self, value, format=None):
        if value is None:
            return ''
        return numbers.format_decimal(value, format=format or self.format, locale=self.locale)
        
    @classmethod
    def std_cleanup(cls, fn):
        """
        A decorator that will handle standard cases: value is None, is a string
        or is already cleaned.

        This is handy when building new Fields as it allows to keep the
        ``.clean_value`` method as simple as possible, i.e.  no need to check for
        standard cases::

            class CountMovies(fields.IntegerField):
                '''
                A field that counts the movies
                '''
                @fields.std_cleanup
                def clean_value(self, value):
                    ## missing a field_name attribute on obj the object itselt is passed
                    return len(value.movies)

        """
        def new_func(self, value):
            ## standard cleanup: values can
            if isinstance(value, (basestring, types.NoneType, self.type, long)):
                return super(self.__class__, self).clean_value(value)
            ## custom one
            return fn(self, value)
        new_func.__doc__ = fn.__doc__
        return new_func
class FloatField(IntegerField):
    """
    The fields to handle floats
    """
    Widget = 'FloatWidget'
    type = float
    length = 10
    
    format = None
    """How to represent integers. Default: None """
    
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        #self.format = "#.###,000"
        self.format = None
        self.locale = babel.default_locale('LC_NUMERIC')
        
    def clean_value(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                if isinstance(value, basestring):
                    value = numbers.parse_decimal(value, locale=self.locale)
                elif isinstance(value, float):
                    pass
                else:
                    value = float(value)
            except Exception, e:
                raise exc.ValidationError(e)
            return value
        
    def format_value(self, value, format=None):
        if value is None:
            return ''
        return numbers.format_decimal(value, format=format or self.format, locale=self.locale)
        
class DecimalField(IntegerField):
    """
    The fields to handle Numeric Fields
    """
    Widget = 'DecimalWidget'
    type = Decimal
    length = 10

    scale = None
    """the number of decimals. Default is desumed by introspection"""

    
    format = None
    """How to represent integers. Default: '#,###.00' (The number of 0 determined by ``scale`` """
    
    
    def __init__(self, *args, **kw):
        """
        If column is defined precision and scale from column will be used. 
        You need to set precision and scale after the field is created otherwise
        """
        Field.__init__(self, *args, **kw)
        
        if self.column is not None:
            self.precision = self.column.type.precision
            self.scale = self.column.type.scale
        else:
            self.precision = 8
            self.scale = 2
            
        self.format = "#,###.%s" % ('0' * self.scale)
        self.format_f = "%%.%sf" % self.scale
        self.locale = babel.default_locale('LC_NUMERIC')
        
    def clean_value(self, value):
        if value in (None, ''):
            return None
        else:
            try:
                if isinstance(value, basestring):
                ## why there's no parse_Decimal in babel?
                    fl = self.format_f % numbers.parse_decimal(value, locale=self.locale)
                    value = Decimal(fl)
                elif isinstance(value, Decimal):
                    pass
                elif isinstance(value, int):
                    value = Decimal(value)
                    #value = self.clean_value(str(value))
                elif isinstance(value, float):
                    fl_str = numbers.format_decimal(value, locale=self.locale)
                    value = self.clean_value(fl_str)
                else:
                    raise exc.ValidationError(_("value is not Decimal nor string: %s" % value))
            except Exception, e:
                raise exc.ValidationError(e)
            return value
        
    def format_value(self, value, format=None):
        if value is None:
            return ''
        return numbers.format_decimal(value, format=format or self.format, locale=self.locale)

    @classmethod
    def std_cleanup(cls, fn):
        """
        A decorator that will handle standard cases: value is None, is a string
        or is already cleaned.

        This is handy when building new Fields as it allows to keep the
        ``.clean_value`` method as simple as possible, i.e.  no need to check for
        standard cases::

            class CountMovies(fields.IntegerField):
                '''
                A field that counts the movies
                '''
                @fields.std_cleanup
                def clean_value(self, value):
                    ## missing a field_name attribute on obj the object itselt is passed
                    return len(value.movies)

        """
        def new_func(self, value):
            ## standard cleanup: values can
            if isinstance(value, (basestring, types.NoneType, self.type, int)):
                return super(self.__class__, self).clean_value(value)
            ## custom one
            return fn(self, value)
        new_func.__doc__ = fn.__doc__
        return new_func
class TextField(VarcharField):
    Widget = 'TextWidget'
    default_def_string = 'TXS'
    type = str

    def set_max_length(self):
        pass

##### Time/Dates
class DateField(Field):
    """
    The fields to handle datets
    """
    Widget = 'DateWidget'
    default_def_string = 'd'
    format = None
    """The format used to represent dates. Default: ``short``"""

    type = date
        
    def __init__(self, *args, **kw):
        Field.__init__(self, *args, **kw)
        self.format = 'short'
        self.locale = babel.default_locale('LC_TIME')
        #if format not in ('short', 'long', 'default', 'medium', 'full'):
        #    pass

    def clean_value(self, value):

        if value in (None, ''):
            return None

        try:
            if isinstance(value, basestring):
                value = dates.parse_date(value, locale=self.locale)
            elif isinstance(value, date):
                pass
            else:
                raise exc.ValidationError(_("value is not date nor string: %s" % value))
        except Exception, e:
            raise exc.ValidationError(e)
        return value
    
    def format_value(self, value, format=None):

        if not value:
            return ''

        return dates.format_date(value, format=format or self.format, locale=self.locale)
        
        
class TimeField(DateField):
    """
    The fields to handle times w/o timezone
    """
    Widget = 'TimeWidget'
    default_def_string = 'ae'
    type = time

    def clean_value(self, value):

        if isinstance(value, basestring):
            try:
                value = dates.parse_time(value)
            except IndexError, e:
                try:
                    value = dates.parse_time("%s:00" % value)
                except Exception, e:
                    raise exc.ValidationError(e)
        return value
        
    def format_value(self, value, format=None):
        if not value:
            return ''
        
        if not isinstance(value, time):
            value = self.clean_value(value)

        return dates.format_time(value, format=format or self.format, locale=self.locale)

class TimeTZField(TimeField):
    """
    The fields to handle times with timezone
    """
    Widget = 'TimeTZWidget'

    def __init__(self, *args, **kwargs):
        TimeField.__init__(self, *args, **kwargs)
        self.TZ = None
        
    def clean_value(self, value):
        if isinstance(value, basestring):
            value = dates.parse_time(value)
        return value
        
    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        TimeField.set_value(self, value, initial=initial, obj=obj,
                            update_widget=update_widget)
        
        if initial:
            if value:
                self.TZ = value.tzinfo
                self.microsecond = value.microsecond
            else:
                self.TZ = None
                self.microsecond = 0

        if obj and not initial:
            setattr(obj, self.field_name, value)
        
    def get_value(self, shown=False):

        value = Field.get_value(self, shown)
        if not self.TZ:
            ## Local will return a tzinfo with the timezone of the system
            ## it will be added to bypass the limitation of dateedit
            self.TZ = localtimezone.Local
            self.microsecond = 0

        if value is None:
            return None
        value = time(*[int(i) for i in re.split('[.:]', value)]) 
        return value.replace(tzinfo=self.TZ, microsecond=self.microsecond)

class IntervalField(Field):
    """
    The fields to handle times with interval
    """
    Widget = 'IntervalWidget'
    type = timedelta

class DateTimeField(DateField):
    """
    The fields to handle datetimes w/o timezone
    """
    Widget = 'DateTimeWidget'
    type = datetime

    def __init__(self, *args, **kwargs):
        DateField.__init__(self, *args, **kwargs)
        self.microsecond = 0
        self.second = 0
        
    def clean_value(self, value, add_second=False, add_microsecond=False):
        """
        parse and return a clean value (ie: a datetime)
        if add_second/add_microsecond, second and microsecond as found in self.(micro)second
        and stored there by set_value are attached to work around widgets that may not be able 
        (or willing) return seconds and microseconds
        """

        if value in (None, ''):
            return None

        if isinstance(value, basestring):
            tmp_date = re.split('\s+', value.strip())
            try:
                date_value = dates.parse_date(tmp_date[0], locale=self.locale)
            except Exception, e:
                raise exc.ValidationError(_('Wrong date format: %s' % tmp_date[0] ))

            try:
                if len(tmp_date) > 1:
                    time_list = [int(i) for i in re.split('[:.]', tmp_date[1]) ]
                else:
                    time_list = []
                time_value = time(*time_list)

            except Exception, e:
                raise exc.ValidationError(_('Wrong time format' ))

            value = datetime.combine(date_value, time_value)

        if isinstance(value, datetime):
            if add_second:
                value = value.replace(second=self.second)
            if add_microsecond:
                value = value.replace(microsecond=self.microsecond)
            
        return value

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        Field.set_value(self, value, initial=initial, obj=obj,
                        update_widget=update_widget)
        
        if initial:
            if value:
                self.TZ = value.tzinfo
                self.microsecond = value.microsecond
                self.second = value.second
            else:
                self.TZ = None
                self.microsecond = 0
                self.second = 0
        
        if obj and not initial:
            setattr(obj, self.field_name, value)

    def format_value(self, value, format=None):

        if not value:
            return ''
        
        return dates.format_datetime(value, format=format or self.format, locale=self.locale)
        
    def get_value(self, shown=False):

        value = Field.get_value(self, shown)

        if value and value.microsecond:
            self.microsecond = value.microsecond
            value = value.replace(microsecond=self.microsecond)

        return value
        
class DateTimeTZField(DateTimeField):
    """
    The fields to handle datetimes with timezone
    """
    Widget = 'DateTimeTZWidget'

    def __init__(self, *args, **kwargs):
        DateTimeField.__init__(self, *args, **kwargs)
        self.TZ = None
        self.microsecond = 0
        
    def clean_value(self, value, add_second=False, add_microsecond=False):

        value = DateTimeField.clean_value(self, value, add_second, add_microsecond)

        if not self.TZ:
            ## Local will return a tzinfo with the timezone of the system
            ## it will be added to bypass the limitation of dateedit
            self.TZ = localtimezone.Local
        
        if value:
            if value.tzinfo:
                return value
            else:
                return value.replace(tzinfo=self.TZ)

        return None

    def get_value(self, shown=False):
        """
        Implement a hack around the fact that you normally don't need TZ
        and I don't provide a cell_renderer that gives you the opportunity to change it
        Attach the same timezone as the original data
        """
        value = Field.get_value(self, shown)
        return self.clean_value(value)

##### Boolean
class BooleanField(Field):
    """
    A field to handle booleans that does not allow NULL
    """

    Widget = 'BooleanWidget'
    default_def_string = 'c'
    type = bool

    def clean_value(self, value):
        if value is None:
            value = False
        if value not in (True, False):
            msg = "Null value not admittable for field %s" % self.field_name
            raise ValidationError(msg) 
        return value
    
    def clear_value(self):
        ## should I check the default here?
        self.set_value(False)

class BooleanNullField(Field):
    """
    A field to handle booleans that allows NULL
    """

    Widget = 'BooleanNullWidget'
    type = bool

    def clean_value(self, value):
        if value not in (True, False, None):
            msg = "Null value not admissable for field %s" % self.field_name
            raise ValidationError(msg) 
        return value
    
##### Misc
class ForeignKeyField(Field):
    """
    A field to handle foreign keys
    """
    Widget = 'ForeignKeyWidget'
    type = str
    
    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)

        from sqlkit.db.minspect import get_foreign_info

        self.lookup_values = {}
        self.broken_lookup = False
        self.table, self.column = get_foreign_info(self.fkey, names=False)
        self.table_lookup, self.column_lookup = self.table, self.column

    def lookup_value(self, field_value):
        """
        retrieve the value in a lookup table in case of foreign_key. It means: "given
        the foreign key return a value describing at the best the referenced record". 
        This implies some guessing of the best representation of the record or using
        information given to site-wide database configuration via _sqlkit_table.
        The details of such mechanism are described in :ref:`completion` and :ref:`TableDescr`.
        Since field_value may be incorrectly casted (it is used in completion)
        errors are catched and None is returned (rather than raising an Error)

        """
        from sqlkit.db.utils import tables, get_description, DictLike
        from sqlalchemy import text, select, Table, exceptions

        if field_value is None:
            return ''
        ## broken_lookup is needed just for cases when a referenced column is not unique (FKey)
        # I think this is not regular but fiebird sample database do have such references...
        if self.broken_lookup:
            return field_value
        try:
            return self.lookup_values[self.field_name][field_value]
        except Exception, e:
            descr_fields =  get_description(self.table_lookup)
            format =        get_description(self.table_lookup, attr='format')
            fields = [self.table_lookup.columns[f_name] for f_name in descr_fields]

            sql = select(fields, self.column_lookup == field_value)
            try:
                all = self.table.metadata.bind.execute(sql).fetchall()
            except (exceptions.DBAPIError), e:
                if hasattr(self, 'master'):
                    self.master.sb(e)
                return None

            if len(all) == 0:
                raise exc.LookupValueMissingValue("%s returns no values for '%s': '%s'" % (
                    sql, self.field_name, field_value))
            elif len(all) > 1:
                msg = "%s returns multiple values for '%s': '%s'" % (
                    sql, self.field_name, field_value)
                warnings.warn(msg)
                self.editable = False
                self.broken_lookup = True
                return field_value
                #raise exc.LookupValueMultipleValues()
            else:
                value = format % DictLike(all[0])
                try:
                    self.lookup_values[self.field_name][field_value] = value
                    return value
                except KeyError:
                    self.lookup_values[self.field_name] = {}
                    self.lookup_values[self.field_name][field_value] = value
                    return value

            self.lookup_values[self.field_name][field_value] = value
        return value

    def set_master(self, master):
        self.master = master
        self._props_for_delete_orphan = minspect.get_props_for_delete_orphan(
            master.mapper, self.field_name)
        
    def clean_value(self, value, input_is_fkey=False):
        """
        return a cleaned value (i.e.: the foreign key)
        if input_is_fkey=False the text is considered an id, else it's considered a 'search' value
        """
        if input_is_fkey:
            return value
        
        query = self.widget.completion.compose_select_statement(
            self.widget.completion.query, '=', value)
        ret = query.all()
        #ret = self.master.metadata.bind.execute(sql).fetchone()
        return ret and ret[0]

    def validate(self, value, clean=False):
        """
        for an fkey field a 'clean' value is an fkey, by definition...
        """
        input_is_fkey = clean

        try:
            value = self.clean_value(value, input_is_fkey=clean)
        except Exception, e:
            msg = "Field %s could not validate value '%s': error was: %s" 
            raise exc.ValidationError(_(msg % (self.field_name, value, e) ))

        if value is None and not self.nullable:
            raise exc.NotNullableFieldError(self.field_name, master=self.master)

        self.master.run_hook('on_field_validation', value, self, field_name=self.field_name)

        return value
        
    def get_value(self, shown=False):

        if not hasattr(self, 'widget'):
            return exc.MissingWidget("%s has no defined 'widget' " % self)
        value = self.widget.get_value(shown)
        ## a shown value is not to be transformed
        if not shown and value == '' and self.initial_value is None:
            return None
        return value

    def get_human_value(self, value, format=None):

        if isinstance(value, (list, tuple)):
            return str([self.lookup_value(v) for v in value])
        return self.lookup_value(value)
    
    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):
        if not shown:
            value = self.clean_value(value, input_is_fkey=True)
        if initial:
            self.initial_value = value
        if hasattr(self, 'widget') and update_widget:
            self.widget.set_value(value, shown=shown)

        if value and not initial:
            ## Rationale: See ex_03 (that uses class_=Movie
            # i.e. with definition of relation with backref with delete-orphan). this function is called
            # all the time we enter a record (not just *new* records).

            ## TODO/FIXME: thhis is not working for sqla 0.6 as backref is no longer a backref!

            for prop in self._props_for_delete_orphan:
                self.add_related_object(prop, value)

        if obj and not initial:
            setattr(obj, self.field_name, value)

    def has_changed(self):
        ## special case, when is empty
        if self.initial_value is None and self.widget.get_value(shown=True) == '':
            return False
        
        if hasattr(self.widget, 'real_value') and self.widget.real_value == False:
            return True
        else:
            return Field.has_changed(self)

    def get_default(self):
        """
        return the default value for this object
        """
        ## The only difference from super is that I don't get out if there's a default
        if hasattr(self, 'master'):
            value = self.master.defaults.get(self.field_name)
        else:
            value = None
            
        if not value:
            try:
                value = self.default
            except KeyError:
                pass
            if isinstance(value, ColumnDefault):
                if not callable(value.arg) and type(value.arg) == self.type:
                    return value.arg
                else:
                    ## FIXME: I'm not able to handle this now.
                    raise NotHandledDefault
        ## This has no meaning as self.type has no real meaning in a foreign key
        if not isinstance(value, self.type):
            pass
        return value
        
    def add_related_object(self, prop, key):
        """
        Add an object to fullfill the  constraint on delete-orphan 

        This is not meant to be used directly, it is used by :meth:`set_value`
        If you have a relation with a delete-orphan constraint that would complain
        that is not attached to anybody configure the Column adding in the info
        keyword the ``attach_instance`` key pointing to the property of the relation
        to be added.

        In the demo you can find this example::

          class Movie(Base):
              __tablename__  = 'movie'
              ...
              director_id    = Column(Integer, ForeignKey('director.id'), nullable=False,
                                      info={'attach_instance': 'director'})

          class Director(Base):
              __tablename__ = 'director'
              ...
              movies      = relation('Movie', backref='director', cascade='all, delete-orphan',)

        Attaching a director_id via completion, requires that you attach a director instance as well.

        """
        if not prop:
            return
        # if the backref that requires this is composed, probably things get more difficoult...
        assert len(prop.mapper.primary_key) ==1, "Sorry, sqlkit doesn't cope with composed primary key in relations with delete-orphan"

        q = self.master.session.query(prop.mapper).autoflush(False)
        obj = q.get(key)
        if self.master.is_mask():
            row_obj = self.master.current
        else:
            row_obj = self.master.get_selected_obj()
        setattr(row_obj, prop.key, obj)
        
class CollectionField(Field):
    """
    A field that manages a collection of objects
    Used in OneToMany or ManyToMany db fields.
    it's default widget is a collectionWidget that uses a SqlTable

    """
    Widget = 'CollectionWidget'

    def __init__(self, *args, **kwargs):
        Field.__init__(self, *args, **kwargs)
        self.initial_value = []

    def set_widget(self,  gtkwidget=None, def_str=None, widget=None):

        Field.set_widget(self,  gtkwidget=gtkwidget, def_str=def_str, widget=widget)
        self.widget.table.connect('after_commit', self.set_initial_value)
        
    def set_initial_value(self, widget, obj, session):
        """
        after_commit the 'new' initial value is the new value...
        """
        self.initial_value = widget.records

    def get_default(self):
        ## FIXME: is this always correct?
        return None

    def clean_value(self, value):
        from copy import copy
        
        if value is None:
            value = []
        return copy(value)

    def set_value(self, value, initial=True, shown=False, obj=None, update_widget=True):

        self.initial_value = self.clean_value(value)
        if value is None:
            value = []
        if hasattr(self, 'widget') and update_widget:
            self.widget.set_value(value)

        if obj and not initial:
            setattr(obj, self.field_name, value)

def std_cleanup(fn):
    """
    A decorator that will handle standard cases: value is None, is a string
    or is already cleaned.

    This is handy when building new Fields as it allows to keep the
    ``.clean_value`` method as simple as possible, i.e.  no need to check for
    standard cases::

        class CountMovies(fields.IntegerField):
            '''
            A field that counts the movies
            '''
            @fields.std_cleanup
            def clean_value(self, value):
                ## missing a field_name attribute on obj the object itselt is passed
                return len(value.movies)

    """
    def new_func(self, value):
        ## standard cleanup: values can
        if isinstance(value, (basestring, types.NoneType, self.type)) or \
               self.type == int and isinstance(value,long):
            return super(self.__class__, self).clean_value(value)
        ## custom one
        return fn(self, value)
    new_func.__doc__ = fn.__doc__
    return new_func
