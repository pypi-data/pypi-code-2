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

"""This module contains general-purpose functions used in the OLD

"""

import os
import shutil
import re
import helpers as h
import codecs
import htmlentitydefs
import string

from docutils import core

from pylons import session, app_globals
from pylons import config

from sqlalchemy import desc

import onlinelinguisticdatabase.model as model
import onlinelinguisticdatabase.model.meta as meta


def removeWhiteSpace(string):
    """Remove leading and trailing whitespace, newlines and tabs;
    reduce multiple spaces to single ones."""
    string = string.strip()
    string = string.replace('\n', ' ')
    string = string.replace('\t', ' ')
    patt = re.compile(' {2,}')
    string = patt.sub(' ', string)
    return string


def removeAllWhiteSpace(string):
    """Remove all spaces, newlines and tabs."""
    string = string.replace(u'\n', u'')
    string = string.replace(u'\t', u'')
    string = string.replace(u' ', u'')
    print '\n\n\n|%s|\n\n\n' % string
    return string


def getUserID():
    """Returns logged in user's ID if a user is logged in; otherwise, None."""
    if 'user_id' in session:
        return session['user_id']
    else:
        return None


def pretty_filesize(bytes):
    """Converts filesize in bytes to a string representation
    in KB, MB or GB, as appropriate."""
    if bytes >= 1073741824:
        return str(round(bytes / 1024 / 1024 / 1024.0, 2)) + ' GB'
    elif bytes >= 1048576:
        return str(round(bytes / 1024 / 1024.0, 1)) + ' MB'
    elif bytes >= 1024:
        return str(round(bytes / 1024.0, 1)) + ' KB'
    elif bytes < 1024:
        return str(bytes) + ' bytes'


def filesize_to_bytes(value, unit):
    """Converts filesize in KB, MB or GB to an integer representing bytes."""
    value = float(value)
    if unit == 'GB':
        result = value * 1024 * 1024 * 1024
    elif unit == 'MB':
        result = value * 1024 * 1024
    elif unit == 'KB':
        result = value * 1024
    else:
        result = value
    return result


def putOrthographyTranslatorsIntoSession():
    """Three variables need defining:
    
    1. storageToOutputTranslator
    2. inputToStorageTranslator
    3. storageToInputTranslator
    
    Whether these variables point to OrthographyTranslator instances or to None,
    depends on the user's user-specific settings.
    
    If (1) the user has chosen an input orthography and (2) that orthography
    differs from the system's storage orthography and (3) that orthography
    differs from the system's default input orthography and (4) that orthography
    is a key in app_globals.OLOrthographies, then set inputToStorageTranslator
    and storageToInputTranslator to the appropriate OrthographyTranslator
    instances.  Do similarly for the storage-output connection.
    
    """

    if session['user_inputOrthography'] and \
        (app_globals.storageOrthography != \
        session['user_inputOrthography']) and (
        session['user_inputOrthography'] != \
        app_globals.defaultInputOrthography) and (
        session['user_inputOrthography'] in app_globals.OLOrthographies):
        # Update the inputToStorageTranslator
        session['user_inputToStorageTranslator'] = h.OrthographyTranslator(
            app_globals.OLOrthographies[session['user_inputOrthography']][1],
            app_globals.storageOrthography[1]
        )
        # Update the storageToInputTranslator
        session['user_storageToInputTranslator'] = h.OrthographyTranslator(
            app_globals.storageOrthography[1],
            app_globals.OLOrthographies[session['user_inputOrthography']][1]
        )
    else:
        session['user_inputToStorageTranslator'] = None
        session['user_storageToInputTranslator'] = None

    if session['user_outputOrthography'] and \
        (app_globals.storageOrthography != \
        session['user_outputOrthography']) and (
        session['user_outputOrthography'] != \
        app_globals.defaultOutputOrthography) and (
        session['user_outputOrthography'] in app_globals.OLOrthographies):
        session['user_storageToOutputTranslator'] = h.OrthographyTranslator(
            app_globals.storageOrthography[1],
            app_globals.OLOrthographies[session['user_outputOrthography']][1]
        )
    else:
        session['user_storageToOutputTranslator'] = None

    session.save()


def getAuthorizedUserIntoSession(user):
    """Put user-specific info into the session."""
    session['user_id'] = user.id
    session['user_username'] = user.username
    session['user_role'] = user.role
    session['user_firstName'] = user.firstName
    session['user_lastName'] = user.lastName
    session['user_collectionViewType'] = user.collectionViewType
    session['user_inputOrthography'] = user.inputOrthography
    session['user_outputOrthography'] = user.outputOrthography
    session.save()
    putOrthographyTranslatorsIntoSession()


def updateSessionAndGlobals(user):
    """Updates both the current user's info in the session and
    the variable app_globals attributes."""
    # Update session with given user
    getAuthorizedUserIntoSession(user)
    # Update the tags options (i.e., possible speakers, elicitors, sources, etc.)
    tags = h.getTags()
    app_globals.speakers = tags['speakers']
    app_globals.users = tags['users']
    app_globals.sources = tags['sources']
    app_globals.syncats = tags['syncats']
    app_globals.keywords = tags['keywords']
    app_globals.elicitationMethods = tags['elicitationMethods']


def applicationSettingsToAppGlobals(applicationSettings=None):
    """This function puts the application settings data into app_globals.
    
    If an applicationSettings object is not received, we try to retrieve one
    from the model.
    """
    # If we have not been passed an applicationSettings object, create one
    #  using data from the model.  Note: new application settings are simply
    #  added to the application_settings table; thus we get the current settings
    #  by selecting that with the highest ID
    if not applicationSettings:
        applicationSettings_q = meta.Session.query(
            model.ApplicationSettings).order_by(
                desc(model.ApplicationSettings.id
                )
            )
        applicationSettings = applicationSettings_q.first()
    
    # If we have an application settings object, update app_globals using it
    if applicationSettings:
        app_globals.objectLanguageName = applicationSettings.objectLanguageName
        app_globals.metaLanguageName = applicationSettings.metaLanguageName
        app_globals.headerImageName = applicationSettings.headerImageName
        app_globals.colorsCSS = applicationSettings.colorsCSS.encode('ascii')
        app_globals.morphemeBreakIsObjectLanguageString = \
                        applicationSettings.morphemeBreakIsObjectLanguageString

        # Create the app_globals.OLOrthographies dictionary with the following
        #  structure: {identifier: (name, OrthographyObject), etc.}
        #  e.g., {'Object Language Orthography 1': ('NAPA', <Orthography object>)}
        app_globals.OLOrthographies = {}
        for i in range(1, 6):
            identifier = 'Object Language Orthography %s' % str(i)
            name = getattr(applicationSettings,
                        'objectLanguageOrthography%sName' % str(i))
            orthography = getattr(applicationSettings,
                        'objectLanguageOrthography%s' % str(i))
            lowercase = getattr(applicationSettings,
                        'OLO%sLowercase' % str(i))
            initialGlottalStops = getattr(applicationSettings,
                        'OLO%sInitialGlottalStops' % str(i))
            app_globals.OLOrthographies[identifier] = (
                name,
                h.Orthography(
                    orthography,
                    lowercase=lowercase,
                    initialGlottalStops=initialGlottalStops
                )
            )

        # Storage, Input and Output Orthographies point to the appropriate
        #  (name, <Orthography object>) tuples in app_globals.OLOrthographies
        app_globals.storageOrthography = app_globals.OLOrthographies[
            applicationSettings.storageOrthography]
        app_globals.defaultInputOrthography = app_globals.OLOrthographies[
            applicationSettings.defaultInputOrthography]
        app_globals.defaultOutputOrthography = app_globals.OLOrthographies[
            applicationSettings.defaultOutputOrthography]

        # Get the orthography of the metalanguage as an Orthography object
        app_globals.metaLanguageOrthography = \
            h.Orthography(applicationSettings.metaLanguageOrthography)
        
        # inputToStorageTranslator
        #  If the defaultInputOrthography differs from the storageOrthography,
        #  set app_globals.inputToStorageTranslator to the appropriate
        #  OrthographyTranslator instance; otherwise, set it to None
        if applicationSettings.storageOrthography != \
                                applicationSettings.defaultInputOrthography:
            app_globals.inputToStorageTranslator = h.OrthographyTranslator(
                app_globals.defaultInputOrthography[1],
                app_globals.storageOrthography[1]
            )
        else:
            app_globals.inputToStorageTranslator = None

        # storageToInputTranslator
        #  If the defaultInputOrthography differs from the storageOrthography,
        #  set app_globals.storageToInputTranslator to the appropriate
        #  OrthographyTranslator instance; otherwise, set it to None
        #  Note: this translator is required for updating data.
        if applicationSettings.storageOrthography != \
                                applicationSettings.defaultInputOrthography:
            app_globals.storageToInputTranslator = h.OrthographyTranslator(
                app_globals.storageOrthography[1],
                app_globals.defaultInputOrthography[1]
            )
        else:
            app_globals.storageToInputTranslator = None
            
        # outputToStorageTranslator
        #  If the defaultOutputOrthography differs from the storageOrthography,
        #  set app_globals.storageToInputTranslator to the appropriate
        #  OrthographyTranslator instance; otherwise, set it to None
        if applicationSettings.storageOrthography != \
                                applicationSettings.defaultOutputOrthography:
            app_globals.storageToOutputTranslator = h.OrthographyTranslator(
                app_globals.storageOrthography[1],
                app_globals.defaultOutputOrthography[1]
            )
        else:
            app_globals.storageToOutputTranslator = None

    # We have no application settings object, so update app_globals with some
    #  default application settings data.
    else:
        defaultOrthography = ','.join(list(string.ascii_lowercase))
        app_globals.objectLanguageName = u'Anonymous'
        app_globals.metaLanguageName = u'Unknown'
        app_globals.headerImageName = u''
        app_globals.colorsCSS= 'green.css'
        app_globals.metaLanguageOrthography = h.Orthography(defaultOrthography)
        app_globals.OLOrthographies = {
            u'Object Language Orthography 1': (
                u'Unnamed',
                h.Orthography(
                    defaultOrthography, lowercase=1, initialGlottalStops=1
                )
            )
        }
        app_globals.storageOrthography = app_globals.OLOrthographies[
            u'Object Language Orthography 1']
        app_globals.defaultInputOrthography = app_globals.OLOrthographies[
            u'Object Language Orthography 1']
        app_globals.defaultOutputOrthography = app_globals.OLOrthographies[
            u'Object Language Orthography 1']
        app_globals.morphemeBreakIsObjectLanguageString = u'yes'
        app_globals.inputToStorageTranslator = None
        app_globals.storageToOutputTranslator = None


################################################################################
# INPUT TO STORAGE TRANSLATE FAMILY OF FUNCTIONS
################################################################################


def getInputToStorageTranslator():
    """Looks for an input-to-storage translator first in the session and then
    in the globals.  If no translator is found, return the identity function.
    
    """
    if session['user_inputToStorageTranslator']:
        return lambda x: h.literal(session[
            'user_inputToStorageTranslator'].translate(x))
    elif app_globals.inputToStorageTranslator:
        return lambda x: h.literal(
            app_globals.inputToStorageTranslator.translate(x))
    else:
        return lambda x: x


def inputToStorageTranslate(string, isMBField=False):
    """This function translates input strings of the object language into the 
    appropriate storage orthography.  An input-to-storage translator is first
    looked for in the user-specific session dict, then in the system-wide
    app_globals; if no translator is found, the string is simply returned.
    
    The isMBField indicates whether the input string is from the morpheme break
    field.  If it is, and if this application does not treat morpheme break
    data as object language strings, then return the string.
    
    """
    if isMBField and app_globals.morphemeBreakIsObjectLanguageString == u'no':
        return string
    else:
        return getInputToStorageTranslator()(string)


def inputToStorageTranslateOLOnly(string):
    """This function behaves just like inputToStorageTranslate except that it
    applies only to strings in <obl></obl> tags.
    
    """
    patt = re.compile('<obl>(.*?)</obl>')
    translator = getInputToStorageTranslator()
    return patt.sub(lambda x: translator(x.group()), string)


################################################################################


################################################################################
# STORAGE TO INPUT TRANSLATE FAMILY OF FUNCTIONS
################################################################################


def getStorageToInputTranslator():
    """Looks for a storage-to-input translator first in the session and then
    in the globals.  If no translator is found, return the identity function.
    
    """
    if session['user_storageToInputTranslator']:
        return lambda x: h.literal(session[
            'user_storageToInputTranslator'].translate(x))
    elif app_globals.storageToInputTranslator:
        return lambda x: h.literal(
            app_globals.storageToInputTranslator.translate(x))
    else:
        return lambda x: x


def storageToInputTranslate(string, isMBField=False):
    """This function translates storage strings of the object language into the 
    appropriate input orthography.  A storage-to-input translator is first
    looked for in the user-specific session dict, then in the system-wide
    app_globals; if no translator is found, the string is simply returned.
    
    The isMBField indicates whether the input string is from the morpheme break
    field.  If it is, and if this application does not treat morpheme break
    data as object language strings, then return the string.
    
    """
    if isMBField and app_globals.morphemeBreakIsObjectLanguageString == u'no':
        return string
    else:
        return getStorageToInputTranslator()(string)


def storageToInputTranslateOLOnly(string):
    """This function behaves just like storageToInputTranslate except that it
    applies only to strings in <obl></obl> tags.
    
    """
    # '?' in regex gets us a non-greedy match, good for parsing xml
    patt = re.compile('<obl>(.*?)</obl>')
    translator = getStorageToInputTranslator()
    return patt.sub(lambda x: translator(x.group()), string)


################################################################################



################################################################################
# STORAGE TO OUTPUT TRANSLATE FAMILY OF FUNCTIONS
################################################################################


def getStorageToOutputTranslator():
    """Looks for a storage-to-input translator first in the session and then
    in the globals.  If no translator is found, return the identity function.
    
    """
    if 'user_storageToOutputTranslator' in session and \
    session['user_storageToOutputTranslator']:
        return lambda x: h.literal(session[
            'user_storageToOutputTranslator'].translate(x))
    elif app_globals.storageToOutputTranslator:
        return lambda x: h.literal(
            app_globals.storageToOutputTranslator.translate(x))
    else:
        return lambda x: h.literal(x)


def storageToOutputTranslate(string, isMBField=False):
    """This function translates storage strings of the object language into the 
    appropriate output orthography.  A storage-to-output translator is first
    looked for in the user-specific session dict, then in the system-wide
    app_globals; if no translator is found, the string is simply returned.
    
    The isMBField indicates whether the input string is from the morpheme break
    field.  If it is, and if this application does not treat morpheme break
    data as object language strings, then return the string.
    
    """
    if isMBField and app_globals.morphemeBreakIsObjectLanguageString == u'no':
        return string
    else:
        return getStorageToOutputTranslator()(string)


def storageToOutputTranslateOLOnly(string):
    """This function behaves just like storageToOutput except that it applies
    only to strings in <obl></obl> tags.
    
    """
    patt = re.compile('<obl>(.*?)</obl>')
    translator = getStorageToOutputTranslator()
    return patt.sub(lambda x: translator(x.group()), string)


################################################################################


def getInputOrthographyAsString():
    """Returns a string representing the input orthography.  Looks first for a
    user-specific value in the session, then a global value in app_globals.  If
    nothing is found, returns empty string.
    
    """
    if 'user_inputOrthography' in session and session['user_inputOrthography']:
        return app_globals.OLOrthographies[session['user_inputOrthography']][1].orthographyAsString
    elif hasattr(app_globals, 'defaultInputOrthography') and \
        app_globals.defaultInputOrthography[1]:
        return app_globals.defaultInputOrthography[1].orthographyAsString
    else:
        return ''


def getObjectLanguageDetails():
    """I don't know what this function was supposed to be for..."""
    pass


def escapeUnderscores(string):
    return string.replace('_', '\_')


# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.
def unescape(text):
    """This function was copied from somewhere (...).  It is used in the
    getmatchinglanguages function of the SettingsController.
    """
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)


def tablify(listOfItems, maxCols, tableClass=None, tableId=None):
    """Returns an HTML table where each item from
    listOfItems occupies a single cell and where
    there are no more than maxCols columns.
    """
    numEmptyCells = maxCols - (len(listOfItems) % maxCols)
    if tableClass:
        tClass = " class='%s'" % tableClass
    else:
        tClass = ''
    if tableId:
        tId = " id='%s'" % tableId
    else:
        tId = ''
    result = '\n\n<table%s%s>' % (tClass, tId)
    for index in range(len(listOfItems)):
        noZeroIndex = index + 1
        if noZeroIndex % maxCols is 1:
            result += '\n\t<tr>\n\t\t<td>%s</td>' % listOfItems[index]
        elif noZeroIndex % maxCols is 0:
            result += '\n\t\t<td>%s</td>\n\t</tr>' % listOfItems[index]
        else:
            result += '\n\t\t<td>%s</td>' % listOfItems[index]
    if numEmptyCells != maxCols:
        result += '%s\n\t</tr>' % ('\n\t\t<td></td>' * numEmptyCells)
    result += '\n</table>\n\n'
    return result


def clip(string, maxLen):
    """Return the first maxLen characters of the input string."""
    if len(string) < maxLen:
        return string
    else:
        return string[:maxLen] + '...'


def rst2html(string):
    """Use docutils.core to return a string of restructuredtext as HTML.
    """
    result = core.publish_parts(string, writer_name='html')
    return result['html_body']


xelatexCovingtonPreamble = u"""\\usepackage{fontspec} 
% Font selection for XeLaTeX; see fontspec.pdf for documentation

\\defaultfontfeatures{Mapping=tex-text} 
% to support TeX conventions like ``---''

\\usepackage{xunicode} 
% Unicode support for LaTeX character names (accents, European chars, etc)

\\usepackage{xltxtra}
% Extra customizations for XeLaTeX

\\setmainfont{Aboriginal Serif} 
% set the main body font, assumes Aboriginal Sans is installed

\\usepackage{covington}
% the covington package formats IGT"""


def rst2latex(string):
    """Use docutils.core to return a string of restructuredtext as a full LaTeX
    document.  Actually, this uses string replacement hacks to make a functional
    (so far?) XeLaTeX document.  These hacks consist of removing the
    '\usepackage[utf8]{inputenc}' declaration and adding some XeLaTeX commands
    to the preamble.
    
    """
    result = core.publish_parts(string, writer_name='latex')['whole']
    result = result.replace('\\usepackage[utf8]{inputenc}', '')
    result = result.replace('%%% Body', xelatexCovingtonPreamble + '\n\n%%% Body')
    return result


def getOrdString(string):
    """Take a string and return a space-delimited string of unicode code points
    (in standard U+XXXX notation) corresponding to each character in the string.
    
    """
    result = ''
    for char in string:
        result += 'U+%0.4X ' % ord(char)
    return result


def getKeyboardTable(fieldId):
    """Create the keyboardTable to be displayed under the input field with id =
    fieldId.  The graphs of keyboard are those of the input orthography.
    
    """
    inputOrthographyAsString = getInputOrthographyAsString()
    keys = inputOrthographyAsString.replace('[', '').replace(']', '').split(',')
    keys = ['<a class="key" title="Click this key to insert \'%s\' into the %s field" \
            onclick="graphToInput(\'%s\', \'%s\');">%s</a>' \
            % (x.replace("'", "\\'"), fieldId, x.replace("'", "\\'"), fieldId, \
            x) for x in keys]
    return h.literal(h.tablify(keys, 10, 'keyboardTable'))
    

def createResearcherDirectory(researcher):
    """Creates a directory named researcher.username in files/researchers/.
    """
    directoryPath = os.path.join(
        config['app_conf']['permanent_store'], 'researchers', researcher.username)
    try:
        os.mkdir(directoryPath)
    except OSError:
        pass


def destroyResearcherDirectory(researcher):
    """Destroys the directory named researcher.username in files/researchers/.
    """
    directoryPath = os.path.join(
        config['app_conf']['permanent_store'], 'researchers', researcher.username)
    shutil.rmtree(directoryPath, ignore_errors=True)


def latexSmallCaps(string):
    """Return a string converted to lowercase within a LaTeX smallcaps
    expression (\textsc{}).
    
    """
    if string.isupper():
        return '\\textsc{%s}' % string.lower()
    else:
        return string


def capsToLatexSmallCaps(string):
    """Function used to convert uppercase morpheme glosses to LaTeX smallcaps.
    
    """
    temp = re.split('(%s| )' % '|'.join(app_globals.validDelimiters), string)
    return ''.join([latexSmallCaps(x) for x in temp])


def getListOfLanguages():
    """ Function returns the ISO 639-3 Code Set
    (http://www.sil.org/iso639-3/download.asp) as a list.
    
    Expects a UTF-8 file named 'iso-639-3.tab' in lib/languages. 
    
    """
    file = codecs.open(
        os.path.join(
            config['pylons.paths']['root'], 'lib', 'languages', 'iso-639-3.tab'
        ),
        'r', 'utf-8'
    )
    temp = [x.split('\t') for x in file]
    return temp

def commatizeNumberString(numberString):
    if len(numberString) > 3:
        numberString = '%s,%s' % (numberString[:-3], numberString[-3:])
    if len(numberString) > 7:
        numberString = '%s,%s' % (numberString[:-7], numberString[-7:])
    return numberString