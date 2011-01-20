# Script to import Ordnance Survey spending data
import datapkg
from datetime import date
import os, sys, csv, re
from pylons import config
import util
import wdmmg.model as model
from wdmmg.lib import loader

slice_name = u'ordnance'
names_root = util.Node('')

def load_file(filename, commit_every=None):
    '''
    Loads a file into a slice with name 'ordnance'.
    - filename - name of file to load  
    - commit_every - if not None, call session.model.commit() at the 
        specified frequency.
    '''
    # Semaphore to prevent the data being loaded twice
    assert not (model.Session.query(model.Slice)
        .filter_by(name=slice_name)
        ).first(), 'ordnance already loaded'
    # Make a new slice for ordnance
    slice_ = model.Slice(name=slice_name, currency=u'gbp', notes=u'''
Ordnance Survey spending data 2009/10.

Source: DCLG data release: http://www.communities.gov.uk/publications/corporate/spendingdata0910
''')

    # The keys used to classify Ordnance Survey spending 
    key_from = util.get_or_create_key(name=u'from', notes=u'''\
The entity that the money was paid from.''')
    key_to = util.get_or_create_key(name=u'to', notes=u'''\
The entity that the money was paid to.''')
    key_time = util.get_or_create_key(name=u'time', notes=u'''\
The accounting period in which the spending happened.''')
    pspes1 = util.get_or_create_key(name=u'pspes1', notes=u'''\
PSPES classification, level 1''')
    pspes2 = util.get_or_create_key(name=u'pspes2', notes=u'''\
PSPES classification, level 2''')
    pspes3 = util.get_or_create_key(name=u'pspes3', notes=u'''\
GL description''')

    # Add parent keys
    key_parent = model.Session.query(model.Key).filter_by(name=u'parent').first()
    if not key_parent:
        key_parent = model.Key(name=u'parent', notes=u'Means "is part of".')
        model.Session.add(key_parent)
    pspes2.keyvalues[key_parent] = pspes1.name
    pspes3.keyvalues[key_parent] = pspes2.name
    model.Session.commit()

    # All spending is from the Ordnance Survey
    ordnance = util.get_or_create_value(key_from, u'ordnance', u'Ordnance Survey spending data')
    ordnance_code = ordnance.code

    # Open the CSV workbook
    reader = csv.reader(open(filename, "rU"))
    header = reader.next()

    for row_index, row in enumerate(reader):
         if commit_every and row_index%commit_every == 0:
             print "Committing before processing row %d" % row_index
             model.Session.commit()
         row = [unicode(x.decode("mac_roman").strip()) for x in row]
         names = []
         supplier = row[0]
         date = row[1]
         expenditure = util.to_float(row[2])
         pspes1_item = row[3]
         names.append(pspes1_item)
         pspes2_item = row[4]
         pspes3_item = row[5]
         if pspes2_item!='': 
             names.append(pspes2_item)
         if pspes3_item!='': 
             names.append(pspes3_item)
         #print names
         util.addnodes(names, names_root)

         # Make the Transaction and its ClassificationItems
         txn = model.Transaction(slice_=slice_, amount=expenditure)
         #print 'making transaction with ' + str(expenditure)
         items = {
             key_from: ordnance_code,
             key_to: supplier,
             key_time: '2009-2010'
         }
         for key, code in items.items():
             model.Session.add(model.ClassificationItem(
                 transaction=txn,
                 value=util.get_or_create_value(key, code)
              ))
         model.Session.add(model.ClassificationItem( # add PSPES1
             transaction=txn,
             value=util.get_or_create_value(pspes1, util.get_code(pspes1_item), pspes1_item)
          ))
         if pspes2_item!='':# add PSPES2
	         model.Session.add(model.ClassificationItem(
	             transaction=txn,
	             value=util.get_or_create_value(pspes2, util.get_code(pspes2_item, pspes1_item), pspes2_item, parent=pspes1_item)
	          ))
         if pspes3_item!='':# add GL description
	         model.Session.add(model.ClassificationItem(
	             transaction=txn,
	             value=util.get_or_create_value(pspes3, util.get_code(pspes3_item, pspes2_item), pspes3_item, parent=pspes2_item)
	          ))
    if commit_every:
        model.Session.commit()

def drop():
    '''
    Drops from the database all records associated with slice 'ordnance'.
    '''
    raise NotImplemented
        
def load():
    '''
    Downloads the OS data, and loads it into the database with slice name 'ordnance'.
    Access via the Paste Script comment "paster load ordnance"
    '''
    # Get the OS data package & unzip it
    #pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'ordnance')
    #pkg = datapkg.load_package(pkgspec)
    filepath = os.path.join(config['getdata_cache'], 'ordnance/ordnance_survey_expenditure.csv')
    load_file(filepath, commit_every=1000)
    model.Session.commit()
    model.Session.remove()
