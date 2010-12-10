'''tabola'''

from tabola.formats import FORMATS as formats

def all(iterable):
    for element in iterable:
        if not element: return False
    return True

class InvalidDatasetType(Exception):

    '''Only Datasets can be added to a DataBook.'''


class InvalidDimensions(Exception):
    
    '''Invalid size.'''

    
class UnsupportedFormat(NotImplementedError):
    
    '''Format is not supported'''


class Dataset(object):

    '''Tabular - Dataset object'''

    def __init__(self, *args, **kw):
        self._data = list(args)
        self.headers = kw.get('headers', tuple())
        self.title = kw.get('title')
        self._register_formats()

    def __len__(self):
        return self.height

    def __getitem__(self, key):
        if isinstance(key, basestring):
            if key in self._headers:
                # get 'key' index from each data
                pos = self._headers.index(key)
                return list(r[pos] for r in self._data)
            else:
                raise KeyError
        else:
            return self._data[key]

    def __setitem__(self, key, value):
        self._validate_row(value)
        self._data[key] = tuple(value)

    def __delitem__(self, key):
        del self._data[key]
        
    def __iter__(self):
        return self._data.__iter__()
        
    def _package(self, dicts=True):
        '''Packages Dataset into lists of dictionaries for transmission.'''
        if self.headers:
            if dicts:
                data = list(dict(zip(self.headers, r)) for r in self ._data)
            else:
                data = [list(self.headers)] + list(self._data)
        else:
            data = list(list(r) for r in self._data)
        return data
    
    @classmethod
    def _register_formats(cls):
        '''Adds format properties.'''
        for f in formats:
            try:
                try:
                    setattr(cls, f.title, property(f.export_set, f.import_set))
                except AttributeError:
                    setattr(cls, f.title, property(f.export_set))
            except AttributeError: pass

    def _get_headers(self):
        '''Headers property.'''
        return self._headers

    def _set_headers(self, collection):
        '''Validating headers setter.'''
        if self._validate_headers(collection):
            try:
                self._headers = list(collection)
            except TypeError:
                self._headers = []
        else:
            self._headers = []
            
    def _del_headers(self):
        self._headers = None
            
    headers = property(_get_headers, _set_headers, _del_headers)

    def _get_dict(self):
        '''Returns python dict of Dataset.'''
        return self._package()
    
    def _set_dict(self, rows):
        if not len(rows): return None
        if isinstance(rows[0], list):
            self.clear()
            for row in rows: self.append_row(row)
        elif isinstance(rows[0], dict):
            self.clear()
            self.headers = rows[0].keys()
            for row in rows: self.append_row(row.values())
        else:
            raise UnsupportedFormat
        
    dict = property(_get_dict, _set_dict)
    
    def _validate_column(self, col):
        if self.headers:
            is_valid = (len(col) - 1) == self.height
        else:
            is_valid = len(col) == self.height if self.height else True
        if is_valid: return True
        raise InvalidDimensions()
    
    def _validate_headers(self, header):
        return all((len(x)==self.width for x in self._data))
    
    def _validate_row(self, row):
        if len(row) == self.width if self.width else True: return True
        raise InvalidDimensions()
    
    @property
    def height(self):
        '''Returns the height of the Dataset.'''
        return len(self._data)

    @property
    def width(self):
        '''Returns the width of the Dataset.'''
        try:
            return len(self._data[0])
        except IndexError:
            try:
                return len(self.headers)
            except TypeError:
                return 0
            
    def append_column(self, column):
        if self._validate_column(column):
            if self.headers:
                # pop the first item off and add to headers
                self.headers.append(column[0])
                column = column[1:]
            if self.height and self.width:
                for i, row in enumerate(self._data):
                    _row = list(row)
                    _row.append(column[i])
                    self._data[i] = tuple(_row)
            else:
                self._data = [tuple([r]) for r in column]

    def append_row(self, row):
        '''Adds a row to the end of Dataset'''
        if self._validate_row(row): self._data.append(tuple(row))
        
    def clear(self):
        '''Erases all data from Dataset.'''
        self._headers = None
        self._data = list()
        
    def get_row_dict(self, key):
        if self.headers: return dict(zip(self.headers, self.__getitem__(key))) 
        raise UnsupportedFormat()

    def insert_row(self, i, row):
        '''Inserts a row at given position in Dataset'''
        if self._validate(row): self._data.insert(i, tuple(row))
    
    def iter_row_dicts(self):
        if self.headers: return self._package() 
        raise UnsupportedFormat()
    

class Databook(object):
    
    '''A book of Dataset objects.'''

    def __init__(self, sets=[]):
        self._datasets = sets
        self._register_formats()
        
    def __len__(self):
        '''The number of Datasets within Databook.'''
        return len(self._datasets)    
    
    def __iter__(self):
        return self._datasets.__iter__()
    
    def _package(self):
        '''Packages Databook for delivery.'''
        return list(dict(title=d.title, data=d.dict) for d in self._datasets)
        
    @classmethod
    def _register_formats(cls):
        '''Adds format properties.'''
        for f in formats:
            try:
                try:
                    setattr(cls, f.title, property(f.export_book, f.import_book))
                except AttributeError:
                    setattr(cls, f.title, property(f.export_book))                    
            except AttributeError: pass

    def append_dataset(self, dataset):
        '''Adds given dataset.'''
        if isinstance(dataset, Dataset):
            self._datasets.append(dataset)
        else:
            raise InvalidDatasetType()

    def clear(self):
        self._datasets = []