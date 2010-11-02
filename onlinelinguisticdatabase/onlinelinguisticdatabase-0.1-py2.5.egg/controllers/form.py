# −*− coding: UTF−8 −*−

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

try:
    import json
except ImportError:
    import simplejson as json

from pylons import request, response, session, app_globals, tmpl_context as c
from pylons import url
from pylons.controllers.util import abort, redirect
from pylons.decorators import validate
from pylons.decorators.rest import restrict

import webhelpers.paginate as paginate

from formencode.schema import Schema
from formencode.validators import Invalid, FancyValidator
from formencode.validators import Int, DateConverter, UnicodeString, OneOf, Regex
from formencode import variabledecode
from formencode import htmlfill, All
from formencode.foreach import ForEach
from formencode.api import NoDefault

from sqlalchemy.sql import or_

from onlinelinguisticdatabase.lib.base import BaseController, render
import onlinelinguisticdatabase.model as model
import onlinelinguisticdatabase.model.meta as meta
import onlinelinguisticdatabase.lib.helpers as h

from sqlalchemy import desc

log = logging.getLogger(__name__)


class FirstGlossNotEmpty(FancyValidator):
    """
    Custom validator.  Ensures that the first gloss field, 'gloss-0.text',
    has some content.
    """
    messages = {
        'one_gloss': 'Please enter a gloss in the first gloss field'
    }
    def validate_python(self, value, state):
        if value[0]['gloss'] == '':
            raise Invalid(self.message("one_gloss", state), value, state)

class Keyword(Schema):
    """Keyword validator ensures that keywords are unicode strings."""
    keyword = UnicodeString()

class NewFormForm(Schema):
    """NewFormForm is a Schema for validating the data entered at the Add Form page."""
    allow_extra_fields = True
    filter_extra_fields = True
    pre_validators = [variabledecode.NestedVariables()]
    """
    tChars = obj_lang.orthographs + [' ']
    mbChars = obj_lang.orthographs + app_globals.validDelimiters + [' ']
    tRegex = r'^(%s)*$' % '|'.join(tChars)
    mbRegex = r'^(%s)*$' % '|'.join(mbChars)
    transcription = All(UnicodeString(not_empty=True, messages={'empty':'Please enter a transcription.'}), Regex(tRegex, messages={'invalid': 'Sorry, the transcription contains invalid characters.'}))
    morphemeBreak = All(UnicodeString(), Regex(mbRegex, messages={'invalid': 'Sorry, the morpheme break contains invalid characters'}))
    """
    transcription = UnicodeString(not_empty=True, messages={'empty':'Please enter a transcription.'})
    morphemeBreak = UnicodeString()
    grammaticality = UnicodeString()
    morphemeGloss = UnicodeString()
    glosses = FirstGlossNotEmpty()
    comments = UnicodeString()
    speakerComments = UnicodeString()
    elicitationMethod = UnicodeString()
    keywords = ForEach(Keyword())
    syntacticCategory = UnicodeString()    
    speaker = UnicodeString()
    elicitor = UnicodeString()
    verifier = UnicodeString()
    source = UnicodeString()
    dateElicited = DateConverter(month_style='mm/dd/yyyy')

class UpdateFormForm(NewFormForm):
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

class SearchFormForm(Schema):
    """SearchForm is a Schema for validating the search terms entered at the Search Forms page."""
    allow_extra_fields = True
    filter_extra_fields = True
    pre_validators = [variabledecode.NestedVariables()]
    searchTerm1 = UnicodeString()
    searchType1 = UnicodeString()
    searchLocation1 = UnicodeString()
    searchTerm2 = UnicodeString()
    searchType2 = UnicodeString()
    searchLocation2 = UnicodeString()
    andOrNot = UnicodeString()
    restrictors = ForEach(RestrictorStruct())
    dateRestrictors = ForEach(DateRestrictorStruct())
    orderByColumn = UnicodeString()
    orderByDirection = UnicodeString()

class AssociateFormFileForm(Schema):
    allow_extra_fields = True
    filter_extra_fields = True
    fileID = Regex(r'^ *[1-9]+[0-9]* *( *, *[1-9]+[0-9]* *)*$', not_empty=True)

def renderAddForm(values=None, errors=None, addUpdate='add'):
    """Function is called by both the add and update actions to create the
    Add Form and Update Form html forms.  The create and save actions can also
    call this function if any errors are present in the input."""

    c.transcriptionKeyboardTable = h.getKeyboardTable('transcription')
    c.morphemeBreakKeyboardTable = h.getKeyboardTable('morphemeBreak')

    # if addUpdate is set to 'update', render update.html instead of add.html
    html = render('/derived/form/add.html')
    if addUpdate == 'update':
        html = render('/derived/form/update.html')
    # Replace 'glosses' with 'glosses-0.gloss' in errors dict
    # so that error messages are put in the proper place
    if errors and 'glosses' in errors:
        errors['glosses-0.gloss'] = errors['glosses']
        del errors['glosses']     
    return htmlfill.render(html, defaults=values, errors=errors)

def getMorphemeIDLists(form):
    """This function takes morpheme-gloss components of a Form and looks for matches
    in other Forms.
    
    Specifically, it looks for Forms whose transcription matches the morpheme string and 
    whose morphemeGloss matches the gloss string.  First it looks for perfect matches
    (i.e., a Form whose morphemeBreak matches the morpheme and whose morphemeGloss
    matches the gloss) and if none are found it looks for "half-matches" and if none
    of those are found, then form.morhemeBreakIDs and form.morhemeGlossIDs are empty lists.

    If any kind of match is found, the id, morpheme/gloss and syntactic category of the
    matching Forms are stored in a list of tuples: (id, mb/gl, sc)."""
    morphemeBreakIDs = []
    morphemeGlossIDs = []
    syncatStr = []
    validDelimiters = app_globals.validDelimiters
    patt = '[%s]' % ''.join(validDelimiters + [' '])
    if form.morphemeBreak and form.morphemeGloss and len(re.split(patt, form.morphemeBreak)) == len(re.split(patt, form.morphemeGloss)):
        morphemeBreak = form.morphemeBreak
        morphemeGloss = form.morphemeGloss
        mbWords = morphemeBreak.split()
        mgWords = morphemeGloss.split()
        scWords = morphemeBreak.split()[:]
        for i in range(len(mbWords)):
            mbWordIDList = []
            mgWordIDList = []
            mbWord = mbWords[i]
            mgWord = mgWords[i]
            scWord = scWords[i]             
            patt = '([%s])' % ''.join(validDelimiters)
            mbWordMorphemesList = re.split(patt, mbWord)[::2] 
            mgWordMorphemesList = re.split(patt, mgWord)[::2]
            scWordMorphemesList = re.split(patt, scWord)
            for ii in range(len(mbWordMorphemesList)):
                morpheme = mbWordMorphemesList[ii]
                gloss = mgWordMorphemesList[ii]
                matches = meta.Session.query(model.Form).filter(model.Form.morphemeBreak==morpheme).filter(model.Form.morphemeGloss==gloss).all()
                # If one or more Forms match both gloss and morpheme, append a list of the IDs
                # of those Forms in morphemeBreakIDs and morphemeGlossIDs
                if matches:
                    mbWordIDList.append([f.syntacticCategory and (f.id, f.morphemeGloss, f.syntacticCategory.name) 
                        or (f.id, f.morphemeGloss, None) for f in matches])
                    mgWordIDList.append([f.syntacticCategory and (f.id, f.morphemeBreak, f.syntacticCategory.name) 
                        or (f.id, f.morphemeBreak, None) for f in matches])
                    scWordMorphemesList[ii * 2] = matches[0].syntacticCategory and matches[0].syntacticCategory.name or '?'
                # Otherwise, look for Forms that match only gloss or only morpheme and append respectively
                else:
                    morphemeMatches = meta.Session.query(model.Form).filter(model.Form.morphemeBreak==morpheme).all()
                    if morphemeMatches:
                        mbWordIDList.append([f.syntacticCategory and (f.id, f.morphemeGloss, f.syntacticCategory.name) 
                            or (f.id, f.morphemeGloss, None) for f in morphemeMatches])
                    else:
                        mbWordIDList.append([])
                    glossMatches = meta.Session.query(model.Form).filter(model.Form.morphemeGloss==gloss).all()
                    if glossMatches:
                        mgWordIDList.append([f.syntacticCategory and (f.id, f.morphemeBreak, f.syntacticCategory.name) 
                            or (f.id, f.morphemeBreak, None) for f in glossMatches])
                    else:
                        mgWordIDList.append([])
                    scWordMorphemesList[ii * 2] = '?'
            morphemeBreakIDs.append(mbWordIDList)
            morphemeGlossIDs.append(mgWordIDList)
            syncatStr.append(''.join(scWordMorphemesList))
    else:
        morphemeBreakIDs = [[[]]]
        morphemeGlossIDs = [[[]]]
        syncatStr = []
    # Convert the data structure into JSON for storage as a string in the DB
    form.morphemeBreakIDs = unicode(json.dumps(morphemeBreakIDs))
    form.morphemeGlossIDs = unicode(json.dumps(morphemeGlossIDs))
    form.syntacticCategoryString = unicode(' '.join(syncatStr))


def getFormAttributes(form, result, createOrSave):
    """Given a Form object and a result dictionary populated by
    user-entered data, this action populates the appropriate attributes with the
    appropriate values.  
    
    This function is called by both create() and save() actions.
    
    Note: the values entered into the transcription and morphemeBreak fields
    are converted from the input orthography to the storage orthography using
    the functions.inputToStorageTranslate function.  <obl>-prefixed and
    </obl>-suffixed substrings of the values entered into the comments and
    speakerComments fields are converted from the input orthography to the
    storage orthography using the functions.inputToStorageTranslateOLOnly
    function.  See the lib/functions and lib/orthography modules for details.
    """
    # Textual Data
    form.transcription = h.inputToStorageTranslate(
        unicode(h.removeWhiteSpace(result['transcription'])))
    #form.phoneticTranscription = result['phoneticTranscription']
    form.morphemeBreak = h.inputToStorageTranslate(
        h.removeWhiteSpace(result['morphemeBreak']), True)
    form.morphemeGloss = h.removeWhiteSpace(result['morphemeGloss'])
    form.comments = h.inputToStorageTranslateOLOnly(result['comments'])
    form.speakerComments = h.inputToStorageTranslateOLOnly(
        result['speakerComments'])
    form.grammaticality = result['grammaticality']
    form.dateElicited = result['dateElicited']
    print '\n\n\n%s\n\n\n' % type(form.dateElicited)
    # One-to-Many Data: Glosses
    # First check if the user has made any changes to the glosses.
    # If there are any changes, just delete all glosses and replace with new ones
    #  (note: this will result in the deletion of a gloss and the recreation of an identical one
    #  with a different index.  There may be a "better" way of doing this, but this way is simple...
    glossesToAdd = [[gloss['gloss'], gloss['grammaticality']] for gloss in result['glosses'] if gloss['gloss']]
    glossesWeHave = [[gloss.gloss, gloss.glossGrammaticality] for gloss in form.glosses]
    if glossesToAdd != glossesWeHave:
        form.glosses = []
        for gloss in glossesToAdd:
            glossObject = model.Gloss()
            glossObject.gloss = h.removeWhiteSpace(gloss[0])
            glossObject.glossGrammaticality = gloss[1]
            form.glosses.append(glossObject)
    
    # Many-to-One Data
    
    if result['elicitationMethod']:
        form.elicitationMethod = meta.Session.query(
            model.ElicitationMethod).get(int(result['elicitationMethod']))
    else:
        form.elicitationMethod = None
    
    if result['syntacticCategory']:
        form.syntacticCategory = meta.Session.query(
            model.SyntacticCategory).get(int(result['syntacticCategory']))
    else:
        form.syntacticCategory = None
    
    if result['source']:
        form.source = meta.Session.query(model.Source).get(int(result['source']))
    else:
        form.source = None
    
    if result['elicitor']:
        form.elicitor = meta.Session.query(model.User).get(int(result['elicitor']))
    else:
        form.elicitor = None
    
    if result['verifier']:
        form.verifier = meta.Session.query(model.User).get(int(result['verifier']))
    else:
        form.verifier = None
    
    if result['speaker']:
        form.speaker = meta.Session.query(model.Speaker).get(int(result['speaker']))
    else:
        form.speaker = None
        
    # Many-to-Many Data: Keywords
    # First check if the user has made any changes to the keywords.
    # If there are any changes, just delete all keywords and replace with new ones    
    keywordsToAdd = [int(kw['keyword']) for kw in result['keywords']]
    keywordsWeHave = [kw.id for kw in form.keywords]
    if keywordsToAdd != keywordsWeHave:
        form.keywords = []
        for keyword in keywordsToAdd:
            keywordObject = meta.Session.query(model.Keyword).get(keyword)
            form.keywords.append(keywordObject)
    # OLD-generated Data
    now = datetime.datetime.now()
    if createOrSave == 'create':
        form.datetimeEntered = now
    form.datetimeModified = now
    # Add the Enterer as the current user, if we are creating.  If we are saving,
    #  leave the enterer as it is
    if createOrSave == 'create':
        form.enterer = meta.Session.query(model.User).get(int(session['user_id']))
    # Create the morphemeBreakIDs and morphemeGlossIDs attributes;
    #  these are lists of lists representing words, containing lists of Form IDs
    #  for their matching morphemes, e.g., [[[1], [2]], [[3], [2]]];
    #  We add the form first to get an ID so that monomorphemic Forms can be self-referential
    meta.Session.add(form)
    getMorphemeIDLists(form)   
    return form

def backupForm(form):
    """Backup a Form that is being updated or deleted to the formbackup table."""
    # transform nested data structures to JSON for storage in a 
    #  relational database unicode text column    
    formBackup = model.FormBackup()
    user = json.dumps({
        'id': session['user_id'],
        'firstName': session['user_firstName'],
        'lastName': session['user_lastName']
    })
    formBackup.toJSON(form, user)
    meta.Session.add(formBackup)

def rememberPreviousSearches(searchToRemember):
    """Function stores the last 10 searches in the session.
    These searches are stored as a list of dictionaries;
    the same dictionaries outputed by the query action.
    """   
    if 'previousSearches' in session:
        previousSearches = session['previousSearches']
        previousSearches.reverse()
        previousSearches.append(searchToRemember)
        previousSearches.reverse()
        if len(previousSearches) > app_globals.maxNoPreviousSearches:
            del previousSearches[-1]
        session['previousSearches'] = previousSearches
    else:
        session['previousSearches'] = [searchToRemember]
    session.save()

class FormController(BaseController):
    """Form Controller contains actions about OLD Forms.
    Authorization and authentication are implemented by the
    helper decorators authenticate and authorize which can be
    found in lib/auth.py."""

    @h.authenticate
    def browse(self):
        """Browse through all Forms in the system."""
        form_q = meta.Session.query(model.Form).order_by(model.Form.transcription)
        c.paginator = paginate.Page(
            form_q,
            page=int(request.params.get('page', 1)),
            items_per_page = app_globals.form_items_per_page
        )
        c.browsing = True
        return render('/derived/form/results.html')

    @h.authenticate
    def view(self, id):
        """View a BLD Form.  Requires a Form ID as input."""
        if id is None:
            abort(404)
        # Redirect to results action
        redirect(url(controller='form', action='results', id=id))

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def add(self):
        """Display HTML form for adding a new BLD Form.
        HTML form calls create action."""
        # Make extra glosses fields invisible by default
        c.viewExtraGlossesFields = False
        
        return renderAddForm()

    @h.authenticate
    def search(self, values=None, errors=None):
        """Display HTML form for searching for BLD Forms.
        HTML form calls query action."""
        # if no user-entered defaults are set, make gloss the default for searchLocation2
        if not values:
            values = {'searchLocation2': u'gloss'}
            values['orderByColumn'] = 'id'
        # By default, the additional search restrictors are hidden
        c.viewRestrictors = False
        # check if this is a redirect from the searchprevious action
        if 'searchToRepeat' in session:
            values = session['searchToRepeat']['values']
            result = session['searchToRepeat']['result']
            del session['searchToRepeat']
            session['flash'] = u'This is a previous search'
            session.save()
            # If the previous search had restrictors specified, make the restrictor fields visible
            restrictors = [restrictor for restrictor in result['restrictors'] if restrictor['options']]
            dateRestrictors = [restrictor for restrictor in result['dateRestrictors'] if restrictor['date']]
            if restrictors or dateRestrictors:
                c.viewRestrictors = True 
        # Get today in MM/DD/YYYY form    
        c.today = datetime.date.today().strftime('%m/%d/%Y')
        html = render('/derived/form/search.html')      
        return htmlfill.render(html, defaults=values, errors=errors)

    @h.authenticate
    def previoussearches(self):
        """Display this user's last 10 searches so that any
        can be repeated and/or altered."""
        c.previousSearches = []
        if 'previousSearches' in session:
            c.previousSearches = session['previousSearches']
        c.maxNoPreviousSearches = app_globals.maxNoPreviousSearches
        return render('/derived/form/previoussearches.html')

    @h.authenticate
    def searchprevious(self, id):
        """Here id represents the index of the search to be repeated from
        the list of previous searches stored in session['previousSearches'].
        If the id/index does not correspond to a stored search,
        the system simply redirects to the (blank) search action."""
        if id and len(session['previousSearches']) >= int(id):
            session['searchToRepeat'] = session['previousSearches'][int(id)]
            session.save()
        redirect(url(controller='form', action='search', id=None))

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    @restrict('POST')
    def create(self):
        """Enter BLD Form data into the database.
        This is the action referenced by the html form
        rendered by the add action."""
        schema = NewFormForm()
        values = dict(request.params)
        try:
            result = schema.to_python(dict(request.params), c)
        except Invalid, e:
            return renderAddForm(
                values=values,
                errors=variabledecode.variable_encode(
                    e.unpack_errors() or {},
                    add_repetitions=False
                )
            )
        else:
            # Create a new Form object and populate its attributes with the results
            form = model.Form()
            form = getFormAttributes(form, result, 'create')
            # Enter the data
            meta.Session.add(form)
            meta.Session.commit()
            # Issue an HTTP redirect
            response.status_int = 302
            response.headers['location'] = url(controller='form', action='view', id=form.id)
            return "Moved temporarily"       

    @h.authenticate
    @restrict('POST')
    def query(self):
        """Query action validates the search input values; 
        if valid, query stores the search input values in the session and redirects to results;
        if invalid, query redirect to search action (though I don't think it's possible to enter an invalid query...).  
        Query is the action referenced by the html form rendered by the search action."""
        schema = SearchFormForm()
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
            # we put result into session['formSearchValues'] so that the results action
            # can use it to build the SQLAlchemy query
            session['formSearchValues'] = result
            # Put both the result and the values (the unmodified user-entered search terms)
            #  into the session so that they can be saved for "Previous Search" functionality.
            result['timeSearched'] = datetime.datetime.now()
            searchToRemember = {'result': result, 'values': values}
            rememberPreviousSearches(searchToRemember)
            session.save() 
            # Issue an HTTP redirect
            response.status_int = 302
            response.headers['location'] = url(controller='form', action='results')
            return "Moved temporarily"

    @h.authenticate
    def results(self, id=None):
        """Results action uses the filterSearchQuery helper function to build
        a query based on the values entered by the user in the search form.

        An optional id argument can be provided in the URL (usually because of a 
        redirect from the view() action.  This id can be a single integer or 
        multiple comma-separated integers."""
        if id:
            patt = re.compile('^[0-9 ]+$')
            IDs = [ID.strip().replace(' ', '') for ID in id.split(',') if patt.match(ID)]
            if not IDs: IDs = [0]
            form_q = meta.Session.query(model.Form)
            filterString = 'or_(' + ', '.join(['model.Form.id==%s' % ID for ID in IDs]) + ')'
            filterString = 'form_q.filter(%s)' % filterString
            # Evaluate the object and methods mentioned in the string using Python's eval(),
            # Update the query object using Python's exec()
            cmd = "form_q = eval('%s' % filterString)"
            exec(cmd)
        else:
            if 'formSearchValues' in session:
                result = session['formSearchValues']
                form_q = meta.Session.query(model.Form)
                form_q = h.filterSearchQuery(result, form_q, 'Form')
            else:
                form_q = meta.Session.query(model.Form)
        forms = form_q.all()

        c.paginator = paginate.Page(
            form_q,
            page=int(request.params.get('page', 1)),
            items_per_page = app_globals.form_items_per_page
        )
    
        print '\n\n\nSomething is wrong in the template\n\n\n'

        return render('/derived/form/results.html')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def update(self, id=None):
        """Displays an HTML form for updating a BLD Form.
        HTML form calls save action."""
        if id is None:
            abort(404)
        form_q = meta.Session.query(model.Form)
        form = form_q.filter_by(id=id).first()
        if form is None:
            abort(404)
        c.formID = form.id
        values = {
            'ID': form.id,
            'transcription': h.storageToInputTranslate(form.transcription),
            'grammaticality': form.grammaticality,
            'morphemeBreak': h.storageToInputTranslate(form.morphemeBreak, True),
            'morphemeGloss': form.morphemeGloss,
            'comments': h.storageToInputTranslateOLOnly(form.comments),
            'speakerComments': h.storageToInputTranslateOLOnly(form.speakerComments),
            'elicitationMethod': form.elicitationmethod_id,
            'syntacticCategory': form.syntacticcategory_id,
            'speaker': form.speaker_id,
            'elicitor': form.elicitor_id,
            'verifier': form.verifier_id,
            'source': form.source_id,
            'dateElicited': form.dateElicited
        }
        # re-format the keys and values of the values dict into a flat structure
        #  so that htmlfill can fill in the form properly. 
        if form.dateElicited:
            values['dateElicited'] = form.dateElicited.strftime('%m/%d/%Y') 
        for i in range(len(form.glosses)):
            gKey = 'glosses-%s.gloss' % i
            ggKey = 'glosses-%s.grammaticality' % i
            iKey = 'glosses-%s.ID' % i
            values[gKey] = form.glosses[i].gloss   
            values[ggKey] = form.glosses[i].glossGrammaticality
            values[iKey] = form.glosses[i].id
        for keyword in form.keywords:
            kKey = 'keywords-%s.keyword' % keyword.id
            values[kKey] = keyword.id
        # Make extra glosses fields visible if there are data in them
        c.viewExtraGlossesFields = False
        if 'glosses-1.ID' in values or 'glosses-2.ID' in values or  'glosses-3.ID' in values:
            c.viewExtraGlossesFields = True 
        return renderAddForm(values, None, 'update')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    @restrict('POST')
    def save(self):
        """Updates existing BLD Form.
        This is the action referenced by the html form
        rendered by the update action."""
        schema = UpdateFormForm()
        values = dict(request.params)
        try:
            result = schema.to_python(dict(request.params), c)
        except Invalid, e:
            c.id = values['ID']
            # Make extra glosses fields visible if there are data in them
            c.viewExtraGlossesFields = False
            if 'glosses-1.ID' in values or 'glosses-2.ID' in values or  'glosses-3.ID' in values:
                c.viewExtraGlossesFields = True 
            return renderAddForm(
                values=values,
                errors=variabledecode.variable_encode(
                    e.unpack_errors() or {},
                    add_repetitions=False
                ),
                addUpdate='update'
            )
        else:
            # Get the Form object with ID from hidden field in update.html
            form_q = meta.Session.query(model.Form)
            form = form_q.filter_by(id=result['ID']).first()
            # Backup the form to the formbackup table
            backupForm(form)
            # Populate the Form's attributes with the data from the user-entered result dict
            form = getFormAttributes(form, result, 'save')
            # Commit the update
            meta.Session.commit()
            # Issue an HTTP redirect
            response.status_int = 302
            response.headers['location'] = url(controller='form', action='view', id=form.id)
            return "Moved temporarily" 

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def delete(self, id):
        """Delete the BLD form with ID=id."""
        if id is None:
            abort(404)
        form_q = meta.Session.query(model.Form)
        form = form_q.get(int(id))
        if form is None:
            abort(404)
        # Back up Form to formbackup table        
        backupForm(form)
        # Delete Form
        meta.Session.delete(form)
        meta.Session.commit()
        session['flash'] = "Form %s has been deleted" % id
        session.save()
        redirect(url(controller='form', action='results'))

    @h.authenticate
    def history(self, id=None):
        """Display previous versions (i.e., history) 
        of BLD Form with id=id."""
        if id is None:
            abort(404)
        c.form = meta.Session.query(model.Form).get(int(id))  
        if c.form is None:
            abort(404)      
        c.formBackups = meta.Session.query(model.FormBackup).filter(model.FormBackup.form_id==int(id)).order_by(desc(model.FormBackup.datetimeModified)).all()  
        return render('/derived/form/history.html')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def associate(self, id):
        """Display the page for associating a BLD Form with id=id 
        to a BLD File.  The HTML form in the rendered page ultimately
        references the link action."""
        if id is None:
            abort(404)
        c.form = meta.Session.query(model.Form).get(int(id))  
        if c.form is None:
            abort(404)   
        return render('/derived/form/associate.html')

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    @restrict('POST')
    @validate(schema=AssociateFormFileForm(), form='associate')
    def link(self, id):
        """Associate BLD Form with id=id to a BLD File.  The ID of the 
        File is passed via a POST form.  This "ID" may in fact be a 
        comma-separated list of File IDs."""
        # Get the Form
        if id is None:
            abort(404)
        form = meta.Session.query(model.Form).get(int(id))  
        if form is None:
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
                if file in form.files:
                    if 'flash' in session:
                        session['flash'] += 'File %s is already associated to Form %s ' % (file.id, form.id)
                    else:
                        session['flash'] = 'File %s is already associated to Form %s ' % (file.id, form.id)
                else:
                    form.files.append(file)
            meta.Session.commit()
            session.save()
        else:
            session['flash'] = u'Sorry, no Files have any of the following IDs: %s' % fileID
            session.save()
        return redirect(url(controller='form', action='view', id=form.id))

    @h.authenticate
    @h.authorize(['administrator', 'researcher'])
    def disassociate(self, id, otherID):
        """Disassociate BLD Form id from BLD File otherID."""
        if id is None or otherID is None:
            abort(404)
        form = meta.Session.query(model.Form).get(int(id)) 
        file = meta.Session.query(model.File).get(int(otherID)) 
        if file is None:
            if form is None:
                abort(404)
            else:
                session['flash'] = 'There is no File with ID %s' % otherID
        if file in form.files:
            form.files.remove(file)
            meta.Session.commit()
            session['flash'] = 'File %s disassociated' % otherID
        else:
            session['flash'] = 'Form %s was never associated to File %s' % (id, otherID)
        session.save()
        redirect(url(controller='form', action='view', id=id))

    @h.authenticate
    def remember(self, id=None):
        """Put BLD Form with id=id into memory."""
        if id is None:
            if 'formSearchValues' in session:
                result = session['formSearchValues']
                form_q = meta.Session.query(model.Form)
                c.forms = h.filterSearchQuery(result, form_q, 'Form').all()
            else:
                c.forms = meta.Session.query(model.Form)            
        else:
            form_q = meta.Session.query(model.Form)
            c.forms = [form_q.get(int(id))]
            if not c.forms:
                abort(404)
        user = meta.Session.query(model.User).filter(model.User.id==session['user_id']).first()
        msg = ''
        for form in c.forms:
            if form in user.rememberedForms:
                msg += u'<p>Form %s is already in memory</p>' % form.id
            else:
                msg += u'<p>Form %s has been remembered</p>' % form.id
                user.rememberedForms.append(form)
        meta.Session.commit()
        session['flash'] = h.literal(msg)
        session.save()
        redirect(url(controller='form', action='results'))

    @h.authenticate
    def export(self, id=None):
        """Export a set of one or more BLD Forms.

        If id is None, export all Forms from last search
        (using session['formSearchValues']); if id is 'memory', export Forms in
        Memory; otherwise, export Form with id == id.

        This action renders an html form (templates/base/export) where the user
        chooses an export type.
        
        """
        c.id = id
        return render('/derived/form/export.html')

    @h.authenticate
    @restrict('POST')
    def exporter(self, id=None):
        """Produce an export document based on the export type chosen by the
        user in the form rendered by the export action.

        An empty id indicates that the set of forms to be exported should be
        queried from the database based on the values of
        session['formSearchValues'].

        An id of 'memory' indicates that we should export everything in Memory.

        To add new export types, add a def to '/base/exporter.html' and add your
        def name and description to app_globals.exportOptions.
        
        """
        if id and id=='memory':
            user = meta.Session.query(model.User).filter(
                model.User.id==session['user_id']).first()
            c.forms = meta.Session.query(model.Form).order_by(
                model.Form.id).filter(
                model.Form.memorizers.contains(user)).all() 
        elif id:
            form_q = meta.Session.query(model.Form)
            c.forms = form_q.filter(model.Form.id==id).all()
        else:
            if 'formSearchValues' in session:
                result = session['formSearchValues']
                form_q = meta.Session.query(model.Form)
                c.forms = h.filterSearchQuery(result, form_q, 'Form').order_by(
                    model.Form.id).all()
            else:
                c.forms = meta.Session.query(model.Form)
        if c.forms is None:
            abort(404)
        c.exportType = request.params['exportType']
        return render('/base/exporter.html')
