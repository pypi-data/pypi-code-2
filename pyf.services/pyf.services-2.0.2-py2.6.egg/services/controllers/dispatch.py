# -*- coding: utf-8 -*-
"""Crud Dispatch Controllers"""

from tg import expose, flash, require, url, request, redirect, validate
from formencode import validators
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from pylons import tmpl_context, request
from repoze.what import predicates

from pyf.services.lib.base import BaseController
from pyf.services.model import DBSession, metadata
from pyf.services.controllers.error import ErrorController
from pyf.services import model
from pyf.services.model import Dispatch, Tube, TubeLayer, Descriptor

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
from pyf.services.controllers.utils import tube_select_getter,\
    descriptor_select_getter
from pyf.services.controllers.widgets import DispatchLauncher

from pyf.services.core.events import create_event_track, get_logger
from pyf.services.core.router import Router

from pyf.services.core.storage import get_storage

from pyf.services.versionning.base import get_repository
from pyf.services.versionning.check import check_dispatch

from tw.forms import SingleSelectField

from tgscheduler.scheduler import add_single_task

import time

import transaction

import operator

import simplejson
from pylons.controllers.util import abort

def get_variants(tube):
    variants = list()
    for layer in tube.layers:
        if not layer.variant_name in variants:
            variants.append((layer.variant_name, layer.variant_name))
            
    variants.sort(key=operator.itemgetter(1))
    return variants

class DispatchController(SecureCrudRestController):
    model = Dispatch
    __order_by__ = 'display_name'
    __desc__ = False

    class new_form_type(AddRecordForm):
        __model__ = Dispatch
        __omit_fields__ = ['id', 'tube_id', 'descriptor_id']
        __field_order__ = ['name', 'display_name', 'descriptor', 'tube', 'variant_name', 'description']
        __hiden_fields__ = ['events']
        
        tube = SingleSelectField('tube',
                                 label_text="Tube",
                                 options=tube_select_getter(needs_source=True),
                                 not_empty=True)
        
        descriptor = SingleSelectField('descriptor',
                                       label_text="Descriptor",
                                       options=descriptor_select_getter,
                                       not_empty=True)
        

    class edit_form_type(EditableForm):
        __model__ = Dispatch
        __omit_fields__ = ['id', 'tube_id', 'descriptor_id']
        __field_order__ = ['name', 'display_name', 'descriptor', 'tube', 'variant_name', 'description']
        
        tube = SingleSelectField('tube',
                                 label_text="Tube",
                                 options=tube_select_getter(needs_source=True),
                                 not_empty=True)
        
        descriptor = SingleSelectField('descriptor',
                                       label_text="Descriptor",
                                       options=descriptor_select_getter,
                                       not_empty=True)

    class edit_filler_type(EditFormFiller):
        __model__ = Dispatch

    class table_type(TableBase):
        __base_widget_type__ = DataGrid
        __model__ = Dispatch
        __omit_fields__ = ['id', 'tube_id', 'descriptor_id', 'events']
        __xml_fields__ = ['actions', 'tube', 'descriptor']

    class table_filler_type(TableFiller):
        __model__ = Dispatch
        
        tube = render_link_field('/tubes/%s', 'tube', 'display_name',
                                 is_list=False)
        descriptor = render_link_field('/descriptors/%s/edit', 'descriptor',
                                       'display_name', is_list=False)
    
    @has_model_permission('view')
    @expose('pyf.services.templates.dispatch.get_one')
    @expose('json')
    def get_one(self, dispatch_id):
        dispatch = DBSession.query(Dispatch).get(dispatch_id)
        if request.response_type == 'application/json':
            return dict(value=dispatch)
            
        return dict(dispatch=dispatch,
                    variants=get_variants(dispatch.tube),
                    launcher=DispatchLauncher(dispatch.id))

    @has_model_permission('view')
    @expose('pyf.services.templates.dispatch.get_one')
    @expose('json')
    def by_name(self, name):
        dispatch = DBSession.query(Dispatch).filter(Dispatch.name==name).first()
        if dispatch is None:
            abort(404, comment="There is no dispatch with name %s" % name)
        return self.get_one(dispatch.id)

    @expose()
    @expose('json')
    @validate(validators={
            'doc': validators.FieldStorageUploadConverter(),
            'dispatch_id': validators.Int(not_none=True),
            'encoding': validators.String(),
            'variant': validators.UnicodeString()
    })
    def upload(self, dispatch_id, doc, variant=None, encoding=None, options=None, **kwargs):
        self.check_model_permission('launch')
        dispatch = DBSession.query(Dispatch).get(dispatch_id)
        router = Router(dispatch)
        
        if options is not None:
            options = simplejson.loads(options)

        if kwargs is not None:
            if options is not None:
                options.update(kwargs)
            else:
                options = kwargs
        
        if options is not None:
            valid_options = dispatch.tube.get_valid_options()
            
            for key in options:
                if key not in valid_options:
                    abort(403,  comment=("You can't set option %s" % key))

        # Trying to see if there is a newer version on the repo...
        repository = get_repository()
        check_dispatch(repository, dispatch, variant=variant)
        
        storage = get_storage('input')
        uuid = storage.store(doc.file)
        
        if variant == "no_variant":
            used_variant = None
        else:
            used_variant = variant or dispatch.variant_name or None

        used_encoding = encoding or dispatch.descriptor.default_encoding or None
        
        event_track = create_event_track(dispatch.tube,
                                         storage_file_uuid=uuid,
                                         source_filename=doc.filename,
                                         encoding=used_encoding,
                                         dispatch=dispatch,
                                         variant_name=used_variant)
        event_track_id = event_track.id
        logger = get_logger(event_track)
        logger.plug_on_event_source(router)
        
        user = model.User.by_user_name(request.identity['repoze.who.userid'])
        logger.info('Process started using dispatch %s (variant %s) by user %s (%s)' % (
                        dispatch.display_name, used_variant, user.user_name,
                        request.environ['REMOTE_ADDR']),
                        user=user, source=user.user_name)
        
        flash('Created event track %s' % event_track_id)
        transaction.commit()
        
        add_single_task(router.process_using_dispatch,
                        args=[doc.file],
                        kw=dict(variant=used_variant, encoding=used_encoding, options=options),
                        initialdelay=0)
        
        time.sleep(1)
        
        if request.response_type == 'application/json':
            return dict(event_track_id=event_track_id)
        
        redirect('/events/%s' % event_track_id)
                
#    def single_process(self, dispatch, doc_file):
#        files = dispatch.process_file(doc_file)
#        for file in files:
#            file = open(file, 'rb')
#            for line in file:
#                yield(line)
#            file.close()
