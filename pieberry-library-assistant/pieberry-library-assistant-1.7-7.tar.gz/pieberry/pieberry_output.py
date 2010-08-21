# coding=utf-8
# output parsers for pieberry
from pieberry_config import *
from utility.bibtex import *
from utility.latex import *
import string, re, os, sys
import traceback
import wx

class pieAllWriter:
    '''Meta-class that directs different types of output'''
    def __init__(self, entries=[]):
        '''entries is a list of bibdata dicts'''
        self._entries = entries
        self._location = config.get('PBoptions', 'default_bibliography')
        self._bibtex_writer = piePybtexWriter()
        self._tsv_writer = pieTSVWriter()

    def addEntry(self, bibdata):
        '''Add an entry to the output file'''
        self._bibtex_writer.addEntry(bibdata)
        if config.getboolean('PBoptions', 'export_tsv'):
            self._tsv_writer.addEntry(bibdata)

    def setLocation(self, location):
        '''Set the location of the file'''
        self._bibtex_writer.setLocation(location)
        if config.getboolean('PBoptions', 'export_tsv'):
            self._tsv_writer.setLocation(location)

    def write(self):
        '''Write to file. 'types' is a tuple of "contexts" to exclude
        from the write-out process, such as submissions.'''
        self._bibtex_writer.write()
        if config.getboolean('PBoptions', 'export_tsv'):
            self._tsv_writer.write()

class piePybtexWriter:
    '''Class to write out bibliographies as BibTex'''
    def __init__(self, entries=None):
        '''entries is a list of bibdata dicts'''
        self._entries = []
        self._location = config.get('PBoptions', 'default_bibliography')

    def addEntry(self, bibdata):
        '''Add an entry to the output file'''
        self._entries.append(bibdata)

    def setLocation(self, location):
        '''Set the location of the file'''
        self._location = location

    def write(self, backup=True):
        '''Write to file. 'types' is a tuple of "contexts" to exclude
        from the write-out process, such as submissions.'''
        if os.path.exists(self._location):
            try:
                # backup 
                f = open(self._location, 'r')
                if backup:
                    b = open(os.path.join(os.path.split(self._location)[0], 'backup.bib'), 'w')
                    b.write(f.read())
                    b.close()
                f.close()
            except:
                raise 'Could not open file'
        else:
            f = open(self._location, 'w')
            f.write('')
            f.close()
        try:
            from pybtex.database.input import bibtex
            from pybtex.database.output.bibtex import Writer
            from pybtex.database import BibliographyDataError
            from pybtex.core import Entry, Person
            from pybtex.bibtex.utils import split_name_list
            from pieberry_pybtex import pieberry_to_pybtex
        except:
            traceback.print_exc()
            raise 'Could not import pybtex'

        parser = bibtex.Parser(encoding='utf-8')
        bib_object = parser.parse_file(self._location)
        for ent in self._entries:
            if ent['exclude'] == True:
                continue
            new_pybtex_entry = pieberry_to_pybtex(ent, texify=True)
            if ent.has_key('bibtex_key'):
                bib_key = ent['bibtex_key']
            else:
                bib_key = autogen_bibtex_key(ent)
            invalid_key = True
            user_gen_new_key = False
            while invalid_key:
                invalid_key = False
                try:
                    bib_object.add_entry(bib_key, new_pybtex_entry)
                except BibliographyDataError:
                    if user_gen_new_key:
                        bib_key = increment_bibtex_key(bib_key)
                        invalid_key = True
                        continue
                    mdia = wx.MessageDialog(None, 'An entry with key %s already exists in the bibliography.\nWould you like to overwrite it? (If no, a new key will be generated' % bib_key, 'Duplicate key', style=wx.YES_NO|wx.ICON_QUESTION)
                    q = mdia.ShowModal()
                    if q == wx.ID_YES:
                        bib_object.entries[bib_key] = new_pybtex_entry
                    else:
                        user_gen_new_key = True
        # import latex_codec
        # latex_codec.register()
        writer = Writer(encoding='utf-8')
        writer.write_file(bib_object, self._location)
                    
class pieBibtexWriter:
    '''Class to write out bibliographies as BibTex'''
    def __init__(self, entries=None):
        '''entries is a list of bibdata dicts'''
        self._entries = []
        self._location = config.get('PBoptions', 'default_bibliography')

    def addEntry(self, bibdata):
        '''Add an entry to the output file'''
        self._entries.append(bibdata)

    def setLocation(self, location):
        '''Set the location of the file'''
        self._location = location

    def write(self):
        '''Write to file. 'types' is a tuple of "contexts" to exclude
        from the write-out process, such as submissions.'''
        savedata = ''
        for entry in self._entries:
            if entry['exclude'] == False:
                try:
                    savedata = savedata + format_bibtex_entry(entry)
                except UnicodeDecodeError:
                    print 'Bad unicode - omitting'
                except: 
                    traceback.print_exc()
                    print 'Unknown formatting error'
        if os.path.exists(self._location):
            outfile = open(self._location, 'r')
            current_data = outfile.read()
            outfile.close()
            savedata = current_data + savedata
        outfile = open(self._location, 'w')
        outfile.write(savedata)
        outfile.close()

class pieTSVWriter:
    '''Class to write out bibliographies in TSV with potentially
    arbitrary columns'''
    def __init__(self, entries=None):
        self._entries = []
        self._location = os.path.splitext(config.get('PBoptions', 'default_bibliography'))[0] + '.tsv'

    def addEntry(self, bibdata):
        '''Add an entry to the output file'''
        self._entries.append(bibdata)

    def setLocation(self, location):
        '''Set the location of the file'''
        self._location = os.path.splitext(location)[0] + '.tsv'

    def write(self):
        '''Write to file. 'types' is a tuple of "contexts" to exclude
        from the write-out process, such as submissions.'''
        # from pprint import pprint
        lines = []
        header = []
        if os.path.exists(self._location):
            f = open(self._location, 'r')
            lines = [unicode(line).rstrip().split('\t') for line in f.readlines()]
            f.close()
        if lines:
            header = lines[0]
        else:
            header = ('bibtex_key', 'author', 'title', 'year', 'month', 'howpublished', 'url', 'final_fn')
            lines.append(header)
        # pprint(header)
        for ent in self._entries:
            if ent['exclude'] == True:
                continue
            row = []
            for col in header:
                if ent.has_key(col):
                    row.append(ent[col])
                else:
                    row.append('')
            lines.append(row)
        # pprint(lines)
        f = open(self._location, 'w')
        f.writelines([u'%s\n' % string.join(line, '\t') for line in lines if len(line) > 0])
        f.close()

if __name__ == '__main__':
    import time
    spoofdata = {
        'title': 'Spoof title',
        'author': '{Goldman Saks}',
        'year': '1833',
        'month': 'January',
        'howpublished': 'Mungdinügn',
        'url': 'http://www.themong.spo.nn/a%20b.html',
        'annote': 'notey',
        'ancillary_downloadtime': time.localtime(),
        'ancillary_creationtime': time.localtime(),
        'ancillary_outfilename': 'C:noodles',
        'ancillary_locofdoc': 'http://www.hell.no',
        'exclude': True,
        'internal_author': 'Jon Hoo',
        'internal_title': 'Noh Wai'
        }
    
    w = piePybtexWriter()
    w.addEntry(spoofdata)
    w.write()
