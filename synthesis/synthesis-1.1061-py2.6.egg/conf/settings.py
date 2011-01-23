#!/usr/bin/env python
import os
#import pydevd

# Settings for synthesis.py

# current Min Python version is 2.4
MINPYVERSION = '2.4'

MODE = 'TEST'   # This is the switch that runs the program in 'TEST' or 'PROD' Mode. 
#MODE = 'PROD'
SKIP_VALIDATION_TEST = False

#The GUI setting determines in Filehandler() will use a GUI controller to start and stop the service.  
#In practical terms, this is determined by whether Windows is running or Unix, since the GUI was built for Windows 
#However, the gui is cross-platform, so the GUI setting should be actually independent of the platform
GUI = False  
# DB settings:
DB_DATABASE = "password_here"
DB_USER = "username_here"
DB_PASSWD = "password"
DB_PORT = 5432
DB_HOST = "localhost"

# Which SvcPt version is this site using, if any?  This version number pulls the xsd schema in and configures the plug in as well.
SVCPT_VERSION = '406'                    # this is 4.06
# uses current working directory, uncomment the line if the output path needs to be elsewhere.
#SOURCE_PATH = 'synthesis/synthesis'
#SOURCE_PATH = 'synthesis'
#BASE_PATH = os.path.join(os.getcwd(), SOURCE_PATH)
BASE_PATH = "/home/username_here/synthesis_install_location/synthesis/synthesis"
print "BASE_PATH is: ", BASE_PATH
#import pydevd; pydevd.settrace()
#ABS_SOURCE_PATH = os.path.abspath(os.getcwd() + SOURCE_PATH)
PATH_TO_GPG = '/usr/bin/gpg'
PGPHOMEDIR = ''
PASSPHRASE = ''
JFCS_SOURCE_ID = 734
JFCS_AGENCY_ID = 711
JFCS_SERVICE_ID = 705


# Input files Processing path
# New 'Customers' input file path must be put into this 'list'.  Add it to the list mechanism.  
INPUTFILES_PATH = [
            BASE_PATH + "/input_files"
            ,
            ]
WEB_SERVICE_INPUTFILES_PATH = [
            BASE_PATH + "/ws_input_files"
            ,
            ]
# subfolder 
#XSD_PATH = SOURCE_PATH + "/" + "xsd"
XSD_PATH = "xsd"
# file path subdirectories
OUTPUTFILES_PATH = os.path.join(BASE_PATH, "output_files")
if not os.path.exists(OUTPUTFILES_PATH):
    os.mkdir(OUTPUTFILES_PATH)
    
USEDFILES_PATH = os.path.join(BASE_PATH, "used_files")
if not os.path.exists(USEDFILES_PATH):
    os.mkdir(USEDFILES_PATH)
    
FAILEDFILES_PATH = os.path.join(BASE_PATH, "failed_files")
if not os.path.exists(FAILEDFILES_PATH):
    os.mkdir(FAILEDFILES_PATH)

#logging settings file location setup
logging_ini_file_name = 'logging.ini'
relative_logging_ini_filepath = os.path.join(BASE_PATH, logging_ini_file_name)
logging_ini_filepath = os.path.abspath(relative_logging_ini_filepath)
print 'logging.ini filepath is at: ', logging_ini_filepath
if not os.path.isfile(logging_ini_filepath):
    print "no logging.ini found"
LOGGING_INI = logging_ini_filepath
    
LOGS = os.path.join(BASE_PATH, "logs")
if not os.path.exists(LOGS):
    os.mkdir(LOGS)

PROCESSED_PATH = ""

SCHEMA_DOCS = {
'hud_hmis_xml_2_8':os.path.join(BASE_PATH, XSD_PATH, 'versions','HMISXML','28','HUD_HMIS.xsd'),               
'hud_hmis_xml_3_0':os.path.join(BASE_PATH, XSD_PATH, 'versions','HMISXML','30','HUD_HMIS.xsd'),
'svcpoint_2_0_xml':os.path.join(BASE_PATH, XSD_PATH, 'versions','SVCPT', SVCPT_VERSION, 'sp.xsd'),    # Service Point current version (output)
'jfcs_service_event_xml':os.path.join(BASE_PATH, XSD_PATH, 'JFCS_SERVICE_EVENT.xsd'),
'jfcs_client_xml':os.path.join(BASE_PATH, XSD_PATH, 'JFCS_CLIENT.xsd'),
'operation_par_xml':os.path.join(BASE_PATH, XSD_PATH, 'Operation_PAR_Extend_HUD_HMIS_2_8.xsd'),
'occ_hud_hmis_xml_3_0':os.path.join(BASE_PATH, XSD_PATH, 'OCC_Extend_HUD_HMIS.xsd')
               }

DEBUG = True								# Debug the application layer
DEBUG_ALCHEMY = False						# Debug the ORM Layer
DEBUG_DB = False								# Debug the DB layer of the application

# This mechanism provides an override to the settings above.  create a file called local_settings.py and simply
# override the values like BASE_PATH='/home/mypath'.  Then import like this: from conf import settings
# this will bring in all of settings.py's values and have the overriddin values of local_settings.py

# email configuration
SMTPSERVER = 'localhost'
SMTPPORT = 25
SMTPSENDER = 'me@localhost'
SMTPSENDERPWD = 'mysecret'

# SMTP Mail recipients is a dictionary that must be defined for each source of input files
SMTPRECIPIENTS =	{
     "/home/username_here/synthesis_install_location/synthesis/synthesis/input_files":
		{
        'VENDOR_NAME': 'SomeVendor',
		'SMTPTOADDRESS': ['someone@somedomain.com',],
		'SMTPTOADDRESSCC': [],
		'SMTPTOADDRESSBCC': [],
		'FINGERPRINT':'',
		'USES_ENCRYPTION':False
		}
	,"~/workspace/synthesis/installer/build/InputFiles2":
		{
        'VENDOR_NAME': 'SomeVendor2',
		'SMTPTOADDRESS': ['admin@superhost.com',],
		'SMTPTOADDRESSCC': [],
		'SMTPTOADDRESSBCC': [],
		'FINGERPRINT':'',
		'USES_ENCRYPTION':True
		}
	,"~/workspace/synthesis/installer/build/InputFiles3":
		{
		'VENDOR_NAME': '',
        'SMTPTOADDRESS': ['sammy.davis@jr.com',],
		'SMTPTOADDRESSCC': [],
		'SMTPTOADDRESSBCC': [],
		'FINGERPRINT':'',
		'USES_ENCRYPTION':False
		}
# output processing
    ,"~/workspace/synthesis/installer/build/OutputFiles":
		{
		'VENDOR_NAME': '',
        'SMTPTOADDRESS': ['user@host.com',],
		'SMTPTOADDRESSCC': [],
		'SMTPTOADDRESSBCC': [],
		'FINGERPRINT':'',
		'USES_ENCRYPTION':False
		}
    ,"~/workspace/synthesis/installer/build/OutputFiles2":
		{
		'VENDOR_NAME': '',
        'SMTPTOADDRESS': ['admin@somehost.com',],
		'SMTPTOADDRESSCC': [],
		'SMTPTOADDRESSBCC': [],
		'FINGERPRINT':'',
		'USES_ENCRYPTION':True
		}
	}

try:
    from local_settings import *
except ImportError:
    pass


