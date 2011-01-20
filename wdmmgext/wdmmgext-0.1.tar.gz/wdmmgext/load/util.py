'''Utilities that are useful to more than one loader module.
'''
import re
import wdmmg.model as model
import urllib2
from urllib2 import urlopen
from urllib import urlencode
import sys
import cgi
try: import json
except ImportError: import simplejson as json
from BeautifulSoup import BeautifulSoup

def byname_string(name, parent):
    return str(parent) + "--" + name


class CofogMapper(object):
    '''
    In the published data, the "function" and "subfunction" columns are used
    inconsistently. This is partly because some departments continue to use a
    previous coding system, and partly because only two columns have been
    allowed for the three levels of the COFOG hierarchy.

    This class uses a mapping provided by William Waites to work out the
    correct COFOG code, given the published data.
    '''
    def __init__(self, mappings):
        '''
        Constructs a COFOG mapper from a mappings object (which is
        usually loaded from a JSON file).

        mappings - a list of triples. In each
            triple, the first element is the good code, and the second and
            third elements give the published values. If the first element
            (the good code) contains non-numerical suffix, it will be removed.
        '''
        self.mappings = {}
        for good, bad1, bad2 in mappings:
            good = re.match(r'([0-9]+(\.[0-9])*)', good).group(1)
            self.mappings[bad1, bad2] = good

    def fix(self, function, subfunction):
        '''
        Looks up the fixed COFOG code given the published values.

        Returns a list giving all available COFOG levels, e.g.
        `[u'01', u'01.1', u'01.1.1']`

        Returns an empty list if no COFOG mapping has been
        defined.
        '''
        ans = self.mappings.get((function, subfunction))
        if ans is None:
            return []
        parts = ans.split('.')
        return ['.'.join(parts[:i+1]) for i, _ in enumerate(parts)]



# tree structure for allocating codes
class Node(object):
    # store a dictionary of nodes by name
    byname = {}
    # when you create the object...
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        if parent is None:
            parent_name = ''
        else:
            parent_name = parent.name
        name_string = byname_string(name, parent_name)
        #print "creating node with name " + name_string
        self.byname[name_string] = self
        if parent is None:  # root pseudo-node
            self.code = 0
        else:  # all normal nodes
            self.parent.children.append(self)
            self.code = len(self.parent.children) # 'end' of code
            # set 0 if necessary
    def get_codes(self, codelist):
        #print "get_codes"
        if self.code:
            # get own code first, then call recursively for each parent
            codelist.append(str(self.code))
            self.parent.get_codes(codelist)

def get_code(nodename, parentname=''):
    # look in the dictionary for the node 
    name_string = byname_string(nodename, parentname)
    #print "get_code, looking with " + name_string
    node = Node.byname.get(name_string)
    if node is None: return ''
    codes = []
    node.get_codes(codes)
    codes.reverse()
    # hack to deal with the Flash requirement for initial zeros
    if len(codes[0])==1:
        codes[0] = '0' + codes[0]            
    code = '.'.join(codes)
    #print code
    return unicode(str(code))

def addnodes(names, parent):
    #print 'addnodes'
    for name in names:
        # check by name - hack
        if parent is None:
            parent_name = ''
        else:
            parent_name = parent.name
        name_string = byname_string(name, parent_name)
        #print "addnodes, checking with " + name_string
        newnode = Node.byname.get(name_string)
        if newnode is None:
            newnode = Node(name, parent)
        parent = newnode
    
def to_float(s):
    '''Clean up numbers: remove commas & spaces and convert to float.
    '''
    if not s: return 0.0
    s = s.replace(',','')
    s = s.replace(' ','')
    return float(s)

def get_or_create_dataset(name, long_name=None, currency=None, notes=None):
    '''Retrieves the dataset with given name, creating it if necessary.
    Use with caution!
    '''
    dataset_ = model.Session.query(model.Dataset).filter_by(name=name).first()
    if not dataset_:
        dataset_ = model.Dataset(name=name, long_name=long_name,\
           currency=currency, notes=notes)
        model.Session.add(dataset_)
        model.Session.commit()
    return dataset_
    
def get_or_create_key(name, notes):
    '''Retrieves the Key called 'name', creating it if necessary.
    '''
    key = model.Session.query(model.Key).filter_by(name=name).first()
    if not key:
        key = model.Key(name=name, notes=notes)
        model.Session.add(key)
    return key

def get_or_create_value(key, code, name=None, notes=u'', index=None, parent=None):
    '''Get or create an enumeration value using an optional cache (index).
    '''
    if not name:
        name = code
    def get_value():
        ev = model.Session.query(model.EnumerationValue).filter_by(key=key,
                code=code).first()
        if ev is None:
            ev = model.EnumerationValue(
                key=key, code=code, name=name or code, notes=notes)
            if parent: 
                key_parent = model.Session.query(model.Key).filter_by(name=u'parent').first()
                if not key_parent:
                    key_parent = model.Key(name=u'parent', notes=u'Means "is part of".')
                    model.Session.add(key_parent)
                ev.keyvalues[key_parent] = parent
            model.Session.add(ev)
        return ev
    if index is None:
        return get_value()
    else:
        if (key.name, code) not in index:
            index[key.name, code] = get_value()
        return index[key.name, code]

# Get the column numbers for the particular sheet that we care about.
def find_idx(header, matchword, required=False):
    idxlist = [ i for i, word in enumerate(header) if matchword in word]
    if not idxlist:
        if required:
            msg = '!! WARNING! Standard header %s not found in %s. Skipping file.' % (
                    matchword, filename)
            print(msg)
            raise Exception(msg)
        else:
            return None
    return idxlist[0]
		
# Translate a phrase from one language to another, using the 
# Google Translate API (used for Israeli data)
def translate(from_lang, to_lang, phrase):
    # Documentation for Google Translate API: 
    # http://code.google.com/apis/ajaxlanguage/documentation/#Examples
    langpair='%s|%s'%(from_lang,to_lang)
    base_url='http://ajax.googleapis.com/ajax/services/language/translate?'
    params=urlencode( (('v',1.0),
                       ('q',phrase),
                       ('langpair',langpair),) )
    url=base_url+params
    try:
        content=urlopen(url).read()
    except urllib2.URLError:
        return u'Translation not available'
    try:
        trans_dict=json.loads(content)
    except AttributeError:
        trans_dict=json.read(content)
    if trans_dict['responseData']:
        translation = trans_dict['responseData']['translatedText']
        s = BeautifulSoup(translation,convertEntities=BeautifulSoup.HTML_ENTITIES).contents[0]
        return unicode(s)
    else:
        return ''

