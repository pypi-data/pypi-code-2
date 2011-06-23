# -*- coding: utf-8 -*-
"""Crud Dispatch Controllers"""

from tg import expose, flash, redirect, validate, tmpl_context
from tg.decorators import without_trailing_slash
from formencode import validators

from pyf.services.model import DBSession
from pyf.services.model import (TubeTask, Tube)

from sprox.tablebase import TableBase

from pyf.services.controllers.crud import (SecureCrudRestController,
                                        DataGrid,
                                        render_boolean, render_link_field,
                                     has_model_permission)
from pyf.services.controllers.crud import FancyTableFiller as TableFiller
from pyf.services.controllers.utils import tube_select_getter

from tw.forms import (TextField, CheckBoxList, MultipleSelectField,
                      SingleSelectField, HiddenField)
from tw import dynforms as twd

from tg.i18n import get_lang
from tw.forms.fields import CheckBox
from tw.api import WidgetsList
import babel

import logging
logger = logging.getLogger()

def get_weekdays():
    locale = babel.Locale.parse(get_lang() or 'en')
    days = locale.days['stand-alone']['wide']
    return [(i+1, days[i]) for i in range(7)]

class TaskForm(twd.HidingTableForm):
    
    class fields(WidgetsList):
        id = HiddenField('id', validator=validators.Int())
        
        display_name = TextField('display_name', not_none=True)
        
        active = CheckBox('active', validator=validators.Bool(default=False))
        
        tube_id = SingleSelectField('tube_id',
                                    label_text="Tube",
                                    options=tube_select_getter(needs_source=False),
                                    not_empty=True)
        
        variant_name = TextField('variant_name')
        
        type = SingleSelectField('type',
                                 label_text="Repeat type",
                                 options=[('weekdays', 'Week Days'),
                                          ('monthdays', 'Month Days'),
                                          ('interval', 'Interval')])
        
        weekdays = CheckBoxList('weekdays', label_text="Week Days",
                                options=get_weekdays)
        monthdays = MultipleSelectField('monthdays', label_text="Month Days",
                                        options=range(1, 32))
        timeofday = TextField('timeofday', label_text="Time of Day",
                              help_text="Expressed as HH:MM")
        interval = TextField('interval', label_text="Interval",
                             help_text="Expressed in seconds")

class TaskController(SecureCrudRestController):
    model = TubeTask
    __order_by__ = 'display_name'
    __desc__ = False

    class table_type(TableBase):
        __base_widget_type__ = DataGrid
        __model__ = TubeTask
        __omit_fields__ = ['id', 'tube_id']
        __xml_fields__ = ['tube', 'active']

    class table_filler_type(TableFiller):
        __model__ = TubeTask
        
        tube = render_link_field('/tubes/%s', 'tube', 'display_name',
                                 is_list=False)
        active = render_boolean('active')
    
    form = TaskForm()
    
    @has_model_permission('edit')
    @expose('pyf.services.templates.tasks.edit')
    def edit(self, task_id, *args, **kw):
        tmpl_context.widget = self.form
        
        task = DBSession.query(TubeTask).get(int(task_id))
        if task is None:
            flash('task not found !')
            redirect('../')
        
        vals = dict(id=task.id,
                    display_name=task.display_name,
                    variant_name=task.variant_name,
                    active=task.active,
                    tube_id=task.tube_id,
                    type=task.type)
        
        if vals['type'] == 'interval':
            vals['interval'] = task.time
        elif vals['type'] == 'weekdays':
            vals['timeofday'] = task.time
            vals['weekdays'] = map(int, task.days.split(','))
        elif vals['type'] == 'monthdays':
            vals['timeofday'] = task.time
            vals['monthdays'] = map(int, task.days.split(','))
        
        vals.update(kw)
        
        return dict(value=vals)
    
    @has_model_permission('create')
    @without_trailing_slash
    @expose('pyf.services.templates.tasks.edit')
    def new(self, *args, **kw):
        value = dict()
        tmpl_context.widget = self.form
        return dict(value=value)
    
    @without_trailing_slash
    @expose()
    @validate(form, error_handler=edit)
    def post(self, *args, **kw):
        self.check_model_permission('create')
        vals = dict()
        vals['type'] = kw['type']
        if vals['type'] == 'interval':
            vals['time'] = kw['interval']
        elif vals['type'] == 'weekdays':
            vals['time'] = kw['timeofday']
            vals['days'] = ','.join(kw['weekdays'])
        elif vals['type'] == 'monthdays':
            vals['time'] = kw['timeofday']
            vals['days'] = ','.join(kw['monthdays'])
            
        vals['tube_id'] = kw['tube_id']
        vals['display_name'] = kw['display_name']
        vals['variant_name'] = kw['variant_name']
        vals['active'] = kw['active']
        
        task = None
        if 'id' in kw and kw['id'] is not None:
            task = DBSession.query(TubeTask).get(kw['id'])
            if not task:
                flash('task not found !', "error")
                redirect('./')
            
            for key, value in vals.iteritems():
                setattr(task, key, value)
                
        else:
            task = TubeTask(**vals)
        
        DBSession.add(task)
        DBSession.flush()
        
        try:
            task.schedule()
            flash('Task #%s saved and (re)scheduled successfully.' % task.id)
        except Exception, e:
            logger.exception(e)
            flash('Task was saved but not scheduled: "%s".' % str(e), "warning")
        
        redirect('/tasks')