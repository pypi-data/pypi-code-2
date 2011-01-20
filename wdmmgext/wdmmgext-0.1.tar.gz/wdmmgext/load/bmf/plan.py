from datetime import date
from zipfile import ZipFile
from StringIO import StringIO
import os, csv

import datapkg
from swiss.tabular import gdocs
from pylons import config

from wdmmg import model
from wdmmg.model import Classifier, KeyMeta

def drop(taxonomy='fkp'):
    Classifier.c.remove({'taxonomy': taxonomy})
    KeyMeta.c.remove({'collection': Classifier.collection_name, 'context': taxonomy})


def load_file(fileobj, taxonomy='fkp'):
    '''
    Loads the specified FKZ.
    '''
    code_ids = {}
    lines = sorted(fileobj.readlines(), reverse=True)
    for row_index, cells in enumerate(lines):
        code, title = cells.split(';', 1)
        cf = Classifier(name=code, label=title.strip(), description=None, 
                        change_date=None, taxonomy=taxonomy)
        if len(code) > 1:
            parent = code[:len(code)-1]
            cf.level = len(code)
            if not parent in code_ids.keys():
                code_ids[parent] = Classifier.c.insert({
                                            'name': parent, 
                                            'label': "(Unbenannt)", 
                                            'taxonomy': taxonomy})
            cf.parent = code_ids[parent]
        code_ids[code] = Classifier.c.insert(cf)
