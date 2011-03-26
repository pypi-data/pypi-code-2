# Lilium DNA #########################################################
#
# Little beautiful Lilium.
#
# Do not touch the Lilium. Consider deriving instead.
#
######################################################################

import os

from utils import _n_en, _sz_c

liliumDNA = {
    'children': [],
    'kv': None,
    'host': [],

    # Names
    'root': 'lilium',
    '_base': {
        'title': 'Zima image board',
        'description': '',
        'inlines': [
            {'style': 'zima.css'},
            {'style': 'wakamark.css'},
            {'script': 'jquery.js'},
            {'script': 'zima.js'}
            ],
        'footer': [
            {'link': 'http://google.com/search?q=zima', 
             'caption':'zima'},
            {'link': 'http://wakaba.c3.cx',
             'caption': 'wakaba'}]
        },

    '_postform': {
        'action': '/post',
        'message': '',
        'inputs': []
        },

    # Parameters
    'indexThreads': 10,
    'maxThreads': 100,
    'tailCount': 5,
    'bumpLimit': 500,
    'theme': 'futaba',

    # Boundaries & restrictions
    'messageMaxSize': 16384,
    'allowedFields': ['parent', 'name', 'email', 'trip', 'sage',
                      'password', 'title', 'c', 'goto'],

    # Directories
    'themesRoot': ['.', 'themes'],
    'staticUrl' : '/static/',
    'staticRoot': ['.', 'static'],

    # Attaches
    'attaches': {
        'attachesMax': 3,
        'pathFs': [u'.', u'media', u'src'],
        'pathUrl': '/src/',
        'forceRename': False,
        'passUnknown': False,
        'requireUnique': True,
        'thumbs': {
            'pathFs': ['.', 'media', 'thumb'],
            'pathUrl': '/thumb/',
            'size': (200, 200),
            'fileNameFormat' : '%ss',
            'format': 'PNG',
            'useAA': True,
            }
        },

    # Captcha
    'captcha': {
        'url': 'captcha',
        'type': 'wakaba',
        'expires': 3,
        'fontName': './resources/cmunbi.otf',
        'rotateFactor': 11
        },

    # Hooks
    'hooks': [
        'hooks.std',
        'hooks.static',
        'captcha',
        'wakamark'
        ],

    # System
    'db': {
        'tailLength': 5, #liliumDNA.tailCount,
        'threadsLimit': 90, #liliumDNA.maxThreads,
        'maxThreads': 100,
        'bumpLimit': 40, #liliumDNA.bumpLimit,
        'harvesterDelta': 10,
        'dbname': 'default',
        'backend': 'memory'
        },

    # Localization
    'l10n': {
        'n': _n_en,
        'sz': _sz_c([['byte', 'bytes'],
                           ['KiB', 'KiB'],
                           ['MiB', 'MiB'],
                           ['GiB', 'GiB']],
                          1024,
                          _n_en)
        },
    }
