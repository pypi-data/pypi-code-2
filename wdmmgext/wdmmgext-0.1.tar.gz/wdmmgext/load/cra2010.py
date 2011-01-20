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

DATASET_NAME = u'cra2010'

def load_file(filename, cofog_mapper, commit_every=None):
    '''
    Loads a file from `fileobj` into a dataset with name 'cra2010'.
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
    
    # Make a suitably configured Loader (this also creates the Dataset).
    cra = loader.Loader(DATASET_NAME, "Country Regional Analysis v2010",
        description = u'''The Country Regional Analysis published by HM Treasury (2010 version).

Source data can be found in the CKAN data package at:
<http://ckan.net/package/ukgov-finances-cra/>''')

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
    
    # And, we create HMT keys.
    describe_key(u'hmt1', "HMT Function", description=u'''\
HMT Functional Classification (Treasury equivalent of COFOG1)''')
    describe_key(u'hmt2', "HMT Sub-Function", description=u'''\
HMT Sub-Functional Classification (Treasury equivalent of COFOG2)''')
    
    describe_key(u'cofog1', 'COFOG level 1', description=u'Classification Of Function Of Government, level 1')
    describe_key(u'cofog2', 'COFOG level 2', description=u'Classification Of Function Of Government, level 2')
    describe_key(u'cofog3', 'COFOG level 3', description=u'Classification Of Function Of Government, level 3')
    
    # Do we need big_society as well? 
    society = cra.create_entity(name=u'society', 
        label = u'Society (the General Public)',
        description = u'''A dummy entity to be the recipient of final government spending'''
        )
    
    # Utility function for parsing numbers.
    def to_float(s):
        #print "To float: " + str(s)
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
            
    
    reader = csv.reader(open(filename, 'rU'), dialect='excel')
    header = reader.next()
    year_col_start = 12
    years = [to_year(x) for x in header[year_col_start:-1]] # we don't load 2010-11, due to lack of LA data
    print years
    entry_id = 0
    for counter,row in enumerate(reader):
        if not row[0]:
            continue
        # Parse row.
        row = [unicode(x.strip()) for x in row]
        dept_name = row[0]
        dept_label = row[1]
        dept = cra.create_entity(name=dept_name, label=dept_label)
        
        function = row[3].split(" - ")[-1].strip()
        #print function
        subfunction_strings = row[5].split(" - ")
        #print subfunction_strings
        #print subfunction_strings[0][:4]
        # deal with unusual rows to match the COFOG mapper
        if subfunction_strings[0][:4] == "10.4":
            subfunction = "of which: family benefits, income support and tax credits (family and children)"
        elif subfunction_strings[0][:4] == "10.7":
            subfunction = "of which: family benefits, income support and tax credits (social exclusion n.e.c.)"
        else:  
            subfunction = subfunction_strings[-1].strip()
            subfunction = subfunction.split("7. ")[-1]
        #hmt1 = row[3]
        #hmt2 = row[5]
        pog_name = row[6]
        pog_label = row[7]
        pog = cra.create_classifier(name=pog_name, taxonomy='pog', label=pog_label)
        cap_or_cur = row[9]
        cg_lg_or_pc = row[10]
        # TODO: seems to affect a lot so requires work ...
        # region = to_region(row[9])
        region = row[11]
        expenditures = [round(1e6*to_float(x)) for x in row[year_col_start:]]
        #print expenditures
        # Skip row whose expenditures are all zero. (Pointless?)
        if not [x for x in expenditures if x]:
            continue
        # Map 'function' and 'subfunction' to three levels of COFOG.
        cofog_parts = cofog_mapper.fix(function, subfunction)
        assert cofog_parts, 'COFOG code is missing for (%s, %s)' % (function, subfunction)
        assert len(cofog_parts) <= 3, 'COFOG code %r has too many levels' % cofog_parts
        cofog_parts = (cofog_parts + [None]*3)[:3]
        # Make a Entry for each non-zero expenditure.
        
        cofog1 = cofog_by_code(cofog_parts[0])
        cofog2 = cofog_by_code(cofog_parts[1])
        cofog3 = cofog_by_code(cofog_parts[2])
        
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
                    'cg_lg_or_pc': cg_lg_or_pc,
                    'region': region
                    }
                cra.classify_entry(ex, cofog1, 'cofog1')
                cra.classify_entry(ex, cofog2, 'cofog2')
                cra.classify_entry(ex, cofog3, 'cofog3')
                e = cra.create_entry(exp, **ex)
                #print e.id
    # Finish off.
    cra.compute_aggregates()

def load_population(fileobj):
    '''
    Adds population data to the EnumerationValues that represent regions.
    The annotations are added in the form of KeyValues, using a Key named
    `key_name`.
    '''
    cra_rec = Dataset.find_one({'name': DATASET_NAME})
    assert cra_rec, "CRA2010 must be loaded first"
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
    # Delete only the keys we created ourselves.
    # TODO: Move as many as possible of these into separate data packages.
    raise NotImplemented

def load():
    '''
    Downloads the CRA, and loads it into the database with dataset name 'cra'.

    Usually access via the Paste Script comment "paster load cra2010", see
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
    filename = os.path.join(config['getdata_cache'] + '/ukgov-finances-cra/cra_2010.csv')
    load_file(filename, cofog_mapper, commit_every=1000)
    # Add population data.
    # TODO: Move population data into a separate data package. After NUTS.
    load_population(pkg.stream('nuts1_population_2006.csv'))
    

