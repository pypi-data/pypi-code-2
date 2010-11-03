# -*- coding: utf-8 -*-
import os
os.chdir(os.path.dirname(__file__))

import json

import bottle
from bottle import route, send_file, abort
from bottle import MakoTemplate, mako_template as template
from mako import filters

import model
import pymongo
bottle.debug(True)

MakoTemplate.settings = {
    'input_encoding': 'utf-8',
    'output_encoding': 'utf-8',
}

@route('/static/:dir/:filename')
def static_file(dir, filename):
    send_file(filename, root='static/%s' % dir)

@route('/')
def home():
    dbs = model.conn.database_names()
    return template('databases', dbs=dbs)

@route('/:db_name')
def databases(db_name):
    if db_name not in model.conn.database_names():
        abort(404)

    db = model.conn[db_name]
    colls = db.collection_names()

    return template('collections', db=db_name, colls=colls)

@route('/filter/:db_name/:coll_name/:query')
@route('/filter/:db_name/:coll_name/:query/:skip/:limit')
def filter(db_name, coll_name, query, skip=0, limit=20):
    if db_name not in model.conn.database_names():
        abort(404)

    db = model.conn[db_name]

    if coll_name not in db.collection_names():
        abort(404)

    coll = db[coll_name]
    print query
    
    dquery = json.loads(query)

    # FIXME: quite crappy to put `int` here
    skip, limit = int(skip), int(limit)
    docs = coll.find(dquery, skip=skip, limit=limit).sort(
        [('_id', pymongo.DESCENDING)])

    count = docs.count()

    next_url = '/'.join(('filter',
        db_name, coll_name, query,
        str(skip + limit), str(limit)))

    return template('documents',
        db=db_name, coll=coll_name, docs=docs,
        count=count, skip=skip, limit=limit, next_url=next_url)

@route('/guess/:db_name/:id')
def guess(db_name, id):
    if db_name not in model.conn.database_names():
        abort(404)

    db = model.conn[db_name]
    colls = db.collection_names()
    obj_id = pymongo.objectid.ObjectId(id)

    docs = {}
    for coll in colls:
        doc = db[coll].find_one(obj_id)
        if doc:
            docs[coll] = doc
    
    return template('guess',
        db=db_name, docs=docs, count=len(docs))

@route('/:db_name/:coll_name')
@route('/:db_name/:coll_name/:skip/:limit')
def collections(db_name, coll_name, skip=0, limit=20):
    if db_name not in model.conn.database_names():
        abort(404)

    db = model.conn[db_name]

    if coll_name not in db.collection_names():
        abort(404)

    coll = db[coll_name]
    count = coll.count()

    # FIXME: quite crappy to put `int` here
    skip, limit = int(skip), int(limit)
    docs = coll.find(skip=skip, limit=limit).sort(
        [('_id', pymongo.DESCENDING)])

    next_url = '/'.join((db_name, coll_name, str(skip + limit), str(limit)))

    return template('documents',
        db=db_name, coll=coll_name, docs=docs,
        count=count, skip=skip, limit=limit, next_url=next_url)

