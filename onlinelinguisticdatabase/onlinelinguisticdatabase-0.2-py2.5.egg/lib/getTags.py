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

import onlinelinguisticdatabase.model as model
import onlinelinguisticdatabase.model.meta as meta

def getTags(tagsList=None):
    """ Function gets speakers, users, sources, syntactic categories
    and elicitation methods options from their respective tables in 
    the database and returns them.

    tagsList is an optional list argument specifying which tags should
    be retrieved.  If None, all tags are retrieved."""
    # Speakers
    speakers = []
    if not tagsList or 'speakers' in tagsList:
        speakers_q = meta.Session.query(model.Speaker).order_by(model.Speaker.lastName)
        speakers = [(speaker.id, speaker.firstName + ' ' + speaker.lastName) for speaker in speakers_q.all()]
    # Users
    users = []
    if not tagsList or 'users' in tagsList:
        users_q = meta.Session.query(model.User).order_by(model.User.lastName).filter(model.User.role!='learner')
        users = [(user.id, user.firstName + ' ' + user.lastName) for user in users_q.all()]
    # Sources
    sources = []
    if not tagsList or 'sources' in tagsList:
        sources_q = meta.Session.query(model.Source).order_by(model.Source.authorLastName)
        sources = [(source.id, source.authorLastName + ', ' + source.authorFirstName[0].upper() + '.  ' + unicode(source.year) + '.  ' + source.title[:10] + '...') for source in sources_q.all()]
    # Syntactic Categories
    syncats = []
    if not tagsList or 'syncats' in tagsList:    
        syncats_q = meta.Session.query(model.SyntacticCategory).order_by(model.SyntacticCategory.name)
        syncats = [(syncat.id, syncat.name) for syncat in syncats_q.all()]
    # Keywords    
    keywords = []
    if not tagsList or 'keywords' in tagsList:    
        keywords_q = meta.Session.query(model.Keyword).order_by(model.Keyword.name)
        keywords = [(keyword.id, keyword.name) for keyword in keywords_q.all()]
    # Elicitation Methods    
    elicitationMethods = []
    if not tagsList or 'elicitationMethods' in tagsList:    
        elicitationMethods_q = meta.Session.query(model.ElicitationMethod).order_by(model.ElicitationMethod.name)
        elicitationMethods = [(elicitationMethod.id, elicitationMethod.name) for elicitationMethod in elicitationMethods_q.all()]
    return {
        'speakers': speakers,
        'users': users,
        'sources': sources,
        'syncats': syncats,
        'keywords': keywords,
        'elicitationMethods': elicitationMethods
    }
