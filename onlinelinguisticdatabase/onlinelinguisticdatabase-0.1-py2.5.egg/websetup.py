# −*− coding: UTF−8 −*−
"""Setup the onlinelinguisticdatabase application"""
import logging
import hashlib
import codecs
import string
import datetime
import os

from pylons import config

from onlinelinguisticdatabase.config.environment import load_environment
from onlinelinguisticdatabase.model import meta
from onlinelinguisticdatabase import model
import onlinelinguisticdatabase.lib.helpers as h
import onlinelinguisticdatabase.lib.languages.iso_639_3 as iso_639_3

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup onlinelinguisticdatabase here"""
    load_environment(conf.global_conf, conf.local_conf)

    # Create the tables if they don't already exist
    meta.metadata.create_all(bind=meta.engine)

    # Create the files directory and the archived_files and researchers
    #  subdirectories
    try:
        os.mkdir('files')
    except OSError:
        pass
    
    try:
        os.mkdir(os.path.join('files', 'archived_files'))
    except OSError:
        pass

    try:
        os.mkdir(os.path.join('files', 'researchers'))
    except OSError:
        pass

    # Add an administrator and some general language data

    # Administrator
    log.info("Creating a default administrator.")
    admin = model.User()
    admin.firstName = u'Admin'
    admin.lastName = u'Admin'
    admin.username = u'admin'
    admin.email = u'admin@example.com'
    admin.password = unicode(hashlib.sha224(u'admin').hexdigest())
    admin.role = {'0': u'administrator', '1': u'mirror'}[config['mirror']]
    admin.collectionViewType = u'long'
    admin.inputOrthography = None
    admin.outputOrthography = None
    h.createResearcherDirectory(admin)
    
    # Researcher
    log.info("Creating a default researcher.")
    researcher = model.User()
    researcher.firstName = u'Researcher'
    researcher.lastName = u'Researcher'
    researcher.username = u'researcher'
    researcher.email = u'researcher@example.com'
    researcher.password = unicode(hashlib.sha224(u'researcher').hexdigest())
    researcher.role = u'researcher'
    researcher.collectionViewType = u'long'
    researcher.inputOrthography = None
    researcher.outputOrthography = None
    h.createResearcherDirectory(researcher)

    # Learner
    log.info("Creating a default learner.")
    learner = model.User()
    learner.firstName = u'Learner'
    learner.lastName = u'Learner'
    learner.username = u'learner'
    learner.email = u'learner@example.com'
    learner.password = unicode(hashlib.sha224(u'learner').hexdigest())
    learner.role = u'learner'
    learner.collectionViewType = u'long'
    learner.inputOrthography = None
    learner.outputOrthography = None
    h.createResearcherDirectory(learner)
    
    # Default Home Page
    homepage = model.Page()
    homepage.name = u'home'
    homepage.heading = u'Welcome to the OLD'
    homepage.content = u"""
The Online Linguistic Database is a web application that helps people to
document, study and learn a language.
        """
    homepage.markup = u'restructuredtext'

    # Default Help Page
    helppage = model.Page()
    helppage.name = u'help'
    helppage.heading = u'OLD Application Help'
    helppage.content = u"""
Welcome to the help page of this OLD application.

This page should contain content entered by your administrator.
        """
    helppage.markup = u'restructuredtext'

    # Enter ISO-639-3 Language data into the languages table
    log.info("Retrieving ISO-639-3 languages data.")
    languages = [getLanguageObject(language) for language in iso_639_3.languages]

    # Default Application Settings
    log.info("Generating default settings.")
    orthography = u', '.join(list(string.ascii_lowercase))
    applicationSettings = model.ApplicationSettings()
    applicationSettings.objectLanguageName = u'Anonymous'
    applicationSettings.storageOrthography = u'Object Language Orthography 1'
    applicationSettings.defaultInputOrthography = u'Object Language Orthography 1'
    applicationSettings.defaultOutputOrthography = u'Object Language Orthography 1'
    applicationSettings.objectLanguageOrthography1 = orthography
    applicationSettings.objectLanguageOrthography1Name = u'English alphabet'
    applicationSettings.metaLanguageName = u'Unknown'
    applicationSettings.metaLanguageOrthography = orthography
    applicationSettings.headerImageName = u''
    applicationSettings.colorsCSS = u'green.css'
    applicationSettings.OLO1Lowercase = u'1'
    applicationSettings.OLO1InitialGlottalStops = u'1'
    applicationSettings.OLO2Lowercase = u'1'
    applicationSettings.OLO2InitialGlottalStops = u'1'
    applicationSettings.OLO3Lowercase = u'1'
    applicationSettings.OLO3InitialGlottalStops = u'1'
    applicationSettings.OLO4Lowercase = u'1'
    applicationSettings.OLO4InitialGlottalStops = u'1'
    applicationSettings.OLO5Lowercase = u'1'
    applicationSettings.OLO5InitialGlottalStops = u'1'
    applicationSettings.morphemeBreakIsObjectLanguageString = u'yes'

    # Initialize the database
    if config['addLanguageData'] == '0':
        data = [
            admin, researcher, learner, homepage, helppage, applicationSettings
        ]
    else:
        data = [
            admin, researcher, learner, homepage, helppage, applicationSettings
        ] + languages
        
    log.info("Adding defaults.")
    meta.Session.add_all(data)
    meta.Session.commit()

    log.info("OLD successfully set up.")

def getLanguageObject(languageList):
    language = model.Language()
    language.Id = languageList[0]
    language.Part2B = languageList[1]
    language.Part2T = languageList[2]
    language.Part1 = languageList[3]     
    language.Scope = languageList[4]
    language.Type = languageList[5]
    language.Ref_Name = languageList[6]
    language.Comment = languageList[7]     
    return language