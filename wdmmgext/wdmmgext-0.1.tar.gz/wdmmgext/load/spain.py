# Script to import Spanish data
# Incomplete, first proof of concept

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

DATASET_NAME = u'spain'
SCHEME = u'spain'

def load_file(filename):
    '''
    Loads a file into a slice with name 'spain'.
    '''

    def describe_key(key, label, description=None):
        Entry.describe_key(key, label, context=DATASET_NAME, description=description)

    # Make a suitably configured Loader (this also creates the Dataset).
    spain_loader = loader.Loader(DATASET_NAME, "Spanish state budget",
        description = u'''
Spanish state budget.
''', currency=u'eur')

    # The keys used to classify Spanish spending 
    describe_key(u'from', "Paid by", description=u'''\
The entity that the money was paid from.''')
    describe_key(u'to', "Paid to", description=u'''\
The entity that the money was paid to.''')
    describe_key(u'time', "Time", description=u'''\
The accounting period in which the spending happened.''')
    describe_key(u'spain1', "Level 1", description=u'''\
Spanish spending code, level 1 (section).''')
    describe_key(u'spain2', "Level 2", description=u'''\
Spanish spending code, level 2 (entity).''')
    describe_key(u'spain3', "Level 3", description=u'''\
Spanish spending code, level 3 (programme).''')
    describe_key(u'spain4', "Level 4", description=u'''\
Spanish spending code, level 4 (concept).''')

    spain_govt = spain_loader.create_entity(name=u'Spain', 
        label = u'Spanish state budget',
        description = u'''Spanish state budget'''
        )
    society = spain_loader.create_entity(name=u'society', 
        label = u'Society (the General Public)',
        description = u'''A dummy entity to be the recipient of final government spending'''
        )

    # Open the Excel workbook
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(0)
    print "Number of rows: " + str(sheet.nrows)
    entry_id = 0
    # Process each row
    for row in range(0,sheet.nrows):
         entries = [{}, {}, {}, {}]
         entries[0]['code'] = ((sheet.cell(row,0).value.strip()))
         entries[0]['name_spanish'] = ((sheet.cell(row,1).value.strip()))
         entries[1]['code'] = ((sheet.cell(row,2).value.strip()))
         entries[1]['name_spanish'] = ((sheet.cell(row,3).value.strip()))
         entries[2]['code'] = ((sheet.cell(row,4).value.strip()))
         entries[2]['name_spanish'] = ((sheet.cell(row,5).value.strip()))
         entries[3]['code'] = ((sheet.cell(row,6).value.strip()))
         entries[3]['name_spanish'] = ((sheet.cell(row,7).value.strip()))
         print entries[3]['name_spanish']
         expenditure_2010 = util.to_float(unicode(sheet.cell(row,8).value))
         #names_english = [util.translate("es", "en", name.encode('utf-8')) for name in names_spanish]
         # Set up the Classifiers.
         code_ids = {}
         kapitel = loader.create_classifier(name, 'bund', label=label.strip(), html_link=html_link,
            pdf_link=pdf_link, einzelplan=context.get('einzelplan'))
         for level, entry in enumerate(entries):
             # entries[level]['name_english'] = util.translate("es", "en", \
             #                   entries[level]['name_spanish'].encode('utf-8'))
             code, title = entry['code'], entry['name_spanish']
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



	     def spain_by_code(code, cache={}, none_object='NONE'):
	         if not code in cache.keys():
	             c = Classifier.find_one({'taxonomy': 'spain', 'name': code})
	             cache[code] = c if c else none_object
	         return cache[code] if cache[code] is not none_object else None	
         # Create the Entries.
         if expenditure_2010:
             # entry_id += 1
             # e = spain_loader.create_entry(expenditure_2010, **{
             #     'name': DATASET_NAME + '-r' + str(entry_id),
             #     'from': spain_govt.to_ref_dict(),
             #     'to': society.to_ref_dict(),
             #     'time': "2009",
             #     'spain':  {"1": {'name': entries[0]['code'], 'ref': entries[0]['name_spanish']},
             #                "2": {'name': entries[1]['code'], 'ref': entries[1]['name_spanish']},
             #                "3": {'name': entries[2]['code'], 'ref': entries[2]['name_spanish']},
             #                "4": {'name': entries[3]['code'], 'ref': entries[3]['name_spanish']}}}
             # )
             ex = {
	             'name': DATASET_NAME + '-r' + str(entry_id),
	             'from': spain_govt.to_ref_dict(),
	             'to': society.to_ref_dict(),
	             'time': "2009",
                 }

             spain1 = cofog_by_code(entries[0]['code'])
             cra.classify_entry(ex, spain1, 'spain1')
             cra.classify_entry(ex, cofog2, 'spain2')
             cra.classify_entry(ex, cofog3, 'spain3')
             cra.classify_entry(ex, cofog3, 'spain4')
             e = cra.create_entry(exp, **ex)
def drop():
    '''
    Drops from the database all records associated with slice 'spain'.
    Not yet complete.
    '''
    # Delete only the keys we created ourselves.
    raise NotImplemented
        
def load():
    '''
    Downloads the Spanish data, and loads it into the database with slice name 'spain'
    Access via the Paste Script comment "paster load israel", see lib/cli.py 
    '''
    # Get the Spanish data package & unzip it
    #pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'spain-state-budget') 
    #pkg = datapkg.load_package(pkgspec)
    # Load the data
    filename = os.path.join(config['getdata_cache'], 'spain-state-budget/cofog-agg-budget.xls')
    load_file(filename)

