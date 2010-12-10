'''ablib - JSON Support.'''

try:
    import simplejson as json
except ImportError:
    from python import json
    
import tabola.core

title = 'json'
extensions = ('json', 'jsn')

def export_set(dataset):
    '''Returns JSON representation of Dataset.'''
    return json.dumps(dataset.dict)

def export_book(databook):
    '''Returns JSON representation of Databook.'''
    return json.dumps(databook._package())
    
def import_set(dset, in_stream):
    '''Returns dataset from JSON stream.'''
    dset.clear()
    dset.dict = json.loads(in_stream)

def import_book(dbook, in_stream):
    '''Returns databook from JSON stream.'''
    dbook.clear()
    for sheet in json.loads(in_stream):
        data = tabola.core.Dataset()
        data.title = sheet['title']
        data.dict = sheet['data']
        dbook.append_dataset(data)