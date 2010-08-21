# 

from pieberry_config import *
from utility.decoding import *
from utility.bibtex import *
from utility.latex import *
from utility.latex import escape_bad_latex_chars as eblc
from utility.latex import unescape_bad_latex_chars as ublc
from pybtex.database.input import bibtex
from pieberry_pybtex_style import Formatter
from pybtex.richtext import Text, Tag
from pybtex.backends import latex, html, plaintext
from pybtex.bibtex.utils import split_name_list
from pybtex.core import Entry, Person
from StringIO import StringIO
import re, time
# import latex_codec

# latex_codec.register()

re_href = re.compile(r'\\href\{(.+?)\}\{(.+?)\}')
re_fileloc = re.compile(r'Saved[_ ]to: (.+?\.(pdf|PDF|Pdf))')
re_corpname = re.compile(r'^\{(.+?)\}(.*)')
re_pubdate = re.compile(r'Publication_date: ([a-z]{3} [a-z]{3} [ 0-9][0-9] [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4})', re.IGNORECASE)
re_dateprefix = re.compile(r'^[12][0-9]{3}[01][0-9][0123][0-9]')
search_terms = ('title', 't', 'author', 'a', 'month', 'm', 'year', 'y', 'key', 'k', 'all')
filesearch_terms = ('title', 't', 'year', 'y', 'month', 'm', 'library', 'l', 'projects', 'p', 'all')
filesearch_abbrev = {'t': 'title', 'y': 'year', 'm': 'month', 'l': 'library', 'p': 'projects', 'all': 'all'}
search_abbrev = {'t': 'title', 'a': 'author', 'y': 'year', 'm': 'month', 'k': 'key', 'all': 'all'}

def pieberry_to_pybtex(ent, texify=False):
    '''convert from pieberry's data dict to a pybtex Entry'''
    from pieberry_output import escape_bad_latex_chars as eblc
    if ent.has_key('bibtex_type'):
        new_pybtex_entry = Entry(ent['bibtex_type'].lower())
    else:
        new_pybtex_entry = Entry(config.get('PBoptions', 'default_bibtex_entry_type'))
    for k, v in ent.items():
        if k in person_fields:
            if ent.has_key('corporate_author') and ent['corporate_author'] == True:
                new_pybtex_entry.add_person(Person('{%s}' % ent[k]), k)
            else:
                for name in split_name_list(ent[k]):
                    new_pybtex_entry.add_person(Person(name), k)
        else:
            if k in bibtex_fields:
                if texify:
                    # the only way i've found to force encoding to latex
                    # not used for now - may be unnecessary with modern bibtex
                    # new_pybtex_entry.fields[k] = unicode(unicode(eblc(v)).encode('latex'))
                    new_pybtex_entry.fields[k] = eblc(v)
                else:
                    new_pybtex_entry.fields[k] = v
    return new_pybtex_entry

def pybtex_to_pieberry(key, ent):
    '''Transform pybtex Entry class to a dict understood by pieberry'''
    ret = {}
    ret['pdflink'] = ''
    # ret['final_fn'] = ''
    ret['bibtex_key'] = key
    for persons in ent.persons.itervalues():
        for person in persons:
            person.text = unicode(person)
    for k, v in ent.fields.items():
        # print 'unicode', v
        # print 'utf8', v.encode('utf-8')
        # print 'cp1252', v.encode('cp1252')
        # try:
        #     assert type(v) == unicode
        # except:
        #     v = unicode(v, 'utf-8')
        if k in bibtex_fields:
            ret[k] = ublc(v)
        if k == 'annote':
            filehere = re_fileloc.search(ublc(v))
            if filehere:
                ret['final_fn'] = os.path.join(config.get('PBoptions', 'workingdir'), ublc(filehere.group(1)))
#                print 'establishing fileloc ', ret['final_fn'], config.get('PBoptions', 'workingdir')
#                print 'WTF ', os.path.join(config.get('PBoptions', 'workingdir'), ublc(filehere.group(1)))
            datehere = re_pubdate.search(v)
            try:
                if datehere:
                    ret['creation_date'] = time.strptime(datehere.group(1))
                else:
                    ret['creation_date'] = time.strptime('%s %s' % (ent.fields['month'], ent.fields['year']), '%B %Y')
            except:
                ret['creation_date'] = time.localtime()
        else:
            try:
                if ent.fields.has_key('year') and ent.fields.has_key('month'):
                    ret['creation_date'] = time.strptime('%s %s' % (ent.fields['month'], ent.fields['year']), '%B %Y')
                else:
                    ret['creation_date'] = time.localtime()
            except:
                ret['creation_date'] = time.localtime()
            
        if k == 'howpublished' and not ret.has_key('url'):
            urlhere = re_href.search(v)
            if urlhere:
                ret['url'] = ret['pdflink'] = ublc(urlhere.group(1))
        if k == 'url':
            ret['pdflink'] = ublc(v)
    formatter = Formatter()
    formatted_names = formatter.format_people(ent)
    rendered_names = formatted_names.render(plaintext.Writer()).rstrip('.')
    corpnamehere = re_corpname.match(rendered_names)
    if corpnamehere:
        ret['corporate_author'] = True
        rendered_names = '%s%s' % (corpnamehere.group(1), corpnamehere.group(2))
    else:
        ret['corporate_author'] = False
    ret['author'] = rendered_names
    ret['pdflink_context'] = ''
    ret['bibtex_type'] = ent.type
    ret['exclude'] = False
    ret['internal_author'] = ''
    ret['internal_title'] = ''
    return ret

def get_top_search_results(searchtext, number=25):
    '''high-level function to return pieberry-friendly list of dicts
    corresponding to top ranked search results in the default
    bibliography'''
    fmts = format_search(searchtext)
    ents = pybtex_entries_from_file(config.get('PBoptions', 'default_bibliography'))
    ranks = exec_search(fmts, ents).items()
    ranks.sort(lambda x, y: cmp(y[1], x[1]))
    return [pybtex_to_pieberry(ky, ents[ky]) for ky, vl in ranks[:number] if vl > 0]

def get_file_search_results(searchtext, number=50):
    fmts = format_search(searchtext, filesearch_terms, filesearch_abbrev)
    # print fmts
    pdir = config.get('AToptions', 'filing_directory')
    ldir = config.get('PBoptions', 'workingdir')

    go_p = bool([t for t in filesearch_abbrev.values() if t in ('title', 'all', 'projects')])
    go_l = bool([t for t in filesearch_abbrev.values() if t in ('title', 'all', 'library')])

    allres = []
    if go_p:
        allres.extend(recurs_dirsearch(pdir, fmts, insystem='projects'))
    if go_l:
        allres.extend(recurs_dirsearch(ldir, fmts, insystem='library'))

    allres.sort(lambda x, y: cmp(y[1], x[1]))
    return allres[:number]

def recurs_dirsearch(wdir, searchdict, insystem):
    hitfiles = []    
    # print 'entering directory: %s' % wdir
    subdirs = [filesystem_decode(f) for f in os.listdir(wdir) if os.path.isdir(os.path.join(wdir,f))]
    # print 'subdirs:', subdirs
    for subdir in subdirs:
        hitfiles.extend(recurs_dirsearch(os.path.join(wdir,subdir), searchdict, insystem))

    files = [filesystem_decode(f) for f in os.listdir(wdir) if os.path.isfile(os.path.join(wdir, f))]
    # print 'files:', files
    strs = []
    if searchdict.has_key('all'):
        strs.extend(searchdict['all'])
    if searchdict.has_key('title'):
        strs.extend(searchdict['title'])
    if searchdict.has_key('library') and insystem == 'library':
        strs.extend(searchdict['library'])
    if searchdict.has_key('projects') and insystem == 'projects':
        strs.extend(searchdict['projects'])
    # print strs

    for fl in files:
        datescore = 0
        strscore = 0
        dpfm = re_dateprefix.match(fl)
        if dpfm:
            dateprefix = dpfm.group(0)
            ftime = '%s %s %s' % (dateprefix[0:4], dateprefix[4:6], dateprefix[6:8])
            fldate = time.strptime(ftime, '%Y %m %d')
        else:
            fldate = time.localtime(os.stat(os.path.join(wdir,fl))[9])
        if searchdict.has_key('year'):
            for y in searchdict['year']:
                if y == time.strftime('%Y', fldate):
                    datescore += 1
        if searchdict.has_key('month'):
            for m in searchdict['month']:
                if m.lower() == time.strftime('%B', fldate).lower() or m == time.strftime('%m', fldate):
                    datescore += 1
        for strg in strs:
            if strg.lower() in fl.lower(): 
                strscore += 1
                # print 'HIT', strg
            
        if strscore > 0:
            strscore += datescore
            hitfiles.append((os.path.join(wdir, fl), strscore))

    # print 'hitfiles:', hitfiles
    return hitfiles

def format_search(text, sterms=search_terms, sabbrev=search_abbrev):
    '''formats a text string into a search dict containing bibtex
    field keys and lists of relevant terms to search for in those
    fields.'''
    re_search = re.compile(r'\s*(%s)==(.+?)\s*(?:,|$)' % string.join(sterms, r'|'))
    s = [k for k in re_search.split(text) if k != '']
    search_dict = {}
    if len(s) == 1:
        search_dict['all'] = s[0].split(';')
    for i in range(len(s)):
        if s[i] in sterms:
            if not s[i] in sabbrev.values():
                search_dict[sabbrev[s[i]]] = s[i+1].split(';')
            else:
                search_dict[s[i]] = s[i+1].split(';')
    return search_dict

# weights for search scoring
search_w = {'exact': 35, 'occurrence': 25, 'fuzzy': 10}
field_w = {'key': 30, 'author': 25, 'title': 20, 'other': 10}

def exec_search(searchdict, entries):
    '''search through pybtex entries for terms in a searchdict'''
    # ranked is a dict whose keys are bibtex keys and values are
    # 'scores' for the entries thus indexed.
    def _debug(t):
        # print t
        pass

    ranked = dict([(k, 0) for k in entries.keys()])

    # key exact match algorithm
    if searchdict.has_key('key'):
        for term in searchdict['key']:
            if entries.has_key(term):
                ranked[term] += search_w['exact'] * field_w['key']

    for entkey, entry in entries.items():
        _debug('Entry - %s, %s' % (unicode(entkey), unicode(entry)))
        for serkey, servals in searchdict.items():
            _debug('Search - %s, %s' % (unicode(serkey), unicode(servals)))
            if serkey == 'author' and entry.persons.has_key('author'):
                auth = string.join([unicode(p) for p in entry.persons['author']])
                for term in servals:
                    if term.strip().lower() == auth.strip().lower():
                        ranked[entkey] += search_w['exact'] * field_w['author']
                    elif term.strip().lower() in auth.strip().lower():
                        ranked[entkey] += search_w['occurrence'] * field_w['author']
            elif serkey == 'title' and entry.fields.has_key('title'):
                title = entry.fields['title']
                for term in servals:
                    if term.strip().lower() == title.strip().lower():
                        ranked[entkey] += search_w['exact'] * field_w['title']
                    elif term.strip().lower() in title.strip().lower():
                        ranked[entkey] += search_w['occurrence'] * field_w['title']
            elif serkey == 'key':
                for term in servals:
                    if (term != entkey) and (term.strip().lower() in entkey.strip().lower()):
                        ranked[entkey] += search_w['occurrence'] * field_w['key']
            elif serkey == 'all':
                if entry.persons.has_key('author'):
                    auth = string.join([unicode(p) for p in entry.persons['author']])
                else:
                    auth = ''
                for term in servals:
                    if term.strip().lower() == auth.strip().lower():
                        ranked[entkey] += search_w['exact'] * field_w['author']
                    elif term.strip().lower() in auth.strip().lower():
                        ranked[entkey] += search_w['occurrence'] * field_w['author']
                    for fkey, fval in entry.fields.items():
                        if term.strip().lower() == unicode(fval).strip().lower():
                            if fkey in field_w.keys():
                                ranked[entkey] += search_w['exact'] * field_w[fkey]
                            else:
                                ranked[entkey] += search_w['exact'] * field_w['other']
                        if term.strip().lower() in unicode(fval).strip().lower():
                            if fkey in field_w.keys():
                                ranked[entkey] += search_w['occurrence'] * field_w[fkey]
                            else:
                                ranked[entkey] += search_w['occurrence'] * field_w['other']
            else:
                if entry.fields.has_key(serkey):
                    for term in servals:
                        if term.strip().lower() == unicode(entry.fields[serkey]).strip().lower():
                            ranked[entkey] += search_w['exact'] * field_w['other']
                        elif term.strip().lower() in unicode(entry.fields[serkey]).strip().lower():
                            ranked[entkey] += search_w['occurrence'] * field_w['other']
    return ranked
    
def pybtex_entries_from_file(filename):
    parser = bibtex.Parser(encoding='utf-8')
    bib_data = parser.parse_file(filename)
    return bib_data.entries

def get_formatted_citation(e):
    return get_formatted_citation_html(e)

def get_formatted_citation_from_bibtex(bibtex_entry):
    parser = bibtex.Parser(encoding='utf-8')
    f = open(os.path.join(sysdir, 'temp.bib'), 'w')
    f.write(bibtex_entry)
    f.close()
    bib_data = parser.parse_file(os.path.join(sysdir, 'temp.bib'))
    e = bib_data.entries[bib_data.entries.keys()[0]]
    return get_formatted_citation(e)

def get_formatted_citation(e, key='k', format='html'):
    formatter = Formatter()
    ents = ((key, e),)
    formatted_data = formatter.format_entries(ents)
    for d in formatted_data:
        if format == 'html':
            rendered_data = d.text.render(html.Writer())
        else:
            rendered_data = d.text.render(plaintext.Writer())
    # get hrefs in order
    href_search = re_href.search(rendered_data)
    output_data = None
    from pieberry_output import unescape_bad_latex_chars as ublc
    if href_search and format == 'html': 
        href = href_search.group(1)
        label = href_search.group(2)
        output_data = re_href.sub('<a href="%s">%s</a>' % (ublc(href), label), rendered_data)
    elif href_search and format == 'plaintext':
        href = href_search.group(1)
        label = href_search.group(2)
        output_data = re_href.sub(label, rendered_data)
    elif format == 'html':
        # hyperlink urls
        if e.fields.has_key('url'):
            output_data = rendered_data.replace(e.fields['howpublished'], '<a href="%s">%s</a>' % (ublc(e.fields['url']), e.fields['howpublished']))
    # hacky reformatting of URLs
    if not output_data:
        output_data = rendered_data
    transtbl = {ord('{'): None, ord('}'): None}
    output_data = output_data.translate(transtbl)
    return output_data


if __name__ == '__main__':
    sstring = 'library==summary, year==2010, month==july'
    print get_file_search_results(sstring)

#     testtext = '''
# @Booklet{AEMC2009_DraRepRevNatFraEleDisNetPlaExp,
#   author = {{Australian Spingroin}},
#   title = {Draft Report - Review of National Framework for Electricity Distribution Network Planning and Expansio},
#   howpublished = {\href{http://aemc.gov.au/Media/docs/EPR0015\%20-\%20Draft\%20Report-8959583c-f010-408b-9a52-89dac517020a-0.pdf}{Web site}},
#   month = {July},
#   year = 2009,
#   annote = {Downloaded_on: Wed Jul 14 19:26:55 2010
# Publication_date: Tue Jul  7 14:25:00 2009
# Saved_to: /home/raif/development/data/Australian Energy Market Commission/Review of National Framework for Electricity Distribution Network Planning and Expansio/20090707 Draft Report.pdf
# Author_from_metadata: Rose Campisi
# Title_from_metadata: Microsoft Word - DPR Draft Report - Contents and Summary - FINAL FOR PUBLICATION.DOC}}


# '''
#     import time
#     spoofdata = {
#         'title': 'Spoof title',
#         'author': '{Goldman Saks}',
#         'year': '1833',
#         'month': 'January',
#         'howpublished': "Mungdin{\''u}gn",
#         'url': 'http://www.themong.spo.nn/',
#         'annote': 'notey',
#         'download_time': time.localtime(),
#         'creation_date': time.localtime(),
#         'final_fn': 'C:noodles',
#         'pdflink': 'http://www.hell.no',
#         'exclude': True,
#         'internal_author': 'Jon Hoo',
#         'internal_title': 'Noh Wai',
#         'journal': 'journal of stuff',
#         'volume': 'Vol 1',
#         'bibtex_type': 'article'
#         }

#     from pprint import pprint
#     # pprint.pprint(format_search('author==gronongin, y==1020'))
#     # pprint.pprint(format_search('author==gronongin;joney title=wot, y==1020'))
#     # pprint.pprint(format_search('lies lies lies'))
#     # pprint.pprint(format_search('all==who;wha;there'))
#     # st = 'dsfksdf'#'y==1833, all==saks' #'a==saks, key==Sa1833_Spotit'
#     # print get_top_search_results(st)

#     bibd = pieberry_to_pybtex(spoofdata)
#     # print dir(bibd)
#     # print bibd.type
#     # pprint.pprint(bibd.fields)
#     # bibe = pybtex_to_pieberry('thekey', bibd)
#     # pprint.pprint(bibe)
#     # bib_data = get_formatted_citation_from_bibtex(testtext)
#     # bibd = pieberry_to_pybtex(spoofdata)
#     bib_data = get_formatted_citation_html_alternate(bibd)
#     print bib_data


# # a data object from pybtex appears to have as its key attribute a
# # dict full of entries referenced by bibtex key, and have additional
# # methods 'add_entry', 'add_entries'. These entries in turn have a
# # range of attributes including: ('add_person', 'collection',
# # 'fields', 'get_crossref', 'persons', 'type', 'vars'). 'persons'
# # returns a dict with person objects indexed by bibtex field. 'fields'
# # returns a simple dict with bibtex keys and values.

