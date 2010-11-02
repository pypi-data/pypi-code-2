# Copyright (C) 2010 Joel Dunham
#
# This file is part of OnlineLinguisticDatabase.
#
# OnlineLinguisticDatabase is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OnlineLinguisticDatabase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OnlineLinguisticDatabase.  If not, see
# <http://www.gnu.org/licenses/>.

import logging
import datetime
import os
import re

from pylons import config
from pylons import request, response, session, app_globals, tmpl_context as c
from pylons import url
from pylons.controllers.util import abort, redirect, forward
from pylons.decorators import validate
from pylons.decorators.rest import restrict

import webhelpers.paginate as paginate

from formencode.schema import Schema
from formencode.validators import Invalid, FancyValidator
from formencode.validators import Int, DateConverter, UnicodeString, OneOf, Regex
from formencode import variabledecode
from formencode import htmlfill
from formencode.foreach import ForEach
from formencode.api import NoDefault
from sqlalchemy.sql import or_

from onlinelinguisticdatabase.lib.base import BaseController, render
import onlinelinguisticdatabase.model as model
import onlinelinguisticdatabase.model.meta as meta
import onlinelinguisticdatabase.lib.helpers as h

from sqlalchemy import desc

log = logging.getLogger(__name__)


class NewCollectionForm(Schema):
    """NewCollectionForm is a Schema for validating the data entered at the Add Collection page."""
    allow_extra_fields = True
    filter_extra_fields = True
    title = UnicodeString(not_empty=True)
    collectionType = UnicodeString()
    description = UnicodeString()
    speaker = UnicodeString()
    elicitor = UnicodeString()
    source = UnicodeString()
    dateElicited = DateConverter(month_style='mm/dd/yyyy')
    contents = UnicodeString()

class UpdateCollectionForm(NewCollectionForm):
    ID = UnicodeString()

class RestrictorStruct(Schema):
    location = UnicodeString()
    containsNot = UnicodeString()
    allAnyOf = UnicodeString
    options = ForEach(UnicodeString())

class DateRestrictorStruct(Schema):
    location = UnicodeString()
    relation = UnicodeString()
    date = DateConverter(month_style='mm/dd/yyyy')

class IntegerRestrictorStruct(Schema):
    location = UnicodeString()
    relation = UnicodeString()
    integer = UnicodeString()
    unit = UnicodeString()

class SearchCollectionForm(Schema):
    """SearchCollection is a Schema for validating the search terms entered at the Search Collections page."""
    allow_extra_fields = True
    filter_extra_fields = True
    searchTerm1 = UnicodeString()
    searchType1 = UnicodeString()
    searchLocation1 = UnicodeString()
    searchTerm2 = UnicodeString()
    searchType2 = UnicodeString()
    searchLocation2 = UnicodeString()
    andOrNot = UnicodeString()
    restrictors = ForEach(RestrictorStruct())
    dateRestrictors = ForEach(DateRestrictorStruct())
    integerRestrictors = ForEach(IntegerRestrictorStruct())
    orderByColumn = UnicodeString()
    orderByDirection = UnicodeString()

class AssociateCollectionFileForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    fileID = Regex(r'^ *[1-9]+[0-9]* *( *, *[1-9]+[0-9]* *)*$', not_empty=True)

def renderAddCollection(values=None, errors=None, addUpdate='add'):
    """Function is called by both the add and update actions to create the
    Add Collection and Update Collection HTML forms.  The create and save actions can also
    call this function if any errors are present in the input."""
    # if addUpdate is set to 'update', render update.html instead of add.html
    if addUpdate == 'add':
        html = render('/derived/collection/add.html')
    else:
        html = render('/derived/collection/update.html')
    
    return htmlfill.render(html, defaults=values, errors=errors)


def getCollectionAttributes(collection, result, createOrSave):
    """Given a (SQLAlchemy) Collection object and a result dictionary populated by
    user-entered data, this function populates the appropriate attributes with the 
    appropriate values.  Function called by both create and save actions."""
    # User-entered Data
    collection.title = result['title']
    collection.type = result['collectionType']
    collection.description = result['description']
    if result['speaker']:
        collection.speaker = meta.Session.query(model.Speaker).get(int(result['speaker']))
    if result['elicitor']:
        collection.elicitor = meta.Session.query(model.User).get(int(result['elicitor']))
    if result['source']:
        collection.source = meta.Session.query(model.Source).get(int(result['source']))
    if result['dateElicited']:
        collection.dateElicited = result['dateElicited']
    # OLD-generated Data
    now = datetime.datetime.now()
    if createOrSave == 'create':
        collection.datetimeEntered = now
    collection.datetimeModified = now
    # Add the Enterer as the current user
    collection.enterer = meta.Session.query(model.User).get(int(session['user_id']))
    # Extract component Forms from collection contents
    collection.forms = []
    collection.contents = result['contents']
    patt = re.compile('form\[([0-9]+)\]')
    formIDs = patt.findall(collection.contents)
    for formID in formIDs:
        form = meta.Session.query(model.Form).get(int(formID))
        if form:
            collection.forms.append(form)
    return collection


class CollectionController(BaseController):
    """Collection Controller contains actions about OLD Collections.
    Authorization and authentication are implemented by the
    helper decorators authenticate and authorize which can be
    found in lib/auth.py."""

    @h.authenticate
    def browse(self):
        """Browse through all Collections in the system."""
        collection_q = meta.Session.query(model.Collection).order_by(model.Collection.title)
        c.paginator = paginate.Page(
            collection_q,
            page=int(request.params.get('page', 1)),
            items_per_page = app_globals.collection_items_per_page
        )
        c.browsing = True
        return render('/derived/collection/results.html')

    @h.authenticate
    def view(self, id, option=None):
        """View a BLD Collection.  Requires a Collection ID as input."""
        if id is None:
            abort(404)
        collection_q = meta.Session.query(model.Collection)
        try:
            c.collection = collection_q.get(int(id))
        except ValueError:
            abort(404)
        if option and option in ['long', 'short', 'columns']:
            c.collectionViewType = option
        else:
            c.collectionViewType = session['user_collectionViewType']
        if c.collection is None:
            abort(404)
        return render('/derived/collection/view.html')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def add(self):
        """Display HTML form for adding a new BLD Collection.
        HTML form calls create action."""
        return renderAddCollection()

    @h.authenticate
    def search(self, values=None, errors=None):
        """Display HTML form for searching for BLD Collections.
        HTML form calls query action."""
        # if no user-entered defaults are set, make gloss the default for searchLocation2
        if not values:
            values = {'searchLocation2': u'description'}
            values['orderByColumn'] = 'id'
        # By default, the additional search restrictors are hidden
        c.viewRestrictors = False
        # Get today in MM/DD/YYYY collection    
        c.today = datetime.date.today().strftime('%m/%d/%Y')
        html = render('/derived/collection/search.html')      
        return htmlfill.render(html, defaults=values, errors=errors)

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    @restrict('POST')
    def create(self):
        """Enter BLD Collection data into the database.
        This is the action referenced by the HTML form
        rendered by the add action."""
        schema = NewCollectionForm()
        values = dict(request.params)
        try:
            result = schema.to_python(dict(request.params), c)
        except Invalid, e:
            return renderAddCollection(
                values=values,
                errors=variabledecode.variable_encode(
                    e.unpack_errors() or {},
                    add_repetitions=False
                )
            )
        else:
            # Create a new Collection SQLAlchemy Object and populate its attributes with the results
            collection = model.Collection()
            collection = getCollectionAttributes(collection, result, 'create')
            # Enter the data
            meta.Session.add(collection)
            meta.Session.commit()
            # Issue an HTTP redirect
            redirect(url(controller='collection', action='view', id=collection.id))

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def getmemory(self):
        """Insert references to Forms in Memory into the content field of
        the Collection being added or updated."""
        values = dict(request.params)
        # Get all Forms that user has memorized ordered by Form ID 
        #  by using the 'memorizers' backreference
        user = meta.Session.query(model.User).filter(model.User.id==session['user_id']).first()
        rememberedForms = meta.Session.query(model.Form).order_by(model.Form.id).filter(model.Form.memorizers.contains(user)).all()         
        rememberedFormIDs = ['form[%s]' % form.id for form in rememberedForms]
        return '\n'.join(rememberedFormIDs)

    @h.authenticate
    @restrict('POST')
    def query(self):
        """Query action validates the search input values; 
        if valid, query stores the search input values in the session and redirects to results;
        if invalid, query redirect to search action (though I don't think it's possible to enter an invalid query...).  
        Query is the action referenced by the HTML form rendered by the search action."""
        schema = SearchCollectionForm()
        values = dict(request.params)
        try:
            result = schema.to_python(dict(request.params), c)
        except Invalid, e:
            return self.search(
                values=values,
                errors=variabledecode.variable_encode(
                    e.unpack_errors() or {},
                    add_repetitions=False
                )
            )
        else:
            # result is a Python dict nested structure representing the user's query
            # we put result into session['collectionSearchValues'] so that the results action
            # can use it to build the SQLAlchemy query
            session['collectionSearchValues'] = result
            session.save() 
            # Issue an HTTP redirect
            response.status_int = 302
            response.headers['location'] = url(controller='collection', action='results')
            return "Moved temporarily"

    @h.authenticate
    def results(self):
        """Results action uses the filterSearchQuery helper function to build
        a query based on the values entered by the user in the search collection."""
        collection_q = meta.Session.query(model.Collection)
        if 'collectionSearchValues' in session:
            result = session['collectionSearchValues']
            collection_q = h.filterSearchQuery(result, collection_q, 'Collection')
        c.paginator = paginate.Page(
            collection_q,
            page=int(request.params.get('page', 1)),
            items_per_page = app_globals.collection_items_per_page
        )
        return render('/derived/collection/results.html')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def update(self, id=None):
        """Displays an HTML form for updating a BLD Collection.
        HTML form calls save action."""
        if id is None:
            abort(404)
        collection_q = meta.Session.query(model.Collection)
        collection = collection_q.filter_by(id=id).first()
        if collection is None:
            abort(404)
        c.collection = collection
        values = {
            'ID': collection.id,
            'title': collection.title,
            'type': collection.type,
            'description': collection.description,
            'elicitor': collection.elicitor_id,
            'speaker': collection.speaker_id,
            'source': collection.source_id,
            'contents': collection.contents
        }
        if collection.dateElicited:
            values['dateElicited'] = collection.dateElicited.strftime('%m/%d/%Y')
        return renderAddCollection(values, None, 'update')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    @restrict('POST')
    def save(self):
        """Updates existing BLD Collection.
        This is the action referenced by the HTML form
        rendered by the update action."""
        schema = UpdateCollectionForm()
        values = dict(request.params)
        try:
            result = schema.to_python(dict(request.params), c)
        except Invalid, e:
            c.id = values['ID']
            return renderAddCollection(
                values=values,
                errors=variabledecode.variable_encode(
                    e.unpack_errors() or {},
                    add_repetitions=False
                ),
                addUpdate='update'
            )
        else:
            # Get the Collection object with ID from hidden field in update.html
            collection_q = meta.Session.query(model.Collection)
            collection = collection_q.filter_by(id=result['ID']).first()
            # Populate the Collection's attributes with the data from the user-entered result dict
            collection = getCollectionAttributes(collection, result, 'save')
            # Commit the update
            meta.Session.commit()
            # Issue an HTTP redirect
            response.status_int = 302
            response.headers['location'] = url(controller='collection', action='view', id=collection.id)
            return "Moved temporarily" 

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def delete(self, id):
        """Delete the BLD collection with ID=id."""
        if id is None:
            abort(404)
        collection_q = meta.Session.query(model.Collection)
        collection = collection_q.get(int(id))
        if collection is None:
            print '\n\nNo collection!!!\n\n\n'
            abort(404)
        # Delete Collection info in database
        meta.Session.delete(collection)
        meta.Session.commit()
        # Create the flash message
        session['flash'] = "Collection %s has been deleted" % id
        session.save()
        redirect(url(controller='collection', action='results'))

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def associate(self, id):
        """Display the page for associating a BLD Collection with id=id 
        to a BLD File.  The HTML form in the rendered page ultimately
        references the link action."""
        if id is None:
            abort(404)
        c.collection = meta.Session.query(model.Collection).get(int(id))  
        if c.collection is None:
            abort(404)   
        return render('/derived/collection/associate.html')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    @restrict('POST')
    @validate(schema=AssociateCollectionFileForm(), form='associate')
    def link(self, id):
        """Associate BLD Collection with id=id to a BLD File.  The ID of the 
        File is passed via a POST form.  This "ID" may in fact be a 
        comma-separated list of File IDs."""
        # Get the Form
        if id is None:
            abort(404)
        collection = meta.Session.query(model.Collection).get(int(id))  
        if collection is None:
            abort(404)
        # Get the File(s)   
        fileID = self.form_result['fileID']
        patt = re.compile('^[0-9 ]+$')
        fileIDs = [ID.strip().replace(' ', '') for ID in fileID.split(',') if patt.match(ID)]
        file_q = meta.Session.query(model.File)
        filterString = 'or_(' + ', '.join(['model.File.id==%s' % ID for ID in fileIDs]) + ')'
        filterString = 'file_q.filter(%s)' % filterString
        cmd = "file_q = eval('%s' % filterString)"
        exec(cmd)
        files = file_q.all()
        if files:
            for file in files:
                if file in collection.files:
                    if 'flash' in session:
                        session['flash'] += 'File %s is already associated to Collection %s ' % (file.id, collection.id)
                    else:
                        session['flash'] = 'File %s is already associated to Collection %s ' % (file.id, collection.id)
                else:
                    collection.files.append(file)
            meta.Session.commit()
            session.save()
        else:
            session['flash'] = u'Sorry, no Files have any of the following IDs: %s' % fileID
            session.save()
        return redirect(url(controller='collection', action='view', id=collection.id))

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def disassociate(self, id, otherID):
        """Disassociate BLD Collection id from BLD File otherID."""
        if id is None or otherID is None:
            abort(404)
        collection = meta.Session.query(model.Collection).get(int(id)) 
        file = meta.Session.query(model.File).get(int(otherID)) 
        if file is None:
            if collection is None:
                abort(404)
            else:
                session['flash'] = 'There is no File with ID %s' % otherID
        if file in collection.files:
            collection.files.remove(file)
            meta.Session.commit()
            session['flash'] = 'File %s disassociated' % otherID
        else:
            session['flash'] = 'Collection %s was never associated to File %s' % (id, otherID)
        session.save()
        redirect(url(controller='collection', action='view', id=id))

    @h.authenticate
    def export(self, id=None):
        return 'NO COLLECTION EXPORT YET'
