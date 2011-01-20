import os, sys, csv, re
from datetime import date
try: import json
except ImportError: import simplejson as json

import datapkg
from pylons import config
import wdmmg.model as model
from wdmmg.model import Dataset, Entry, Entity, Classifier
from wdmmg.lib import loader
import util

DATASET_NAME = u'cra'

def load_file(fileobj, cofog_mapper, commit_every=None):
    '''
    Loads a file from `fileobj` into a dataset with name 'cra'.
    The file should be CSV formatted, with the same structure as the 
    Country Regional Analysis data.
    
    fileobj - an open, readable file-like object.
    
    commit_every - if not None, call model.Session.commit() at the 
        specified frequency, expressed as a number of Entry records.
    '''
    # Semaphore to ensure COFOG is loaded first.
    assert Classifier.find_one({'taxonomy': 'cofog'}), 'COFOG must be loaded first'
    
    def describe_key(key, label, description=None):
        Entry.describe_key(key, label, context=DATASET_NAME, description=description)
    
    
    # Retrieve or create the required Keys.
    describe_key(u'from', 'Paid by', description=u'''\
The entity that the money was paid from.''')
    describe_key(u'to', "Paid to", description=u'''\
The entity that the money was paid to.''')
    describe_key(u'time', "Time", description=u'''\
The accounting period in which the spending happened.''')
    describe_key(u'pog', "Programme Object Group")
    describe_key(u'cap_or_cur', "Capital/Current", description=u'''\
Capital (one-off investment) or Current (on-going running costs)''')
    describe_key(u'cg_lg_or_pc', "CG, LG or PC", description=u"Central government, local government or public corporation")
    describe_key(u'region', 'Geographic Region', u'''\
Geographical (NUTS) area for which money was spent''')
    
    describe_key(u'cofog1', 'COFOG level 1', description=u'Classification Of Function Of Government, level 1')
    describe_key(u'cofog2', 'COFOG level 2', description=u'Classification Of Function Of Government, level 2')
    describe_key(u'cofog3', 'COFOG level 3', description=u'Classification Of Function Of Government, level 3')
    
    # Make a suitably configured Loader (this also creates the Dataset).
    cra = loader.Loader(DATASET_NAME, "Country Regional Analysis v2009", 
        description = u'''The Country Regional Analysis published by HM Treasury (2009 version).

Source data can be found in the CKAN data package at:
<http://ckan.net/package/ukgov-finances-cra/>''')
    
    society = cra.create_entity(name=u'society', 
        label = u'Society (the General Public)',
        description = u'''A dummy entity to be the recipient of final government spending'''
        )
        
    # Utility function for parsing numbers.
    def to_float(s):
        if not s: return 0.0
        return float(s.replace(',', ''))
    # Utility function for formatting tax years.
    def to_year(s):
        y = int(s[:4])
        return unicode(y)
    def to_region(region_name):
        return region_name.replace('_', ' ')
      
    def cofog_by_code(code, cache={}, none_object='NONE'):
        if not code in cache.keys():
            c = Classifier.find_one({'taxonomy': 'cofog', 'name': code})
            cache[code] = c if c else none_object
        return cache[code] if cache[code] is not none_object else None
    
    # For each line of the file...
    reader = csv.reader(fileobj)
    header = reader.next()
    year_col_start = 10
    years = [to_year(x) for x in header[year_col_start:]]
    entry_id = 0
    
    for row in reader:
        if not row[0]:
            # Skip blank row.
            continue
        # Parse row.
        row = [unicode(x.strip()) for x in row]
        dept_name = row[0]
        dept_label = row[1]
        dept = cra.create_entity(name=dept_name, label=dept_label)
        function = row[2]
        subfunction = row[3]
        pog_name = row[4]
        pog_label = row[5]
        pog = cra.create_classifier(name=pog_name, taxonomy='pog', label=pog_label)
        cap_or_cur = row[7]
        # TODO: seems to affect a lot so requires work ...
        # region = to_region(row[9])
        region = row[9]
        expenditures = [round(1e6*to_float(x)) for x in row[year_col_start:]]
        # Skip row whose expenditures are all zero. (Pointless?)
        if not [x for x in expenditures if x]:
            continue
        # Map 'function' and 'subfunction' to three levels of COFOG.
        cofog_parts = cofog_mapper.fix(function, subfunction)
        assert cofog_parts, 'COFOG code is missing for (%s, %s)' % (function, subfunction)
        assert len(cofog_parts) <= 3, 'COFOG code %r has too many levels' % cofog_parts
        cofog_parts = (cofog_parts + [None]*3)[:3]
        
        cofog1 = cofog_by_code(cofog_parts[0])
        cofog2 = cofog_by_code(cofog_parts[1])
        cofog3 = cofog_by_code(cofog_parts[2])
        
        # Make a Entry for each non-zero expenditure.
        for year, exp in zip(years, expenditures):
            if exp:
                entry_id += 1
                ex = {
                    'name': DATASET_NAME + '-r' + str(entry_id),
                    'from': dept.to_ref_dict(),
                    'to': society.to_ref_dict(),
                    'time': year,
                    'pog': pog.to_ref_dict(),
                    'cap_or_cur': cap_or_cur,
                    'region': region
                    }
                cra.classify_entry(ex, cofog1, 'cofog1')
                cra.classify_entry(ex, cofog2, 'cofog2')
                cra.classify_entry(ex, cofog3, 'cofog3')
                e = cra.create_entry(exp, **ex)
                
    # Finish off.
    cra.compute_aggregates()

def load_population(fileobj):
    '''
    Adds population data to the EnumerationValues that represent regions.
    The annotations are added in the form of KeyValues, using a Key named
    `key_name`.
    '''
    cra_rec = Dataset.find_one({'name': DATASET_NAME})
    assert cra_rec, "CRA must be loaded first"
    Entry.describe_key(u'population2006', 'Population as of 2006', context=DATASET_NAME, description=u'''\
This data comes from the "All ages" column of the document "Table 8 Mid-2006 Population Estimates: Selected age groups for local authorities in the United Kingdom; estimated resident population" which is available here:

    http://www.statistics.gov.uk/statbase/Expodata/Spreadsheets/D9664.xls
''')
    reader = csv.reader(fileobj)
    header = reader.next()
    for row in reader:
        if not row: continue
        code, population = row
        Entry.c.update(
            {'region': code, 'dataset.name': DATASET_NAME}, 
            {'$set': {'population2006': int(population)}}, 
            multi=True)

def drop():
    '''
    Drops from the database all records associated with dataset 'cra'.
    '''
    raise NotImplemented

def load():
    '''
    Downloads the CRA, and loads it into the database with dataset name 'cra'.

    Usually access via the Paste Script comment "paster load cra", see
    ../lib/cli.py .
    '''
    # Get the CRA data package.
    pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'ukgov-finances-cra')
    pkg = datapkg.load_package(pkgspec)
    # Make a CofogMapper.
    cofog_mapper = util.CofogMapper(json.load(pkg.stream('cofog_map.json')))
    # Load the data.
    # TODO: Move NUTS codes into a separate data package.
    # TODO: Move POG codes into a separate data package.
    load_file(pkg.stream('cra_2009_db.csv'), cofog_mapper, commit_every=1000)
    # Add population data.
    # TODO: Move population data into a separate data package. After NUTS.
    load_population(pkg.stream('nuts1_population_2006.csv'))

