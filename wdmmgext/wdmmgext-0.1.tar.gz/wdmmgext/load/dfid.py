# Script to import DFID data
# Uses Node class in util to create codes
import datapkg
from datetime import date
import os, sys, csv, re
from pylons import config

import util
from wdmmg.model import Dataset, Entry, Entity, Classifier
from wdmmg.lib import loader
import xlrd

DATASET_NAME = u'dfid'
SCHEME = u'dfid'
names_root = util.Node('')

def load_file(filename):
    '''
    Loads a file into a dataset with name 'dfid'.
    - filename - name of file to load  
    '''

    def describe_key(key, label, description=None):
        Entry.describe_key(key, label, context=DATASET_NAME, description=description)

    # Make a suitably configured Loader (this also creates the Dataset).
    dfid_loader = loader.Loader(DATASET_NAME, "DfID spending data",
        description = u'''
DFID spending data.

Source: DfID.
''', currency=u'gbp')

    # The keys used to classify DfID spending 
    describe_key(u'from', "Paid by", description=u'''\
The entity that the money was paid from.''')
    describe_key(u'to', "Paid to", description=u'''\
The entity that the money was paid to.''')
    describe_key(u'time', "Time", description=u'''\
The accounting period in which the spending happened.''')
    describe_key(u'dfid_continent_or_agency', "Continent or agency", description=u'''\
Continent or international agency in which DfID funds were spent''')
    describe_key(u'dfid_continent_or_agency_sub', "Area or sub-agency", description=u'''\
Area or international sub-agency in which DfID funds were spent''')
    describe_key(u'dfid_country_or_subagency', "Country or sub-agency", description=u'''\
Country in which DfID funds were spent''')
    describe_key('dfid_sector', "Sector", description=u'''\
Sector in which DfID funds were spent''')

    dfid_dept = dfid_loader.create_entity(name=u'DfID', 
        label = u'Department for International Development',
        description = u'''Department for International Development'''
        )
    society = dfid_loader.create_entity(name=u'society', 
        label = u'Society (the General Public)',
        description = u'''A dummy entity to be the recipient of final government spending'''
        )

    # Utility function for formatting years (borrowed from CRA script)
    def to_year(s):
        y = int(s[:4])
        return u'%4d-%4d' % (y, y+1)

    # Open the Excel workbook
    book = xlrd.open_workbook(filename)
    sheet = book.sheet_by_index(1)

    unique_names = []
    entry_id = 0
    for row in range(2,sheet.nrows): 
         dfid_continent_or_agency_code = unicode(sheet.cell(row,0).value.strip())
         names = []
         names.append(dfid_continent_or_agency_code)
         dfid_continent_or_agency_sub_code = unicode(sheet.cell(row,1).value.strip())
         if dfid_continent_or_agency_sub_code:
             names.append(dfid_continent_or_agency_sub_code)
         dfid_country_or_subagency_code = unicode(sheet.cell(row,2).value.strip())
         if dfid_country_or_subagency_code:
             names.append(dfid_country_or_subagency_code)
        # We need each key to have a unique code. Use util.addnodes to achieve this.
         util.addnodes(names, names_root)
         year = to_year(unicode(sheet.cell(row,3).value.strip()))
         expenditure = util.to_float(unicode(sheet.cell(row,5).value))*1000
         entries = [{}, {}, {}]
         entries[0] = {'name': dfid_continent_or_agency_code, \
                     'code': util.get_code(dfid_continent_or_agency_code)}
         entries[1] = {'name': dfid_continent_or_agency_sub_code, \
                     'code': util.get_code(dfid_continent_or_agency_sub_code, \
                             dfid_continent_or_agency_code)}
         entries[2] = {'name': dfid_country_or_subagency_code, \
                    'code': util.get_code(dfid_country_or_subagency_code, \
                            dfid_continent_or_agency_sub_code)}
         # Set up the Classifiers.
         code_ids = {}
         for level, entry in enumerate(entries):
             code, title = entry['code'], entry['name']
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

         if expenditure:
             entry_id += 1
             e = dfid_loader.create_entry(expenditure, **{
                 'name': DATASET_NAME + '-r' + str(entry_id),
                 'from': dfid_dept.to_ref_dict(),
                 'to': society.to_ref_dict(),
                 'time': year,
                 'dfid':  {"1": {'name': entries[0]['code'], 'ref': entries[0]['name']},
                           "2": {'name': entries[1]['code'], 'ref': entries[1]['name']},
                           "3": {'name': entries[2]['code'], 'ref': entries[2]['name']}}}
             )

def drop():
    '''
    Drops from the database all records associated with dataset 'dfid'.
    '''
    # Check keys aren't being used elsewhere.
    raise NotImplemented
        
def load(filepath=None):
    '''
    Downloads the DFID data, and loads it into the database with dataset name 'dfid'.
    Access via the Paste Script comment "paster load dfid", see lib/cli.py 
    '''
    # Get the DFID data package & unzip it
    if not filepath: 
        filepath = os.path.join(config['getdata_cache'], 'dfid/DFIDv3.xls')
    load_file(filepath)

