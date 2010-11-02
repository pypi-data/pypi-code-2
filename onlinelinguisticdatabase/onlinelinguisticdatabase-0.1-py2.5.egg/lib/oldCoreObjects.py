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

import copy
import datetime
import logging

try:
    import json
except ImportError:
    import simplejson as json

log = logging.getLogger(__name__)

class Column:
    """Empty class that the fromJSON() method uses to convert its
    dicts into objects that are Form attributes.  See fromJSON(self) below."""
    pass

class Form(object):   

    def listifyCoreData(self, length=45, decrementor=3):
        """From transcription, morphemeBreak and morphemeGloss
        compute list attributes transcriptionList, morphemeBreakList
        and morphemeGlossList if, and only if, transcription,
        morphemeBreak and morphemeGloss have equal number of words.

        These three lists contain an equal number of sublists of words
        where the longest sublist[x] from the three types 
        (i.e., transcriptionList[x], morphemeBreakList[x], morphemeGlossList[x])
        is no greater than length.

        length is decremented by decrementor on each successive sublist.
        """				
        # Splits fields into lists of words.
        tempTransList = self.transcription.split()
        tempMorphBreak = self.morphemeBreak.split()
        tempMorphGloss = self.morphemeGloss.split()
        # Only get lists if fields have same number of "words".
        if len(tempTransList) == len(tempMorphBreak) == len(tempMorphGloss):
            combinedList = zip(tempTransList, tempMorphBreak, tempMorphGloss)
            # Get a list of the lengths of the longest string in each triple of combinedList 
            longestLengths = [max([len(word) for word in triple]) for triple in combinedList]         
            lengthsList = [[]]
            for lngth in longestLengths:
                lengthsList[-1].append(lngth)
                # Oops we appended too much!
                if sum(lengthsList[-1]) >= length:
                    length = length - decrementor
                    # If there's only one length in the sublist, 
                    #  leave it there and append a new sublist
                    if len(lengthsList[-1]) == 1:
                        lengthsList.append([])
                    # Otherwise, remove the last length and 
                    #  add it to a newly appended sublist
                    else:
                        lngthToMove = lengthsList[-1].pop()
                        lengthsList.append([lngthToMove])
            # A really ugly list comprehension that takes s.t. like a = [[9, 5, 11, 8, 5, 3], [19, 9]]
            #  and returns s.t. like tupleIndices = [(0, 6), (6, 8)], i.e., the indices required to go from
            #  b = [9, 5, 11, 8, 5, 3, 19, 9] to a
            tupleIndices = [(sum([len(x) for x in lengthsList[:i]]), sum([len(x) for x in lengthsList[:i]]) + len(lengthsList[i])) for i in range(len(lengthsList))]
            self.transcriptionList = [tempTransList[toople[0]:toople[1]] for toople in tupleIndices]
            self.morphemeBreakList = [tempMorphBreak[toople[0]:toople[1]] for toople in tupleIndices]
            self.morphemeGlossList = [tempMorphGloss[toople[0]:toople[1]] for toople in tupleIndices] 
            # Split the lists of morpheme break and morpheme gloss IDs in the same manner
            morphemeBreakIDs = json.loads(self.morphemeBreakIDs) 
            morphemeGlossIDs = json.loads(self.morphemeGlossIDs)            
            self.morphemeBreakIDsList = [morphemeBreakIDs[toople[0]:toople[1]] for toople in tupleIndices]
            self.morphemeGlossIDsList = [morphemeGlossIDs[toople[0]:toople[1]] for toople in tupleIndices]
    
    def getMorphemeGlossTuples(self, validDelimiters=[' ', '-', '=']):
        """From morphemeBreak and morphemeGloss, create list
        self.morphemeGlossTuples as a list of morpheme-gloss
        tuples (or lists).  Do so only if morphembeBreak and
        morphemeGloss have equal numbers of morphemes/glosses.

        Allow for the possibility of multiple delimiters
        (e.g., ' ', '-' or '=') and keep track of the previous
        delimiter so that the original strings can be recreated.

        Example:
        self.morphemeBreak = u"kn=ts-q'way'ilc pintk"
        self.morphemeGloss = u'1sERG=CUST-dance always"

        self.morphemeGlossTuples = [
            (u'kn', u'1sERG', u''),
            (u'ts', u'CUST', u'='),
            (u'q'way'ilc', u'dance', u'-'),
            (u'pintk', u'always', u' ')
        ]
        """
        previousDelimiter = 0
        breaks = []
        gloss = []
        delimiters = []
 
        #Goes through morphemeBreak char by char
        for i in range(len(self.morphemeBreak)):
            #Check if char is delimiter
            if self.morphemeBreak[i] in validDelimiters:
                #If it is not the first delimiter, add to list and take all text since previous delimiter.
                if previousDelimiter != 0:
                    delimiters.append(self.morphemeBreak[previousDelimiter])
                    breaks.append(self.morphemeBreak[previousDelimiter+1:i])
                #If it is first delimiter, take all text since beginning and append empty delimiter to list.
                else:
                    delimiters.append(u'')
                    breaks.append(self.morphemeBreak[previousDelimiter:i])
                previousDelimiter = i
            #If end of break, take the rest.
            elif i == len(self.morphemeBreak) - 1:
                    delimiters.append(self.morphemeBreak[previousDelimiter])
                    breaks.append(self.morphemeBreak[previousDelimiter+1:i+1])
 
        previousDelimiter = 0
 
        #Ditto for the gloss, but no need to append delimiters this time.
        for i in range(len(self.morphemeGloss)):
            if self.morphemeGloss[i] in validDelimiters:
                if previousDelimiter != 0:
                    gloss.append(self.morphemeGloss[previousDelimiter + 1:i])
                else:
                    gloss.append(self.morphemeGloss[previousDelimiter:i])
                previousDelimiter = i
            elif i == len(self.morphemeGloss) - 1:
                gloss.append(self.morphemeGloss[previousDelimiter+1:i+1])
 
        #Makes sure lists are equal length and no empty morphemes (no 2 delimiters in a row)
        if len(breaks) == len(gloss) and not '' in breaks and not '' in gloss:
            self.morphemeGlossTuples = zip(breaks, gloss, delimiters)
        else:
            self.morphemeGlossTuples = []

        
class FormBackup(Form):
    """FormBackup subclasses Form.  FormBackup has two novel methods,
    toJSON() and fromJSON().

    toJSON() takes a Form object as input and takes its data and stores
    nested data structures as JSON dictionaries which can be stored in 
    a database char field.

    fromJSON() takes converst the JSONified dictionaries back into Column
    objects, thus making the FormBackup behave just like a Form object."""
 
    def toJSON(self, form, user):
        """Convert the "pertinent" nested data structures of
        a Form into a python dict and then into a JSON data structure using 
        the json module from the standard library."""
        self.form_id = form.id
        self.transcription = form.transcription
        self.phoneticTranscription = form.phoneticTranscription
        self.morphemeBreak = form.morphemeBreak
        self.morphemeGloss = form.morphemeGloss
        self.grammaticality = form.grammaticality
        self.comments = form.comments
        self.speakerComments = form.speakerComments
        self.dateElicited = form.dateElicited
        self.datetimeEntered = form.datetimeEntered
        self.datetimeModified = datetime.datetime.now()
        self.syntacticCategoryString = form.syntacticCategoryString
        self.morphemeBreakIDs = form.morphemeBreakIDs
        self.morphemeGlossIDs = form.morphemeGlossIDs
        self.backuper = user
        if form.elicitationMethod:
            self.elicitationMethod = json.dumps({
                'id': form.elicitationMethod.id, 
                'name': form.elicitationMethod.name
            })
        if form.syntacticCategory:
            self.syntacticCategory = json.dumps({
                'id': form.syntacticCategory.id, 
                'name': form.syntacticCategory.name
            })
        if form.source:
            self.source = json.dumps({
                'id': form.source.id, 
                'authorFirstName': form.source.authorFirstName, 
                'authorLastName': form.source.authorLastName, 
                'year': form.source.year, 
                'fullReference': form.source.fullReference
            })
        if form.speaker:
            self.speaker = json.dumps({
                'id': form.speaker.id, 
                'firstName': form.speaker.firstName, 
                'lastName': form.speaker.lastName, 
                'dialect': form.speaker.dialect
            })
        if form.elicitor:
            self.elicitor = json.dumps({
                'id': form.elicitor.id, 
                'firstName': form.elicitor.firstName, 
                'lastName': form.elicitor.lastName
        })
        if form.enterer:
            self.enterer = json.dumps({
                'id': form.enterer.id, 
                'firstName': form.enterer.firstName, 
                'lastName': form.enterer.lastName
            })
        if form.verifier:
            self.verifier = json.dumps({
                'id': form.verifier.id, 
                'firstName': form.verifier.firstName, 
                'lastName': form.verifier.lastName
            })
        if form.glosses:
            self.glosses = json.dumps([{
                'id': gloss.id, 
                'gloss': gloss.gloss, 
                'glossGrammaticality': gloss.glossGrammaticality} for gloss in form.glosses])
        if form.keywords:
            self.keywords = json.dumps([{
                'id': keyword.id, 
                'name': keyword.name} for keyword in form.keywords])
        if form.files:
            self.files = json.dumps([{
                'id': file.id, 
                'name': file.name, 
                'embeddedFileMarkup': file.embeddedFileMarkup, 
                'embeddedFilePassword': file.embeddedFilePassword} for file in form.files])


    def fromJSON(self):
        """Convert the JSONified dictionaries back into Column objects, 
        thus making the FormBackup behave just like a Form object.  (Almost.)"""
        if self.elicitationMethod:
            elicitationMethod = json.loads(self.elicitationMethod)
            self.elicitationMethod = Column()
            self.elicitationMethod.id = elicitationMethod['id']
            self.elicitationMethod.name = elicitationMethod['name']            
        if self.syntacticCategory:
            syntacticCategory = json.loads(self.syntacticCategory)
            self.syntacticCategory = Column()
            self.syntacticCategory.id = syntacticCategory['id']
            self.syntacticCategory.name = syntacticCategory['name']            
        if self.source:
            source = json.loads(self.source)
            self.source = Column()
            self.source.id = source['id']
            self.source.authorFirstName = source['authorFirstName']            
            self.source.authorLastName = source['authorLastName']            
            self.source.year = source['year']            
            self.source.fullReference = source['fullReference']            
        if self.speaker:
            speaker = json.loads(self.speaker)
            self.speaker = Column()
            self.speaker.id = speaker['id']
            self.speaker.firstName = speaker['firstName']            
            self.speaker.lastName = speaker['lastName']            
            self.speaker.dialect = speaker['dialect']            
        if self.elicitor:
            elicitor = json.loads(self.elicitor)
            self.elicitor = Column()
            self.elicitor.id = elicitor['id']
            self.elicitor.firstName = elicitor['firstName']            
            self.elicitor.lastName = elicitor['lastName']            
        if self.enterer:
            enterer = json.loads(self.enterer)
            self.enterer = Column()
            self.enterer.id = enterer['id']
            self.enterer.firstName = enterer['firstName']            
            self.enterer.lastName = enterer['lastName']            
        if self.verifier:
            verifier = json.loads(self.verifier)
            self.verifier = Column()
            self.verifier.id = verifier['id']
            self.verifier.firstName = verifier['firstName']            
            self.verifier.lastName = verifier['lastName']            
        if self.glosses:
            glosses = json.loads(self.glosses)
            self.glosses = []
            for glossDict in glosses:
                gloss = Column()
                gloss.id = glossDict['id']
                gloss.gloss = glossDict['gloss']
                gloss.glossGrammaticality = glossDict['glossGrammaticality']
                self.glosses.append(gloss)
        if self.keywords:
            keywords = json.loads(self.keywords)
            self.keywords = []
            for keywordDict in keywords:
                keyword = Column()
                keyword.id = keywordDict['id']
                keyword.name = keywordDict['name']
                self.keywords.append(keyword)
        if self.files:
            files = json.loads(self.files)
            self.files = []
            for fileDict in files:
                file = Column()
                file.id = fileDict['id']
                file.name = fileDict['name']
                file.embeddedFileMarkup = fileDict['embeddedFileMarkup']
                file.embeddedFilePassword = fileDict['embeddedFilePassword']
                self.files.append(file)
        if self.backuper:
            backuper = json.loads(self.backuper)
            self.backuper = Column()
            self.backuper.id = backuper['id']
            self.backuper.firstName = backuper['firstName']            
            self.backuper.lastName = backuper['lastName']
    
if __name__ == '__main__':
    form = Form()

    form.transcription = u'anna ninaa itsinoyii ami aakii ki ikaakomimmoka matonni'
    form.morphemeBreak = u'ann-wa ninaa it-ino-yii am-yi aakii ki iik-waakomimm-ok-wa matonni'
    form.morphemeGloss = u'DEM-3PROX man LOC-see-DIR DEM-3OBV woman and INT-love-INV-3SG yesterday'
    form.gloss = u'the man saw that woman and he loved her yesterday'   

    preppedForm = getPreppedForm(form)
    print '%s\n%s\n%s\n%s' % (form.transcription, form.morphemeBreak, form.morphemeGloss, form.gloss)
