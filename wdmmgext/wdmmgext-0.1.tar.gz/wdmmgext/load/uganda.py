# Script to import Uganda data

import os, sys, re
import xlrd
from datetime import date
try: import json
except ImportError: import simplejson as json

import datapkg
from pylons import config

from swiss.tabular import gdocs
import util
from wdmmg.model import Dataset, Entry, Entity, Classifier, KeyMeta
from wdmmg.lib import loader

years = [u'2003-2004', u'2004-2005', u'2005-2006', u'2006-2007']
DATASET_NAME=u'uganda'

def load(is_test=False, *args): 
    '''
    Loads the Uganda GDocs files into a dataset.
    '''
    def describe_key(key, label, description=None):
        Entry.describe_key(key, label, context=DATASET_NAME, description=description)

    # Make a suitably configured Loader (this also creates the Dataset).
    uganda_loader = loader.Loader(DATASET_NAME, "Ugandan government spending 2003-2007",
        description = u'''Ugandan government and donor spending from 2003-2007, 
supplied by <a href="http://www.publishwhatyoufund.org/">PublishWhatYouFund</a>.

Source data can be found in the CKAN data package at:
<a href="http://www.ckan.net/package/ugandabudget">
http://www.ckan.net/package/ugandabudget</a>''', currency=u'ugx')

    # Retrieve or create the keys used to classify Ugandan spending.
    describe_key(u'from', 'Paid by', description=u'''\
The entity that the money was paid from.''')
    describe_key(u'to', "Paid to", description=u'''\
The entity that the money was paid to.''')
    describe_key(u'time', "Time", description=u'''\
The accounting period in which the spending happened.''')
    describe_key(u'name', "Name", description=u'''\
Internal dataset name''')
    describe_key(u'cap_or_cur', "Capital or current", description=u'''\
Capital (one-off investment) or Current (on-going running costs)''')
    describe_key('wage_or_nonwage', "Wage or non-wage", description=u'''\
Wage-related current costs, or non-wage-related current costs.''')
    describe_key(u'uganda_id', "Internal ID", description=u'''\
Internal spending item ID.''')
    describe_key(u'gou_vote', "GoU vote", description=u'''\
Government of Uganda vote.''')
    describe_key(u'project_code', "Project code", description=u'''\
Project code (more info TBA).''')
    describe_key(u'project_name', "Project name", description=u'''\
Project name (more info TBA).''')
    describe_key(u'mtef_sector', "MTEF sector", description=u'''\
MTEF sector (more info TBA).''')
    describe_key(u'mtef_reference', "MTEF reference", description=u'''\
MTEF reference (more info TBA).''')
    describe_key(u'paf', "PAF", description=u'''\
PAF (more info TBA).''')
    describe_key(u'swg', "SWG", description=u'''\
SWG (more info TBA).''')
    describe_key(u'sector_objective', "Sector objective", description=u'''\
Sector objective (more info TBA).''')
    describe_key(u'a_peap1', 'PEAP level 1 (Pillar)', description=u'''\
PEAP classification level 1''')
    describe_key(u'a_peap2', 'PEAP level 2 (Objective)', description=u'''\
PEAP classification level 2''')
    describe_key(u'a_peap3', 'PEAP level 3 (Area)', description=u'''\
PEAP classification level 3''')

    # Get header indices for each of the columns we care about. 
    def get_header_indices(header):
        try:
            id_idx = util.find_idx(header, 'id',required=False)
            vote_idx = util.find_idx(header, 'gouvote',required=False)
            vote_name_idx = util.find_idx(header, 'votename',required=False)
            proj_code_idx = util.find_idx(header, 'projectcode',required=False)
            proj_name_idx = util.find_idx(header, 'projectname',required=False)
            dp_idx = util.find_idx(header, 'dp',required=False)
            gou_idx = util.find_idx(header, 'gou',required=False)
            mtef_sector_idx = util.find_idx(header, 'mtefsector',required=False)
            mtef_ref_idx = util.find_idx(header, 'mtefreference',required=False)
            paf_idx = util.find_idx(header, 'paf',required=False)
            swg_idx = util.find_idx(header, 'swg',required=False)
            so_idx = util.find_idx(header, 'sectorobjective',required=False)
            peap1_idx = util.find_idx(header, 'peappillar',required=False)
            peap2_idx = util.find_idx(header, 'peapobjective',required=False)
            peap3_idx = util.find_idx(header, 'peaparea',required=False)
            amount_03_index = util.find_idx(header, 'outturn2003-2004ugxbn',required=False)
            amount_04_index = util.find_idx(header, 'outturn2004-2005ugxbn',required=False)
            amount_05_index = util.find_idx(header, 'outturn2005-2006ugxbn',required=False)
            amount_06_index = util.find_idx(header, 'budget2006-2007ugxbn',required=False)
        except Exception, e:
            print 'ERROR: ', e
            return 0
        header_indices = {'id_idx': id_idx, 'vote_idx': vote_idx, \
             'vote_name_idx': vote_name_idx, 'proj_code_idx': proj_code_idx, \
             'proj_name_idx': proj_name_idx, 'dp_idx': dp_idx, \
             'gou_idx': gou_idx, 'mtef_sector_idx': mtef_sector_idx, \
             'mtef_ref_idx': mtef_ref_idx, 'paf_idx': paf_idx, \
             'swg_idx': swg_idx, 'so_idx': so_idx, 'peap1_idx': peap1_idx, \
             'peap2_idx': peap2_idx, 'peap3_idx': peap3_idx, \
             'amount_03_index': amount_03_index, 'amount_04_index': \
             amount_04_index, 'amount_05_index': amount_05_index, \
             'amount_06_index': amount_06_index}
        return header_indices

    # Make entries for each row.
    def process_row(row, header_indices, who_from, cap_or_cur, wage_or_nonwage,entry_id):
        print row
        id_value = row[header_indices['id_idx']]
        funders = {"Donors":"01","Government":"02","Government (including Budget Support)":"03"}
        funder = uganda_loader.create_entity(name=funders[who_from], label=who_from)
        # GoU vote. Create this as an Entity. (Also used as value for 'to'.)
        gou_vote_value = row[header_indices['vote_idx']]
        gou_vote_name_value = row[header_indices['vote_name_idx']]
        gou_vote = uganda_loader.create_entity(name=gou_vote_value, label=gou_vote_name_value)
        # Project details. Create this as an Entity.
        project_code_value = row[header_indices['proj_code_idx']]
        project_name_value = row[header_indices['proj_name_idx']]
        project = uganda_loader.create_entity(name=project_code_value, label=project_name_value)
        # MTEF/SWF/Sector. Create as Entities.
        mtef_sector_value = row[header_indices['mtef_sector_idx']]
        mtef_sector = uganda_loader.create_entity(name=mtef_sector_value, label=mtef_sector_value)
        mtef_reference_value = row[header_indices['mtef_ref_idx']]
        mtef_reference = uganda_loader.create_entity(name=mtef_reference_value, label=mtef_reference_value)
        swg_value = row[header_indices['swg_idx']]
        swg = uganda_loader.create_entity(name=swg_value, label=swg_value)
        sector_objective_value = row[header_indices['so_idx']]
        sector_objective = uganda_loader.create_entity(name=sector_objective_value, label=sector_objective_value)
         # Clean up PEAP codes on the fly
        def peap(row_value, parent_code=None):
            row_values = row_value.split(" ")
            row_code = row_values[0]
            # Deal with non-numeric values - assign codes of 0.
            if not row_code[0].isdigit():
                if parent_code is not None: 
                    row_code = parent_code + ".0"
                else:
                    row_code = "0"
            else:
                if row_code[-1]==".":
                    row_code = row_code[:-1]
                row_value = " ".join(row_values[1:])
            return unicode(row_value), unicode(row_code)
        peap1_value, peap1_code = peap(row[header_indices['peap1_idx']])
        peap2_value, peap2_code = peap(row[header_indices['peap2_idx']], peap1_code)
        peap3_value, peap3_code = peap(row[header_indices['peap3_idx']], peap2_code)
        amounts = [row[header_indices['amount_03_index']], \
                   row[header_indices['amount_04_index']], \
                   row[header_indices['amount_05_index']], \
                   row[header_indices['amount_06_index']]]
        expenditures = [round(1e9*util.to_float(x)) for x in amounts]
        # Skip row whose expenditures are all zero. 
        if not [x for x in expenditures if x]:
            return 1
        for year, exp in zip(years, expenditures):
            if exp:
                entry_id += 1
                print 'Creating an entry with amount %s and ID %s' % (exp, entry_id)
                e = uganda_loader.create_entry(exp, **{
                    'name': DATASET_NAME + '-r' + str(entry_id),
                    'from': funder.to_ref_dict(), 
                    'to': gou_vote.to_ref_dict(),
                    'time': year,
                    'cap_or_cur': cap_or_cur,
                    'wage_or_nonwage': wage_or_nonwage,
                    'uganda_id': id_value,
                    'gou_vote': gou_vote.to_ref_dict(),
                    'project': project.to_ref_dict(),
                    'mtef_sector': mtef_sector.to_ref_dict(),
                    'mtef_reference': mtef_reference.to_ref_dict(),
                    'swg': swg.to_ref_dict(),
                    'sector_objective': sector_objective.to_ref_dict(),
                    'peap':   {"1": {'name': peap1_value, 'ref': peap1_code},
                               "2": {'name': peap2_value, 'ref': peap2_code},
                               "3": {'name': peap3_value, 'ref': peap3_code}}}
                )
    
    def load_file(who_from, cap_or_cur, wage_or_nonwage, sheet_name=None, filename=None):
        # Open the file: first get header indices, then process each row.
        if filename: 
            book = xlrd.open_workbook(filename=filename)
            sheet = book.sheet_by_index(0)
            # Get header and indices.
            header = [str(sheet.cell(0,col).value) \
                     for col in range(0,sheet.ncols)]
            print header
            header_indices = get_header_indices(header)
            # Process each row. 
            entry_id=0
            for row_num in range(2,sheet.nrows-1):  
                entry_id += 1
                row = [str(sheet.cell(row_num,col).value) \
                      for col in range(0,sheet.ncols)]
                row = [unicode(x.strip()) if x is not None else u'' for x in row]
                process_row(row, header_indices, who_from, cap_or_cur, wage_or_nonwage,entry_id)
        else: 
            # Get header and indices.
            all_rows = gdocs.GDocsReaderTextDb('t5yiq3m1DbXC3pvB29GCwfg',
                config['gdocs_username'], config['gdocs_password']
            ).read(sheet_name=sheet_name).to_list()
            header = all_rows[0]
            print header
            header_indices = get_header_indices(header)
            # Process each row.
            entry_id=0
            for row in all_rows[2:]:
                entry_id += 1
                row = [unicode(x.strip()) if x is not None else u'' for x in row]
                process_row(row, header_indices, who_from, cap_or_cur, wage_or_nonwage,entry_id)

    load_file(who_from=u'Donors', cap_or_cur=u'Capital',\
               wage_or_nonwage=u'N/A (capital spending)', sheet_name='Donor Development')
    if not is_test:
        load_file(who_from=u'Government',cap_or_cur=u'Capital', \
                   wage_or_nonwage=u'N/A (capital spending)', sheet_name='GoU Development')
        load_file(who_from=u'Government (including Budget Support)', \
                  cap_or_cur=u'Current', wage_or_nonwage=u'Wage', sheet_name='GoU Development')
        load_file(who_from=u'Government (including Budget Support)',\
                   cap_or_cur=u'Current',wage_or_nonwage=u'Non-wage', sheet_name='GoU Development')
