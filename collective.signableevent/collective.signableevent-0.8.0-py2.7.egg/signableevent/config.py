"""Common configuration constants
"""

PROJECT_NAME = 'collective.signableevent'

ADD_PERMISSIONS = {
    # -*- extra stuff goes here -*-
    'EventSignup': 'collective.signableevent: Add EventSignup',
    'SignableEvent': 'collective.signableevent: Add SignableEvent',
}

SKINS_DIR = 'skins'
GLOBALS = globals()

CONFIGLETS = (
    {'id'           : "signableevents",
     'name'         : 'Export CSV',
     'action'       : 'signableevents_allsigned_csv',
     'condition'    : '',
     'category'     : 'Products',
     'visible'      : 1,
     'appId'        : PROJECT_NAME,
     'permission'   : 'Manage portal',
     'imageUrl'     : 'event_signup_icon.png' },
    )