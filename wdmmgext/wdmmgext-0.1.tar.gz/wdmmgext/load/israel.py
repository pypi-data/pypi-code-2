# Script to import Israeli data
# Incomplete, needs discussion with RGRP re appropriate keys

import os, sys, csv, re
from datetime import date
try: import json
except ImportError: import simplejson as json

import datapkg
from pylons import config

from wdmmg.model import Dataset, Entry, Entity, Classifier
import util
from wdmmg.lib import loader
import xlrd

DATASET_NAME = u'israel'
SCHEME = u'israel'

def load_file(filename):
    '''
    Loads a file into a slice with name 'israel'.
    - filename - name of the file.
    '''
    def describe_key(key, label, description=None):
        Entry.describe_key(key, label, context=DATASET_NAME, description=description)

    # Make a suitably configured Loader (this also creates the Dataset).
    israel_loader = loader.Loader(DATASET_NAME, "Israeli state budget",
        description = u'''
Israeli state budget.
''', currency=u'ils')

    # The keys used to classify Israeli spending 
    describe_key(u'from', "Paid by", description=u'''\
The entity that the money was paid from.''')
    describe_key(u'to', "Paid to", description=u'''\
The entity that the money was paid to.''')
    describe_key(u'time', "Time", description=u'''\
The accounting period in which the spending happened.''')
    describe_key(u'israel.1', "Level 1", description=u'''\
Israeli spending code, level 1 (section).''')
    describe_key(u'israel.2', "Level 2", description=u'''\
Israeli spending code, level 2 (entity).''')
    describe_key(u'israel.3', "Level 3", description=u'''\
Israeli spending code, level 3 (programme).''')
    describe_key(u'israel.4', "Level 4", description=u'''\
Israeli spending code, level 4 (concept).''')

    israel_govt = israel_loader.create_entity(name=u'Israel', 
        label = u'Israeli state budget',
        description = u'''Israeli state budget'''
        )
    society = israel_loader.create_entity(name=u'society', 
        label = u'Society (the General Public)',
        description = u'''A dummy entity to be the recipient of final government spending'''
        )

    # Open the Excel workbook
    book = xlrd.open_workbook(filename=filename)
    sheet = book.sheet_by_index(0)
    print "Number of rows: " + str(sheet.nrows)
    entry_id = 0

    for row in range(5,200): # sheet.nrows): # for each row after the header 
        entries = [{}, {}, {}, {}]
        entries[0]['code'] = ((sheet.cell(row,0).value.strip()))
        entries[0]['name_hebrew'] = ((sheet.cell(row,1).value.strip()))
        entries[0]['name_english'] = util.translate("iw", "en", entries[0]['name_hebrew'].encode('utf-8')) 
        entries[1]['code'] = ((sheet.cell(row,2).value.strip()))
        entries[1]['name_hebrew'] = ((sheet.cell(row,3).value.strip()))
        entries[1]['name_english'] = util.translate("iw", "en", entries[1]['name_hebrew'].encode('utf-8'))
        entries[2]['code'] = ((sheet.cell(row,4).value.strip()))
        entries[2]['name_hebrew'] = ((sheet.cell(row,5).value.strip()))
        entries[2]['name_english'] = util.translate("iw", "en", entries[2]['name_hebrew'].encode('utf-8'))
        entries[3]['code'] = ((sheet.cell(row,6).value.strip()))
        entries[3]['name_hebrew'] = ((sheet.cell(row,7).value.strip())) 
        entries[3]['name_english'] = util.translate("iw", "en", entries[3]['name_hebrew'].encode('utf-8'))
        #names_english = [util.translate("iw", "en", name.encode('utf-8')) for name in names_hebrew]
        print entries[3]['name_hebrew'], entries[3]['name_english']
        expenditure_2009 = util.to_float(unicode(sheet.cell(row,8).value))

        # Set up the Classifiers.
        code_ids = {}
        for level, entry in enumerate(entries):
            code, title = entry['code'], entry['name_hebrew']
            cf = Classifier(name=code, label=title, description=None, 
                            change_date=None, scheme=SCHEME)
            if level > 0:
                parent = entries[level-1]['code']
                cf.level = level
                if not parent in code_ids.keys():
                    code_ids[parent] = Classifier.c.insert({
                                                'name': parent, 
                                                'label': "(Parent)", 
                                                'scheme': scheme})
                cf.parent = code_ids[parent]
            code_ids[code] = Classifier.c.insert(cf)

        if expenditure_2009:
            entry_id += 1
            e = israel_loader.create_entry(expenditure_2009, **{
                'name': DATASET_NAME + '-r' + str(entry_id),
                'from': israel_govt.to_ref_dict(),
                'to': society.to_ref_dict(),
                'time': "2009",
                'israel': {"1": {'name': entries[0]['code'], 
                           'ref': entries[0]['name_hebrew'] + " = " \
                                 + entries[0]['name_hebrew']},
                           "2": {'name': entries[1]['code'], 
                           'ref': entries[1]['name_hebrew'] + " = " \
                                 + entries[1]['name_english']},
                           "3": {'name': entries[2]['code'],
                           'ref': entries[2]['name_hebrew'] + " = " \
                                 + entries[2]['name_english']},
                           "4": {'name': entries[3]['code'], 
                           'ref': entries[3]['name_hebrew'] + " = " \
                                 + entries[3]['name_english']}}}
            )

def drop():
    '''
    Drops from the database all records associated with slice 'israel'.
    Not yet complete.
    '''
    # Delete only the keys we created ourselves.
    raise NotImplemented
        
def load(filename=None):
    '''
    Downloads the Israel data, and loads it into the database with slice name 'israel'
    Access via the Paste Script comment "paster load israel", see lib/cli.py 
    '''
    print filename
    if not filename:
        filename = os.path.join(config['getdata_cache'], 'israel-state-budget/Israel state Budget 2009_2010 290710.xls')
	load_file(filename)