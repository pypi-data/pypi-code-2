# -*- coding: utf-8 -*-
"""Crud Tube Layer Controllers"""

from tg import expose, flash, require, request, redirect, validate
from formencode import validators
from pylons import tmpl_context

from pyf.services.model import DBSession
from pyf.services import model
from pyf.services.model import Tube, TubeLayer

from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller

from pyf.services.controllers.crud import (SecureCrudRestController, DataGrid,
                                        render_boolean, render_link_field,
    has_model_permission)
from pyf.services.controllers.crud import FancyTableFiller as TableFiller
from pyf.services.controllers.utils import tube_select_getter

from pyf.services.core.events import create_event_track, get_logger
from pyf.services.core.router import Router
from pyf.services.core.tasks import launch_tube

from tw.forms import SingleSelectField
from tg.decorators import with_trailing_slash, paginate, override_template

from tgscheduler.scheduler import add_single_task

import operator

import transaction
import time

import pylons

class TubeLayerTable(TableBase):
    __base_widget_type__ = DataGrid
    __model__ = TubeLayer
    __omit_fields__ = ['id', 'payload', 'description', 'tube_id']
    __xml_fields__ = ['actions', 'tube', 'active']
tubelayer_table = TubeLayerTable(DBSession)

class TubeLayerTableFiller(TableFiller):
    __model__ = TubeLayer
    __base_url__ = '/tubelayers/'
    def _do_get_provider_count_and_objs(self, tube=None, **kw):
        layers = DBSession.query(TubeLayer)
        if tube:
            layers = layers.filter(TubeLayer.tube==tube)
            
        layers = layers.all()
        return len(layers), layers
    
    tube = render_link_field('/tubes/%s', 'tube', 'display_name', is_list=False)
    active = render_boolean('active')
    
tubelayer_table_filler = TubeLayerTableFiller(DBSession)

class TubeLayerController(SecureCrudRestController):
    model = TubeLayer
    __post_to_versionning__ = True
    __order_by__ = 'name'
    __desc__ = False

    class new_form_type(AddRecordForm):
        __model__ = TubeLayer
        __omit_fields__ = ['dispatchs', 'layers', 'tube_id', 'id']
        __field_order__ = ['name', 'display_name', 'active', 'tube', 'variant_name',
                           'priority', 'description', 'payload']
        
        tube = SingleSelectField('tube',
                                 label_text="Tube",
                                 options=tube_select_getter(),
                                 not_empty=True)

    class edit_form_type(EditableForm):
        __model__ = TubeLayer
        __omit_fields__ = ['dispatchs', 'layers', 'tube_id', 'id']
        __field_order__ = ['name', 'display_name', 'active', 'tube', 'variant_name',
                           'priority', 'description', 'payload']
        
        tube = SingleSelectField('tube',
                                 label_text="Tube",
                                 options=tube_select_getter(),
                                 not_empty=True)

    class edit_filler_type(EditFormFiller):
        __model__ = TubeLayer
    
    @has_model_permission('edit')
    @expose('pyf.services.templates.tubelayer.edit')
    def edit(self, *args, **kwargs):
        return SecureCrudRestController.edit(self, *args, **kwargs)
    
    @has_model_permission('create')
    @expose('pyf.services.templates.tubelayer.edit')
    def new(self, *args, **kwargs):
        return SecureCrudRestController.new(self, *args, **kwargs)
    
    @has_model_permission('view')
    @with_trailing_slash
    @paginate('value_list', items_per_page=20)
    @expose('pyf.services.templates.tubelayer.get_all')
    @expose('json')
    def get_all(self, *args, **kw):
        """Return all records.
           Pagination is done by offset/limit in the filler method.
           Returns an HTML page with the records if not json.
        """        
        query = DBSession.query(TubeLayer)
        kw = kw.copy()
        if 'order_by' not in kw and self.__order_by__ is not None:
            kw['order_by'] = self.__order_by__
        if 'desc' not in kw and self.__desc__ is not None:
            kw['desc'] = self.__desc__
        
        if kw['order_by']:
            col = getattr(self.model, kw['order_by'])
            if kw['desc'] and not kw['desc'] == 'False':
                col = col.desc()
            query = query.order_by(col)
            
        if kw.get('variant_name'):
            query = query.filter(TubeLayer.variant_name==kw['variant_name'])
        else:
            kw['variant_name'] = ''
        
        if kw.get('tube_id'):
            kw['tube_id'] = int(kw['tube_id'])
            query = query.filter(TubeLayer.tube_id==kw['tube_id'])
        else:
            kw['tube_id'] = ''
        
        if pylons.request.response_type == 'application/json':
            count = query.count()
            values = query.all()
            return dict(value_list = values, count = count)
        
        variant_names = self.get_available_values_for_column('variant_name')
        variant_names.sort()
        
        tmpl_context.widget = self.table
        return dict(model=self.model.__name__, value_list=query,
                    variant_names=variant_names, tubes=tube_select_getter()(),
                    line_formater=self.table_filler.get_value_item,
                    kw=kw)

    table = tubelayer_table
    table_filler = tubelayer_table_filler
