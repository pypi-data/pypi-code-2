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
import hashlib

from pylons import request, response, session, app_globals, tmpl_context as c
from pylons import url
from pylons.controllers.util import abort, redirect
from pylons.decorators.rest import restrict
from pylons.decorators import validate

from formencode.schema import Schema
from formencode.validators import UnicodeString, Email, Invalid, FancyValidator, PlainText, OneOf
from formencode import htmlfill
import formencode

from onlinelinguisticdatabase.lib.base import BaseController, render
import onlinelinguisticdatabase.model as model
import onlinelinguisticdatabase.model.meta as meta
import onlinelinguisticdatabase.lib.helpers as h

from onlinelinguisticdatabase.lib.oldMarkup import linkToOLDEntitites, embedFiles, embedForms

log = logging.getLogger(__name__)

class UniqueUsername(FancyValidator):
    """
    Custom validator.  Ensures that the username is unique
    """
    messages = {
        'repeated_username': 'Sorry, that username is already taken'
    }
    def validate_python(self, value, state):
        users = meta.Session.query(model.User).all()
        if value in [user.username for user in users]:
            raise Invalid(self.message("repeated_username", state), value, state)

class NewResearcherForm(Schema):
    """NewResearcherForm is a Schema for validating the 
    data entered at the Add Researcher page."""
    allow_extra_fields = True
    filter_extra_fields = True
    username = formencode.All(UniqueUsername(), PlainText(not_empty=True))
    password = PlainText(not_empty=True)
    firstName = UnicodeString(not_empty=True)
    lastName = UnicodeString(not_empty=True)
    email = Email(not_empty=True)
    affiliation = UnicodeString()
    role = OneOf(app_globals.roles)
    personalPageContent = UnicodeString()

class UpdateResearcherForm(NewResearcherForm):
    """Schema class that inherits from NewResearcherForm
    and adds an ID and modifies the password validator."""
    ID = UnicodeString()
    username = PlainText()
    password = PlainText()
    
class SaveSettingsForm(Schema):
    """SaveSettingsForm is a Schema for validating
    changes to a User's settings."""    
    allow_extra_fields = True
    filter_extra_fields = True
    collectionViewType = OneOf(app_globals.collectionViewTypes)
    inputOrthography = UnicodeString()
    outputOrthography = UnicodeString()

def getResearcherAttributes(researcher, result, createOrSave):
    researcher.username = result['username']
    researcher.firstName = result['firstName']
    researcher.lastName = result['lastName']
    researcher.email = result['email']
    researcher.affiliation = result['affiliation']
    researcher.personalPageContent = result['personalPageContent']
    researcher.role = result['role']
    # Only update the password if something was added
    if result['password']:
        researcher.password = hashlib.sha224(result['password']).hexdigest()

class ResearcherController(BaseController):
    
    def view(self, id):
        """View an OLD Researcher.  Requires a Researcher ID as input."""
        if id is None:
            abort(404)
        researcher_q = meta.Session.query(model.User)
        c.researcher = researcher_q.get(int(id))
        if c.researcher is None:
            abort(404)

        # Convert OLD Markup references to links/representations
        c.personalPageContent = linkToOLDEntitites(c.personalPageContent)
        c.personalPageContent = embedFiles(c.personalPageContent)
        c.personalPageContent = embedForms(c.personalPageContent)
        
        return render('/derived/people/researcher/view.html')

    @h.authenticate
    @h.authorize(['administrator'])
    def add(self):
        """Add a new OLD Researcher.  This action renders the html form 
        for adding a new Researcher."""
        return render('/derived/people/researcher/add.html')

    @h.authenticate
    @h.authorize(['administrator'])
    @restrict('POST')    
    @validate(schema=NewResearcherForm(), form='add')
    def create(self):
        """Insert new Researcher data into database."""
        researcher = model.User()
        getResearcherAttributes(researcher, self.form_result, 'create')

        # Create a directory in files directory for this researcher
        h.createResearcherDirectory(researcher)

        # Enter the data
        meta.Session.add(researcher)
        meta.Session.commit()
        # Update the users variable in app_globals
        tags = h.getTags(['users'])
        app_globals.users = tags['users']
        # Issue an HTTP redirect
        response.status_int = 302
        response.headers['location'] = url(controller='researcher', action='view', id=researcher.id)
        return "Moved temporarily"           

    @h.authenticate
    @h.authorize(['administrator', 'researcher', 'learner'], userIDIsArgs1=True)
    def edit(self, id):
        """Edit an OLD Researcher.  A non-administrator can only edit their own
        information; hence the userIDIsArgs1=True argument in the authorize validator."""
        if id is None:
            abort(404)
        researcher_q = meta.Session.query(model.User)
        c.researcher = researcher_q.get(int(id))
        if c.researcher is None:
            abort(404)
        html = render('/derived/people/researcher/edit.html')
        values = {
            'ID': c.researcher.id,
            'username': c.researcher.username,
            'firstName': c.researcher.firstName,
            'lastName': c.researcher.lastName,
            'email': c.researcher.email,
            'affiliation': c.researcher.affiliation,
            'personalPageContent': c.researcher.personalPageContent,
            'role': c.researcher.role
        }
        return htmlfill.render(html, values)

    @h.authenticate
    @restrict('POST')    
    @validate(schema=UpdateResearcherForm(), form='edit')
    def save(self):
        """Update OLD Researcher with newly altered data."""
        researcher_q = meta.Session.query(model.User)
        researcher = researcher_q.get(int(self.form_result['ID']))        
        getResearcherAttributes(researcher, self.form_result, 'save')
        # Update the data
        meta.Session.commit()
        # Update the users variable in app_globals
        tags = h.getTags(['users'])
        app_globals.users = tags['users']
        # update the session if we have just updated the current user
        if researcher.id == session['user_id']:
            h.getAuthorizedUserIntoSession(researcher)
        # Issue an HTTP redirect
        response.status_int = 302
        response.headers['location'] = url(controller='researcher', action='view', id=researcher.id)
        return "Moved temporarily"    

    @h.authenticate
    @h.authorize(['administrator'])
    def delete(self, id):
        """Delete the BLD Researcher with ID=id."""
        if id is None:
            abort(404)
        researcher_q = meta.Session.query(model.User)
        researcher = researcher_q.get(int(id))
        if researcher is None:
            abort(404)
        meta.Session.delete(researcher)
        meta.Session.commit()
        
        # Destroy the researcher's directory in the files directory
        h.destroyResearcherDirectory(researcher)

        # Update the users variable in app_globals
        tags = h.getTags(['users'])
        app_globals.users = tags['users']
        session['flash'] = "Researcher %s has been deleted" % id
        session.save()
        redirect(url(controller='people'))

    @h.authenticate
    @h.authorize(['administrator', 'researcher', 'learner'], userIDIsArgs1=True)
    def settings(self, id):
        """View the logged in researcher's settings"""
        if id is None: 
            abort(404)
        researcher_q = meta.Session.query(model.User)
        c.researcher = researcher_q.get(int(id))
        if c.researcher is None:
            abort(404)
        return render('/derived/people/researcher/settings.html')

    @h.authenticate
    @h.authorize(['administrator', 'researcher', 'learner'], userIDIsArgs1=True)
    def editsettings(self, id):
        """Edit the logged in researcher's settings"""
        if id is None: 
            abort(404)
        researcher_q = meta.Session.query(model.User)
        c.researcher = researcher_q.get(int(id))
        if c.researcher is None:
            abort(404)
        values = {
            'collectionViewType': c.researcher.collectionViewType,
            'inputOrthography': c.researcher.inputOrthography,
            'outputOrthography': c.researcher.outputOrthography
        }
        html = render('/derived/people/researcher/editsettings.html')
        return htmlfill.render(html, defaults=values)
        
    @h.authenticate
    @restrict('POST')
    @validate(schema=SaveSettingsForm(), form='editsettings')
    def savesettings(self, id):
        """Save the newly changed user-specific settings"""
        if id is None: 
            abort(404)
        researcher_q = meta.Session.query(model.User)
        c.researcher = researcher_q.get(int(id))
        if c.researcher is None:
            abort(404)  
        # Save settings in model
        c.researcher.collectionViewType = self.form_result['collectionViewType']
        c.researcher.inputOrthography = self.form_result['inputOrthography']
        c.researcher.outputOrthography = self.form_result['outputOrthography']
        meta.Session.commit()
        # Save settings in session
        session['user_collectionViewType'] = c.researcher.collectionViewType
        session['user_inputOrthography'] = c.researcher.inputOrthography
        session['user_outputOrthography'] = c.researcher.outputOrthography

        # Put the appropriate translators in the session.
        #  That is, if the user has chosen an output orthography that is
        #  different from the storage orthography AND is different from the
        #  default output orthography, create a new translator in the session.
        #  Ditto for the input-to-storage translator.
        h.putOrthographyTranslatorsIntoSession()

        session.save()
        
        # Issue an HTTP redirect
        response.status_int = 302
        response.headers['location'] = url(controller='researcher', \
                                        action='settings', id=c.researcher.id)
        return "Moved temporarily"