# -*- coding: utf-8 -*-
"""Crud Dispatch Controllers"""

from tg import expose, flash, require, url, request, redirect, validate
from tg.decorators import paginate, with_trailing_slash
from formencode import validators
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons import tmpl_context, response
from repoze.what import predicates

from pyf.services.lib.base import BaseController
from pyf.services.model import DBSession, metadata
from pyf.services.controllers.error import ErrorController
from pyf.services import model
from pyf.services.model import (Dispatch, Tube, TubeLayer, Descriptor,
                             EventTrack, EventHistory,
                             EventOutputFile)

from tgext.crud import CrudRestController
from sprox.tablebase import TableBase
from sprox.formbase import AddRecordForm, EditableForm
from sprox.fillerbase import EditFormFiller

from pyf.services.controllers.crud import (SecureCrudRestController,
                                        DataGrid,
                                        render_boolean,
                                        render_link, render_link_field,
    has_model_permission)
from pyf.services.controllers.crud import FancyTableFiller as TableFiller

from pyf.services.core.events import create_event_track, get_logger
from pyf.services.core.router import Router
from pyf.services.core.storage import get_storage

from tgscheduler.scheduler import add_single_task

import operator
import itertools

import time

import transaction

import pylons

import os

def file2generator(f, size=(1024 * 20000)):
    while True:
        data = f.read(size) # Read blocks of 20M at a time
        if not data:
            break
        yield data

def get_tubes():
    query = DBSession.query(Tube).order_by(Tube.name.asc())
    tubes = list()
    for tube in query:
        tubes.append((tube.id, tube.name))
    tubes.sort(key=lambda x: x[1].lower())
    return tubes

def get_dispatchs():
    query = DBSession.query(Dispatch).order_by(Dispatch.display_name.asc())
    dispatchs = list()
    for dispatch in query:
        dispatchs.append((dispatch.id, dispatch.display_name))
    dispatchs.sort(key=lambda x: x[1].lower())
    return dispatchs

class EventTrackController(SecureCrudRestController):
    model = EventTrack
    __order_by__ = 'start_date'
    __desc__ = True
    
    class new_form_type(AddRecordForm):
        __model__ = EventTrack
        __omit_fields__ = ['id', 'tube_id', 'descriptor_id']

    class edit_form_type(EditableForm):
        __model__ = EventTrack
        __omit_fields__ = ['id', 'tube_id', 'descriptor_id']

    class edit_filler_type(EditFormFiller):
        __model__ = EventTrack

    class table_type(TableBase):
        __base_widget_type__ = DataGrid
#        __base_widget_type__ =  FilteringGrid
        __model__ = EventTrack
        __omit_fields__ = ['id', 'tube_id', 'dispatch_id',
                           'history', 'storage_file_uuid']
        __xml_fields__ = ['actions', 'tube', 'dispatch',
                          'progression']

    class table_filler_type(TableFiller):
        __model__ = EventTrack
        
        tube = render_link_field('/tubes/%s', 'tube', 'display_name',
                                 is_list=False)
        dispatch = render_link_field('/dispatchs/%s', 'dispatch',
                                     'display_name', is_list=False)
        
        def progression(self, obj):
            prog_text = "%d%%" % int(obj.progression or 0)
            tpl = """<div class="progressbar mini">
                <div id="test" class="progressbar-completed" style="width:%s;">
                    <div></div><p>%s</p>
                </div>
            </div>"""
            return tpl % (prog_text, prog_text)
        
        output_files = lambda controller, obj: str(len(obj.output_files or []))
        
        __actions__ = lambda x, y: "<a href='/events/%s'>View</a>" % y.id 
    
    @has_model_permission('view')
    @with_trailing_slash
    @paginate('value_list', items_per_page=20)
    @expose('pyf.services.templates.events.get_all')
    @expose('json')
    def get_all(self, *args, **kw):
        """Return all records.
           Pagination is done by offset/limit in the filler method.
           Returns an HTML page with the records if not json.
        """        
        query = DBSession.query(EventTrack)
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
            
        if kw.get('status'):
            query = query.filter(EventTrack.status==kw['status'])
        else:
            kw['status'] = ''
        
        if kw.get('tube_id'):
            kw['tube_id'] = int(kw['tube_id'])
            query = query.filter(EventTrack.tube_id==kw['tube_id'])
        else:
            kw['tube_id'] = ''
        
        if kw.get('dispatch_id'):
            kw['dispatch_id'] = int(kw['dispatch_id'])
            query = query.filter(EventTrack.dispatch_id==kw['dispatch_id'])
        else:
            kw['dispatch_id'] = ''
        
        if pylons.request.response_type == 'application/json':
            count = query.count()
            values = query.all()
            return dict(value_list = values, count = count)
        
        statuses = self.get_available_values_for_column('status')
        statuses.sort()
        
        tmpl_context.widget = self.table
        return dict(model=self.model.__name__, value_list=query,
                    statuses=statuses, tubes=get_tubes(), dispatchs=get_dispatchs(),
                    line_formater=self.table_filler.get_value_item,
                    kw=kw)
        
    @has_model_permission('view')
    @expose('pyf.services.templates.events.view_log')
    @expose('json')
    @paginate('messages', items_per_page=10)
    def get_one(self, eventtrack_id):
        eventtrack = DBSession.query(EventTrack).get(eventtrack_id)
        messages = DBSession.query(EventHistory)
        messages = messages.filter(EventHistory.eventtrack_id == eventtrack.id)
        messages = messages.order_by(EventHistory.timestamp.desc())
        
        if pylons.request.response_type == 'application/json':
            # pre fetching relations :)
            b = eventtrack.ordered_output_files
            c = eventtrack.history
            setattr(eventtrack, 'output_files', b)
            setattr(eventtrack, 'history', c)
            return dict(value=eventtrack)
        
        return dict(eventtrack=eventtrack,
                    messages=messages)
        
    @has_model_permission('view')
    @expose(content_type="application/x-download")
    def download_output(self, outputfile_id):
        if outputfile_id:
            outputfile = DBSession.query(EventOutputFile).get(outputfile_id)
            if outputfile:
                storage = get_storage('output')
                storage_filename = storage.get_filename(outputfile.file_uuid)
                fStat = os.stat(storage_filename)

                response.headers["Content-Type"] = "application/x-download"
                if outputfile.filename: 
                    response.headers["Content-Disposition"] =\
                     "attachment; filename=%s" % outputfile.filename
                    
                response.headers['Content-Length'] = int(fStat.st_size)
                f = open(storage_filename, 'rb')
                return file2generator(f)
        
    @has_model_permission('view')
    @expose(content_type="application/x-download")
    def download_input(self, eventtrack_id):
        eventtrack = DBSession.query(EventTrack).get(eventtrack_id)
        if eventtrack.storage_file_uuid:
            storage = get_storage('input')
            storage_filename = storage.get_filename(eventtrack.storage_file_uuid)
            fStat = os.stat(storage_filename)

            response.headers["Content-Type"] = "application/x-download"
            if eventtrack.source_filename: 
                response.headers["Content-Disposition"] =\
                     "attachment; filename=%s" % eventtrack.source_filename
                
            response.headers['Content-Length'] = int(fStat.st_size)
            f = open(storage_filename, 'rb')
            return file2generator(f)
