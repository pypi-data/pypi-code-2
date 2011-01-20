from datetime import date
from zipfile import ZipFile
from StringIO import StringIO
import os, csv

import datapkg
from swiss.tabular import gdocs
from pylons import config

from wdmmg import model
from wdmmg.model import Classifier, KeyMeta, Entry
import util

TAXONOMY = 'cofog'


def drop():
    '''
    Drops Keys 'cofog1', 'cofog2' and 'cofog3' and all associated
    EnumerationValues and KeyValues.
    '''
    
    Classifier.c.remove({'taxonomy': TAXONOMY})
    Explanation.c.remove({'collection': Classifier.collection_name, 'context': TAXONOMY})
    
def load():
    '''
    Downloads the COFOG list, and loads it into the database with key names
    'cofog1', 'cofog2' and 'cofog3'.

    Typically this is invoked from a paster shell:
      $ paster shell
      >>> from wdmmg.getdata import cofog
      >>> cofog.load()

    The cofog datapkg must be in place.
    '''
    # Get the COFOG data package.
    pkgspec = 'file://%s' % os.path.join(config['getdata_cache'], 'cofog')
    pkg = datapkg.load_package(pkgspec)
    fileobj = pkg.stream('cofog.csv')
    load_file(fileobj)
    dejargonise()
    promote_notes()

def dejargonise():
    '''
    Downloads alternative names for the COFOG codes, chosen specially for WDMMG,
    and replaces the names in the database. The original names are backed up.
    '''
    # Create the 'official_name' Key if necessary.
    Classifier.describe_key(u'official_name', 'Official Name', context='cofog', description=u'''\
The official names of things, as defined by the relevant standards body. We \
do not always use the official names for things, because they are sometimes \
difficult to understand. When we substitute an alternative name, we record \
the official name using this key.''')
    
    # Loop through the rows of the Google spreadsheet where the data is maintained.
    for row in gdocs.GDocsReaderTextDb(
        'tQSJ9dxTh8AKl-ON4Qqja8Q', # Google spreadsheet key.
        config['gdocs_username'],
        config['gdocs_password']
    ).read().to_list()[2:]:
#        print row
        code, official_name, alternative_name, notes = row
        concept = Classifier.find_one({'taxonomy': TAXONOMY, 'name': code})
        assert concept, 'Spreadsheet contains an unknown COFOG code: %r' % row
        if alternative_name:
            concept['official_label'] = concept.label
            concept.label = unicode(alternative_name)
            print "Setting name of %r to %r" % (code, alternative_name)
            Classifier.c.update({'_id': concept.id}, concept)

def promote_notes():
    '''
    Where a level 2 COFOG code has exactly one level 3 sub-code, there is
    often no detailed description for the level 2 code. This method will
    supply the missing description by copying it from the level 3 sub-code.
    '''
    for item in Classifier.find({'taxonomy': TAXONOMY, 'level': 2}):
        if item.description:
            continue
        children = Classifier.find({'taxonomy': TAXONOMY, 'level': 3, 'parent': item.id})
        if children.count() != 1: 
            continue
        child = children.next()
        if child.description:
            print "Copying notes from %s to %s" % (child.name, item.name)
            print "Old notes = ", item.description.encode('utf-8')
            item.description = child.description
            print "New notes = ", item.description.encode('utf-8')
            Classifier.c.update({'_id': child.id}, child)

def load_file(fileobj):
    '''
    Loads the specified COFOG-like file into the database with key names
    'cofog1', 'cofog2' and 'cofog3'.
    '''
    Entry.describe_key(key=u'cofog1', label=u'Classification Of Function Of Government')
    
    code_ids = {}
    
    reader = csv.reader(fileobj)
    header = reader.next() # Code, Title, Details, Change date
    
    for row_index, cells in enumerate(reader):
        code, title, details, change_date = [unicode(x, 'UTF-8') for x in cells]
        concept = Classifier(name=code, label=title, description=details, change_date=change_date, 
                          taxonomy=TAXONOMY)
        # Create the enumeration values.
        #print '%r, %r' % (code, title)
        parts = code.split('.')
        parents = [u'.'.join(parts[:i+1]) for i, _ in enumerate(parts)]
        #print parents
        if len(parents)==1:
            #print 'Creating level 1 code', parents[0]
            concept.level = 1
        elif len(parents)==2:
            #print 'Creating level 2 code', parents[1]
            concept.parent = code_ids[parents[0]]
            concept.level = 2
        elif len(parents)==3:
            #print 'Creating level 3 code', parents[2]
            concept.parent = code_ids[parents[1]]
            concept.level = 3
        else:
            assert False, code    
        code_ids[code] = Classifier.c.insert(concept)
    
