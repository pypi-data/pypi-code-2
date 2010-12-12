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

import re
import copy
import datetime
import logging

from os import sep, path 
from random import randrange
    
try:
    import json
except ImportError:
    import simplejson as json

from pylons import app_globals, url
import helpers as h

log = logging.getLogger(__name__)

class Column:
    """Empty class that the fromJSON() methods of FormBackup and
    CollectionBackup use to convert their dicts into objects that are attributes
    of FormBackup and CollectionBackup.  See FormBackup.fromJSON() and
    CollectionBackup.fromJSON() below.
    
    """
    
    pass



################################################################################
#################  Form and FormBackup Classes  ################################
################################################################################


class Form(object):

    def listifyCoreData(self, length=45, decrementor=3):
        """From transcription, morphemeBreak and morphemeGloss compute list
        attributes transcriptionList, morphemeBreakList and morphemeGlossList
        if, and only if, transcription, morphemeBreak and morphemeGloss have
        equal number of words.

        These three lists contain an equal number of sublists of words where the
        longest sublist[x] from the three types (i.e., transcriptionList[x],
        morphemeBreakList[x], morphemeGlossList[x]) is no greater than length.

        length is decremented by decrementor on each successive sublist.

        """

        # Splits fields into lists of words.
        tempTransList = self.transcription.split()
        tempMorphBreak = self.morphemeBreak.split()
        tempMorphGloss = self.morphemeGloss.split()

        # Only get lists if fields have same number of "words".
        if len(tempTransList) == len(tempMorphBreak) == len(tempMorphGloss):
            combinedList = zip(tempTransList, tempMorphBreak, tempMorphGloss)
            # Get a list of the lengths of the longest string in each triple of
            #  combinedList 
            longestLengths = [
                max([len(word) for word in triple]) for triple in combinedList]
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

            # A really ugly list comprehension that takes s.t. like
            #  a = [[9, 5, 11, 8, 5, 3], [19, 9]]
            #  and returns s.t. like
            #  tupleIndices = [(0, 6), (6, 8)],
            #  i.e., the indices required to go from
            #  b = [9, 5, 11, 8, 5, 3, 19, 9] to a
            tupleIndices = [
                (sum([len(x) for x in lengthsList[:i]]), sum([len(x) for x in \
                lengthsList[:i]]) + len(lengthsList[i])) \
                for i in range(len(lengthsList))
            ]
            self.transcriptionList = [
                tempTransList[toople[0]:toople[1]] for toople in tupleIndices]
            self.morphemeBreakList = [
                tempMorphBreak[toople[0]:toople[1]] for toople in tupleIndices]
            self.morphemeGlossList = [
                tempMorphGloss[toople[0]:toople[1]] for toople in tupleIndices] 
            
            # Split the lists of morpheme break and morpheme gloss IDs in the same manner
            morphemeBreakIDs = json.loads(self.morphemeBreakIDs) 
            morphemeGlossIDs = json.loads(self.morphemeGlossIDs)            
            self.morphemeBreakIDsList = [morphemeBreakIDs[toople[0]:toople[1]] for toople in tupleIndices]
            self.morphemeGlossIDsList = [morphemeGlossIDs[toople[0]:toople[1]] for toople in tupleIndices]

    def getMorphemeGlossTuples(self, validDelimiters=[' ', '-', '=']):
        """From morphemeBreak and morphemeGloss, create list
        self.morphemeGlossTuples as a list of morpheme-gloss tuples (or lists).
        Do so only if morphembeBreak and morphemeGloss have equal numbers of
        morphemes/glosses.

        Allow for the possibility of multiple delimiters (e.g., ' ', '-' or '=')
        and keep track of the previous delimiter so that the original strings
        can be recreated.

        Example:
        
            self.morphemeBreak = u"kn=ts-q'way'ilc pintk"
            self.morphemeGloss = u'1sERG=CUST-dance always"

            self.morphemeGlossTuples = [(u'kn', u'1sERG', u''),
                                        (u'ts', u'CUST', u'='),
                                        (u'q'way'ilc', u'dance', u'-'),
                                        (u'pintk', u'always', u' ')]

        """

        previousDelimiter = 0
        breaks = []
        gloss = []
        delimiters = []
 
        # Goes through morphemeBreak char by char
        for i in range(len(self.morphemeBreak)):
            
            # Check if char is delimiter
            if self.morphemeBreak[i] in validDelimiters:
                # If it is not the first delimiter, add to list and take all text
                #  since previous delimiter.
                if previousDelimiter != 0:
                    delimiters.append(self.morphemeBreak[previousDelimiter])
                    breaks.append(self.morphemeBreak[previousDelimiter+1:i])
                # If it is first delimiter, take all text since beginning and
                #  append empty delimiter to list.
                else:
                    delimiters.append(u'')
                    breaks.append(self.morphemeBreak[previousDelimiter:i])
                previousDelimiter = i
            
            # If end of break, take the rest.
            elif i == len(self.morphemeBreak) - 1:
                delimiters.append(self.morphemeBreak[previousDelimiter])
                breaks.append(self.morphemeBreak[previousDelimiter+1:i+1])

        previousDelimiter = 0

        # Ditto for the gloss, but no need to append delimiters this time.
        for i in range(len(self.morphemeGloss)):
            if self.morphemeGloss[i] in validDelimiters:
                if previousDelimiter != 0:
                    gloss.append(self.morphemeGloss[previousDelimiter + 1:i])
                else:
                    gloss.append(self.morphemeGloss[previousDelimiter:i])
                previousDelimiter = i
            elif i == len(self.morphemeGloss) - 1:
                gloss.append(self.morphemeGloss[previousDelimiter+1:i+1])
 
        # Makes sure lists are equal length and no empty morphemes (no 2
        #  delimiters in a row)
        if len(breaks) == len(gloss) and not '' in breaks and not '' in gloss:
            self.morphemeGlossTuples = zip(breaks, gloss, delimiters)
        else:
            self.morphemeGlossTuples = []

    def getIGTHTMLTable(self):
        """Return an HTML representation of the Form in interlinear gloss text
        (IGT) format.
        
        """
        
        # If there is a morphological analysis with equal numbers of 'words' in
        #  each field, align the words using HTML table cells.
        if self.morphemeGloss and self.morphemeBreak and \
        len(self.transcription.split(' ')) == len(self.morphemeGloss.split(' ')) and \
        len(self.transcription.split(' ')) == len(self.morphemeBreak.split(' ')):
            result = self.getIGTHTMLTableWordsAligned()
        
        # Otherwise, just use a single table cell for each field
        else:
            result = u'<table>'
            result += u'<tr><td class="dataCellTr">%s%s</td></tr>' % (
                self.grammaticality,
                h.storageToOutputTranslate(self.transcription)
            )
            result += u'<tr><td class="dataCell">%s</td></tr>' % \
                h.storageToOutputTranslate(self.morphemeBreak, True)
            result += u'<tr><td class="dataCell">%s</td></tr>' % \
                self.morphemeGloss
            for gloss in self.glosses:
                result += u'<tr><td class="dataCell">&lsquo;%s%s&rsquo;</td></tr>' % \
                    (
                        (lambda x: x if x else u'')(gloss.glossGrammaticality),
                        gloss.gloss
                    )
            result += u'</table>'
        return result
    
    def getIGTHTMLTableWordsAligned(self):
        """Return an HTML representation of the Form in interlinear gloss text
        (IGT) format where the words are aligned using table cells.

        """

        self.listifyCoreData()
        result = u'<table>'
        for i in range(len(self.transcriptionList)):
            
            # styleAttribute makes a dummy <td> have a greater and greater width
            #  on each iteration, thus creating the "upside down staircase effect"
            styleAttribute = u'width: %sem;min-width: %sem; padding: 0;' % \
                             ((i * 2), (i * 2))
            
            result += u'<table>'
            result += u'<tr><td style="%s"></td>%s</tr>' % (
                styleAttribute,
                self.getOneWordPerCell(
                    self.transcriptionList[i], 'transcription', i)
            )
            result += u'<tr><td style="%s"></td>%s</tr>' % (
                styleAttribute,
                self.getOneWordPerCell(
                    self.morphemeBreakList[i], 'morphemeBreak', i)
            )
            result += u'<tr><td style="%s"></td>%s</tr>' % (
                styleAttribute,
                self.getOneWordPerCell(
                    self.morphemeGlossList[i], 'morphemeGloss', i)
            )
            result += u'</table>'
        for gloss in self.glosses:
            result += u'<table>'
            result += u'<tr><td class="dataCell">&lsquo;%s%s&rsquo;</td></tr>' % (
                gloss.glossGrammaticality, gloss.gloss)
        result += u'</table>'
        return result
    
    def getOneWordPerCell(self, wordList, lineType, subListIndex):
        result = u''
        for ii in range(len(wordList)):
            word = wordList[ii]
            if lineType == 'transcription' and ii == 0 and subListIndex == 0:
                result += u'<td class="dataCellTr">%s%s</td>' % (
                    self.grammaticality, h.storageToOutputTranslate(word))
            elif lineType == 'transcription':
                result += u'<td class="dataCellTr">%s</td>' % \
                    h.storageToOutputTranslate(word)
            else: 
                result += u'<td class="dataCell">%s</td>' % \
                    self.getMorphemeAsLink(word, lineType, subListIndex, ii)
        return result
    
    def getMorphemeAsLink(self, word, lineType, subListIndex, wordIndex):
        """For each morpheme (or morpheme gloss), check if it has a list of IDs
        in morphemeBreakIDs (or in morphemeGlossIDs, etc.) and, if so, convert
        the string representing the morpheme into a link to the appropriate
        Forms.  Links where the morpheme and morpheme gloss have the class
        'match' so that a color representation of the consistency can be made
        via CSS.
        
        """

        validDelimiters = app_globals.validDelimiters
        patt = '([%s])' % ''.join(validDelimiters)
        spacePatt = re.compile('([\t\n]| {2,})')
        morphemeBreakWords = spacePatt.sub(
            ' ', self.morphemeBreak.strip()).split()
        morphemeGlossWords = spacePatt.sub(
            ' ', self.morphemeGloss.strip()).split()
        morphemes = [len(re.split(patt, x)) for x in morphemeBreakWords]
        glosses = [len(re.split(patt, x)) for x in morphemeGlossWords]
        if morphemes == glosses:
            morphsAndDelimitersList = re.split(patt, word)
            mbIDsList = self.morphemeBreakIDsList[subListIndex][wordIndex]
            mgIDsList = self.morphemeGlossIDsList[subListIndex][wordIndex]
            madList = []
            for iii in range(len(morphsAndDelimitersList)):
                el = morphsAndDelimitersList[iii]
                if el in morphsAndDelimitersList[::2]:
                    if lineType == 'morphemeBreak':
                        elIDsList = mbIDsList[iii / 2]
                        otherIDsList = mgIDsList[iii / 2]
                    else:
                        elIDsList = mgIDsList[iii / 2]
                        otherIDsList = mbIDsList[iii / 2]
                    if [triple[0] for triple in elIDsList] == [
                        triple[0] for triple in otherIDsList]:
                        klass = 'match'
                    else:
                        klass = 'nonmatch'
                    if len(elIDsList) > 0:
                        id = ','.join([str(triple[0]) for triple in elIDsList])
                        URL = url(controller='form', action='view', id=id)
                        title = '; '.join(['%s (%s)' % (
                            triple[1], triple[2] or 'NULL') for triple in elIDsList])
                        madList.append(
                            '<a class="%s" href="%s" title="%s">%s</a>' % \
                                      (klass, URL, title, el)
                        )
                    else:
                        id = None
                        madList.append(el)
                else:
                    madList.append(el)
            word = ''.join(madList)
        return h.storageToOutputTranslate(word, True)


class FormBackup(Form):
    """FormBackup subclasses Form.  FormBackup has two novel methods,
    toJSON() and fromJSON().

    toJSON() takes a Form object as input and takes its data and stores
    nested data structures as JSON dictionaries which can be stored in 
    a database char field.

    fromJSON() converts the JSONified dictionaries back into Column
    objects, thus making the FormBackup behave just like a Form object.
    
    """
 
    def toJSON(self, form, user):
        """Convert the "pertinent" nested data structures of
        a Form into a python dict and then into a JSON data structure using 
        the json module from the standard library.

        Note: the user argument is already a Python string / JSON object

        """
        
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
        thus making the FormBackup behave just like a Form object.  (Almost.)
        
        """
        
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



################################################################################
#################  Collection and CollectionBackup Classes  ####################
################################################################################

class Collection(object):
    """A dummy Collection object for CollectionBackup to subclass.
    
    Perhaps some Collection-related functionality should be implemented as
    methods here.  E.g., the functions in controllers/collection.py that format
    the contents of a Collection ...
    
    """
    
    pass

class CollectionBackup(Collection):
    """CollectionBackup subclasses Collection.  CollectionBackup has two novel
    methods, toJSON() and fromJSON().

    toJSON() takes a Collection object as input and takes its data and stores
    nested data structures as JSON dictionaries which can be stored in 
    a database char field.

    fromJSON() converts the JSONified dictionaries back into Column
    objects, thus making the CollectionBackup behave just like a Collection
    object.

    """
 
    def toJSON(self, collection, user):
        """Convert the "pertinent" nested data structures of
        a Collection into a python dict and then into a JSON data structure
        using the json module from the standard library.
        
        Note: the user argument is already a Python string / JSON object
        
        """
        
        self.collection_id = collection.id
        self.dateElicited = collection.dateElicited
        self.datetimeEntered = collection.datetimeEntered
        self.datetimeModified = datetime.datetime.now()
        self.backuper = user
        self.title = collection.title
        self.type = collection.type
        self.description = collection.description
        self.contents = collection.contents

        if collection.speaker:
            self.speaker = json.dumps({
                'id': collection.speaker.id, 
                'firstName': collection.speaker.firstName, 
                'lastName': collection.speaker.lastName, 
                'dialect': collection.speaker.dialect
            })
        if collection.source:
            self.source = json.dumps({
                'id': collection.source.id, 
                'authorFirstName': collection.source.authorFirstName, 
                'authorLastName': collection.source.authorLastName, 
                'year': collection.source.year, 
                'fullReference': collection.source.fullReference
            })
        if collection.enterer:
            self.enterer = json.dumps({
                'id': collection.enterer.id, 
                'firstName': collection.enterer.firstName, 
                'lastName': collection.enterer.lastName
            })
        if collection.elicitor:
            self.elicitor = json.dumps({
                'id': collection.elicitor.id, 
                'firstName': collection.elicitor.firstName, 
                'lastName': collection.elicitor.lastName
            })

        # The Many-to-Many Collection-to-File relationship is represented by
        #  a list of JS objects in JSON.
        #  Why are not the MIMEType and other data included here or in the
        #  above FormBackup.toJSON() method?
        if collection.files:
            self.files = json.dumps([{
                'id': file.id, 
                'name': file.name, 
                'embeddedFileMarkup': file.embeddedFileMarkup, 
                'embeddedFilePassword': file.embeddedFilePassword} for file in collection.files])

        # The Many-to-Many Collection-to-Form relationship is recoverable from
        #  self.contents, so it is not re-stored as a JSON list of objects
        #  as is the Collection-to-File relationship (which is assumed to
        #  contain far fewer associations...)

    def fromJSON(self):
        """Convert the JSONified dictionaries back into Column objects, 
        thus making the CollectionBackup behave just like a Collection object.
        (Almost.)
        
        """

        if self.speaker:
            speaker = json.loads(self.speaker)
            self.speaker = Column()
            self.speaker.id = speaker['id']
            self.speaker.firstName = speaker['firstName']
            self.speaker.lastName = speaker['lastName']
            self.speaker.dialect = speaker['dialect']
        if self.source:
            source = json.loads(self.source)
            self.source = Column()
            self.source.id = source['id']
            self.source.authorFirstName = source['authorFirstName']
            self.source.authorLastName = source['authorLastName']
            self.source.year = source['year']
            self.source.fullReference = source['fullReference']
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


################################################################################
#################  File Class ##################################################
################################################################################

# Browser HTML5 audio compatibilities
#
#                        mp3     ogg     wav     au/snd      aif/aifc/aiff   
#    Firefox (Linux, Mac)N       Y       Y       N           N               
#    Chrome (Linux)      Y       Y       N       N           N               
#    Safari (Mac)        Y       N       N       Y           N

class File(object):

    def getHTMLRepresentation(self, size=u'long'):
        """Generates an HTML representation of the File.
        
        Four components:
        
        1. metadata
        2. associated Forms
        3. action buttons
        4. representation of the File's media
        
        """

        HTMLRepresentation = u''

        # Get a string representing the type of the file
        fileType = self.getFileType()

        # Get the metadata, associated Forms, action buttons and file data
        HTMLRepresentation += self.getMetaData(fileType)
        
        if size != u'short':
            HTMLRepresentation += self.getAssociatedForms()
            HTMLRepresentation += self.getButtons()

        HTMLRepresentation += self.getFileMedia(fileType)

        HTMLRepresentation += u'<div class="tableSpacerDiv"></div>'

        return HTMLRepresentation

    def getFileType(self):
        """Return the file type.  Should be one of ['audio', 'video', 'text',
        'image']
        
        """
        
        if app_globals.allowedFileTypes[self.MIMEtype]:
            return app_globals.allowedFileTypes[self.MIMEtype]
        else:
            return self.MIMEtype.split('/')[0]

    def getMetaData(self, fileType):
        """Returns an HTML table representation of the metadata of this File.

        """

        result = u'<table class="fileTable">'
        result += u'\n <tr>\n  <td class="fileTableRowLabel">ID</td>'
        result += u'\n  <td class="dataCell">%s</td>\n </tr>' % self.id
        result += u'\n <tr>\n  <td class="fileTableRowLabel">name</td>'
        result += u'\n  <td class="dataCellTr">%s</td>\n </tr>' % self.name
        result += u'\n <tr>\n  <td class="fileTableRowLabel">type</td>'
        result += u'\n  <td class="dataCell">%s</td>\n </tr>' % fileType
        result += u'\n <tr>\n  <td class="fileTableRowLabel">size</td>'
        result += u'\n  <td class="dataCell">%s</td>\n </tr>' % \
                  h.pretty_filesize(self.size)

        if self.description:
            result += u'\n <tr>\n  <td class="fileTableRowLabel">description</td>'
            result += u'\n  <td class="dataCell">%s</td>\n </tr>' % self.description

        if self.utteranceType:
            result += u'\n <tr>\n  <td class="fileTableRowLabel">utterance type</td>'
            result += u'\n  <td class="dataCell">%s</td>\n </tr>' % self.utteranceType

        result += u'\n <tr>\n  <td class="fileTableRowLabel">enterer</td>'
        result += u'\n  <td class="dataCell">%s %s</td>\n </tr>' % (
            self.enterer.firstName, self.enterer.lastName)

        if self.speaker:
            result += u'\n <tr>\n  <td class="fileTableRowLabel">speaker</td>'
            result += u'\n  <td class="dataCell">%s %s</td>\n </tr>' % (
                self.speaker.firstName, self.speaker.lastName)

        if self.elicitor:
            result += u'\n <tr>\n  <td class="fileTableRowLabel">elicitor</td>'
            result += u'\n  <td class="dataCell">%s %s</td>\n </tr>' (
                self.elicitor.firstName, self.elicitor.lastName)

        if self.dateElicited:
            result += u'\n <tr>\n  <td class="fileTableRowLabel">date elicited</td>'
            result += u'\n  <td class="dataCell">%s</td>\n </tr>' % \
                      self.dateElicited.strftime('%b %d, %Y')

        result += u'\n <tr>\n  <td class="fileTableRowLabel">time entered</td>'
        result += u'\n  <td class="dataCell">%s</td>\n </tr>' % \
                  self.datetimeEntered.strftime('%b %d, %Y at %I:%M %p')
        result += u'\n <tr>\n  <td class="fileTableRowLabel">last updated</td>'
        result += u'\n  <td class="dataCell">%s</td>\n </tr>' % \
                  self.datetimeModified.strftime('%b %d, %Y at %I:%M %p')
        result += u'</table>'

        return result

    def getButtons(self):
        """Return an HTML div containing links to various File actions: update,
        delete and associate.
        
        """

        updateURL = url(controller='file', action='update', id=self.id)
        deleteURL = url(controller='file', action='delete', id=self.id)
        associateURL = url(controller='file', action='associate', id=self.id)
        
        result = u'<div class="fileButtonsDiv">'
        
        result += u'\n <a href="%s" class="buttonLink" title="Edit this '
        result += u'File\'s data">' % updateURL
        result += u'\n  update\n </a>'
        
        result += u'\n <a href="%s" class="buttonLink" ' % deleteURL
        result += u'onclick="return confirmDelete(\'File\', %s)" ' % self.id
        result += u'title="Delete this File; confirmation will be requested">'
        result += u'\n  delete\n </a>'
        
        result += u'\n <a href="%s" class="buttonLink" ' % associateURL
        result += u'title="Associate one or more Forms to this File">\n  '
        result += u'associate\n </a>'
        
        result += u'</div>'

        return result
    
    def getAssociatedForms(self):
        """Return an HTML representation of the Forms that are associated to
        this File.

        """
        
        result = u''
        
        for form in self.forms:
            result += u'<div class="associatedEntitiesDiv">'

            maxLen = 20
            transcription = h.clip(
                form.grammaticality + form.transcription, maxLen)
            gloss = h.clip(
                form.glosses[0].glossGrammaticality + form.glosses[0].gloss,
                maxLen
            )
            
            disassociateURL = url(
                'disassociate', controller='file', id=self.id, otherID=form.id)
            disassociateTitle = u'Click to disassociate Form %s from File %s' % (
                form.id, self.id)
            viewURL = url(controller='form', action='view', id=form.id)
            viewTitle = u'Click to view more info about Form %s' % form.id
            
            result += u'\n Associated Form %s:' % form.id
            result += u'<span class="emphasize">%s</span>' % \
                      h.storageToOutputTranslate(transcription)
            result += u'\n&lsquo;%s&rsquo;' % h.literal(gloss)
            result += u' <div class="containerDivIndent">'
            result += u'\n  <a href="%s" class="buttonLink" ' % disassociateURL
            result += u'title="%s">disassociate</a>' % disassociateTitle
            result += u'\n  <a href="%s" class="buttonLink" title="%s">view</a>' % \
                      (viewURL, viewTitle)
            result += u'\n </div>\n</div>'

        return result

    def getFileMedia(self, fileType, hidden=True):
        """Returns a representation of the media of the File.  I.e., an <img />
        tag for image file types, etc.
        
        """
        
        fileReference = url('retrieve', path=self.name)
        
        result = u'<div class="fileContent">'

        if fileType == 'image':
            result += self.displayImage(fileReference, hidden)
        elif fileType == 'audio':
            result += self.displayAudio(fileReference, hidden)
        elif fileType == 'video':
            result += self.displayVideo(fileReference, hidden)
        else:
            result += self.displayTextual(fileReference, hidden)

        result += u'</div>'
        
        return result

    def displayImage(self, fileReference, hidden=True):
        """An OLD File representing an image is displayed using HTML's <img />
        tag.  The image is hidden by default and is revealed with a button
        click.
        
        """
        
        fileName = path.splitext(self.name)[0]
        buttonID = fileName + 'Button'

        style = u''
        if hidden:
            style = u' style="display:none;"'

        imgTag = u'\n<img alt="%s"%s src="%s" ' % \
            (self.name, style, fileReference)
        imgTag += u'class="imageFile" id="%s" />' %  fileName

        if hidden:
            result = u'<a onclick="addRemoveElement(\'%s\', \'%s\', \'image\', ' % \
                (fileName, buttonID)
            result += u'\'hide image|show image\');"'
            result += u' class="buttonLink" id="%s" title="show image embedded ' % \
                buttonID
            result += u'in the page">show image</a>'
            result += imgTag
        else:
            result = imgTag

        return result

    def displayAudio(self, fileReference, hidden=True):
        result = self.getJavaScriptForAudio()

        fileName = self.name.replace('.', '_') 
        uniqueNo = str(randrange(0,1000))
        uniqueFileName = fileName + uniqueNo

        # A button to create an audio player in the embeddedAudioDiv
        result += u'\n\n<a class="buttonLink" '
        result += u'title="click to show audio embedded in page" '
        result += u'onclick="playAudio(\'%s\', \'%s\', \'%s\', \'%s\')">' % \
            (fileReference, fileName, self.MIMEtype, uniqueFileName)
        result += u'play audio</a>'
        
        # A button that links directly to the audio file (for download)
        result += u'\n\n<a href="%s" class="buttonLink" ' % fileReference
        result += u'title="click to link to this audio file; '
        result += u'right-click to download this audio file">'
        result += u'link to audio</a>'
        
        # The embeddedAudioDiv for displaying the embedded audio
        result += u'\n\n<div id="%s" class="embeddedAudioDiv"></div>' % \
                  uniqueFileName

        return result

    def displayVideo(self, fileReference, hidden=True):
        """What's the problem here?...
        
        """
        
        return u'Video display has not yet been implemented ...'
    
    def displayTextual(self, fileReference, hidden=True):
        fileExtension = self.name.split('.')[-1]
        result = u'<a href="%s" class="buttonLink" ' % \
            fileReference
        result += u'title="right-click to download this %s file">' % \
            fileExtension
        result += u'link to text</a>'
        return result

    def getJavaScriptForAudio(self):
        return """
<script type="text/javascript">

  function playAudio(fileReference, fileName, MIMEtype, uniqueFileName)
  {
      var embeddedAudioDiv = document.getElementById(uniqueFileName);
      var useAudioTag = canUseHTMLAudioTag(MIMEtype);
      embeddedAudioDiv.style.display="block";
      embeddedAudioDiv.style.display="visible";
      if (useAudioTag)
      {
          var output = '<audio src="' + fileReference + '" controls="controls">';
          output += '</audio>';
      }
      else
      {
          var output = '<embed src="' + fileReference + '" autoplay="false" ';
          output += 'autostart="false" width="300" height="30" />';
      }
      embeddedAudioDiv.innerHTML = output;
  }

  function canUseHTMLAudioTag(MIMEtype)
  {
      var audio  = document.createElement("audio");
      canPlayMIMEtype = (typeof audio.canPlayType === "function" && audio.canPlayType(MIMEtype) !== "");
      return(canPlayMIMEtype);
  }

</script>"""


if __name__ == '__main__':
    form = Form()

    form.transcription = u'anna ninaa itsinoyii ami aakii ki ikaakomimmoka matonni'
    form.morphemeBreak = u'ann-wa ninaa it-ino-yii am-yi aakii ki iik-waakomimm-ok-wa matonni'
    form.morphemeGloss = u'DEM-3PROX man LOC-see-DIR DEM-3OBV woman and INT-love-INV-3SG yesterday'
    form.gloss = u'the man saw that woman and he loved her yesterday'   

    preppedForm = getPreppedForm(form)
    print '%s\n%s\n%s\n%s' % (form.transcription, form.morphemeBreak, form.morphemeGloss, form.gloss)
