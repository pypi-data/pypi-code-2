import os, sys, csv, re
from datetime import date
try: import json
except ImportError: import simplejson as json

import datapkg
from swiss.tabular import gdocs
from pylons import config

import wdmmg.model as model
import util

dataset_name = u'gla'

def load_file(fileobj, period_mapper={}, commit_every=None):
    '''
    Loads a file from `fileobj` into a dataset with name 'gra'.
    
    fileobj - an open, readable file-like object.
    
    period_mapper - a dict from filename (e.g. u'january_2008.csv') to
        reporting period (e.g. u'2008-01').
    
    commit_every - if not None, call session.model.commit() at the 
        specified frequency.
    '''
    # Semaphore to prevent the data being loaded twice.
    assert not (model.Session.query(model.Dataset)
        .filter_by(name=dataset_name)
        ).first(), 'GLA already loaded'
    # Make a new dataset.
    dataset_ = model.Dataset(name=dataset_name, currency=u'gbp', notes=u'''
Greater London Authority spending data.

Source data package: <http://ckan.net/package/gla-spending/>
''')
    # The keys used to classify spending.
    key_from = util.get_or_create_key(name=u'from', notes=u'''\
The entity that the money was paid from.''')
    key_to = util.get_or_create_key(u'to', u'''\
The account that the money was paid to.''')
    key_time = util.get_or_create_key(name=u'time', notes=u'''\
The accounting period in which the spending happened.''')
    key_docNumber = util.get_or_create_key(u'docNumber', u'''\
The invoice or other document number.''')
    key_filename = util.get_or_create_key(u'filename', u'''\
The name of the data file in which this spending appears.''')
    key_rowNumber = util.get_or_create_key(u'rowNumber', u'''\
The row number of this spending within its data file.''')
    # Utility function for creating EnumerationValues.
    def get_or_create_value(key, code, name=None, notes=u'', index={}):
        if not name:
            name = code
        if (key.name, code) not in index:
            index[key.name, code] = model.EnumerationValue(
                key=key, code=code, name=name or code, notes=notes)
            model.Session.add(index[key.name, code])
        return index[key.name, code]
    gla = get_or_create_value(key_from, 'GLA', 'Greater London Authority')
    gla_code = gla.code
    # Utility function for parsing numbers.
    def to_float(s):
        if not s: return 0.0
        return float(s.replace(',', ''))
    # For each line of the file...
    reader = csv.reader(fileobj)
    header = reader.next()
#    print header
    for row_index, row in enumerate(reader):
        # Progress output.
        if commit_every and row_index%commit_every == 0:
            print "Committing before processing row %d" % row_index
            model.Session.commit()
        # Parse row.
        if not row[0]:
            # Skip blank row.
            continue
#        print row
        row = [unicode(x.strip()) for x in row]
        amount = to_float(row[0])
        date = row[1] # Often missing.
        description = row[2]
        docNumber = row[3] # Often missing.
        docType = row[4] # Ignore.
        link = row[5]
        rowNumber = row[6]
        supplier = row[7]
        # Computed values.
        filename = link.split('/')[-1]
        period = period_mapper.get(filename, None)
        # Make the Entry and its ClassificationItems.
        txn = model.Entry(dataset_=dataset_, amount=amount)
        txn.notes = description
        items = {
            key_from: gla_code,
            key_to: supplier,
            key_filename: filename,
            key_rowNumber: rowNumber
        }
        if period is not None:
            items[key_time] = period
        if date:
            items[key_time] = date
        if docNumber:
            items[key_docNumber] = docNumber
        for key, code in items.items():
            model.Session.add(model.ClassificationItem(
                entry=txn,
                value=get_or_create_value(key, code)
            ))
    if commit_every:
        model.Session.commit()


def drop():
    '''
    Drops from the database all records associated with dataset 'cra'.
    '''
    # TODO.
    raise NotImplemented


def load_period_mapper(spreadsheet_key='0AijCXAu1IV6YdDFyYW1VTHJvYXlmQThHQURrQ3VXY1E'):
    '''
    Constructs a dict that maps GLA data file name to reporting period. The
    data is loaded from a Google spreadsheet.
    '''
    ans = {}
    for row in gdocs.GDocsReaderTextDb(spreadsheet_key,
        config['gdocs_username'], config['gdocs_password']
    ).read().to_list()[1:]:
        filename, period, has_dates, has_docNumbers = row
        ans[unicode(filename)] = unicode(period)
    return ans


def load():
    '''
    Downloads the GLA, and loads it into the database with dataset name 'gla'.
    Also downloads the mapping from GLA filename to reporting period (month)
    from a Google Documents spreadsheet.
    '''
    # Get the GLA data package.
    pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'gla-spending')
    pkg = datapkg.load_package(pkgspec)
    # Load the data.
    load_file(
        pkg.stream('greater-london-assembly-expenditure'),
        load_period_mapper(),
        commit_every=1000
    )
    model.Session.commit()
    model.Session.remove()

