# -*- coding: utf-8 -*-
from citeulike_api import citeulike_api
from citeulike_api.citeulike_api import strip_html_tags, strip_tex_nonsense, strip_wrapping_braces
import codecs
import os.path
from sphinx.util import texescape
texescape.init()
from Recode import Recodec
tex_codec = Recodec('utf8..ltex')
from collections import defaultdict
from base import BaseRenderer

"""
output to ReST. This should probably be reimplemented as a Jinja2 thing, likke the ReST output
"""

class Renderer(BaseRenderer):
    
    # template_name = "bibtex_plain.bib"
    
    def __init__(self,
          escape_diacritics=False,
          escape_markup=True,
          attachment_path='.',
          *args, **kwargs):
        self.escape_diacritics = escape_diacritics
        self.escape_markup = escape_markup
        self.attachment_path = attachment_path
        super(Renderer, self).__init__(*args, **kwargs)
    
    def render(self, record_list):
        return list2bib(record_list,
          escape_diacritics=self.escape_diacritics,
          escape_markup=self.escape_markup,
          attachment_path=self.attachment_path)

def list2bib(arr, escape_diacritics=False,
            escape_markup=True,
            attachment_path='.'):
    """converts a list of python dicts representing the CUL JSON to a bibtex
    string
    
    TODO:
      * sort consistently
      * avoid duplicate keys (Titmuss, for example)
      * handle multiple field-stripping logics (HTML-friendly, BibTeX-friendly)
      * handle multiple character encodings
    """
    formatted = []
    for e in arr:
        formatted.append(dict2bib(e,
          escape_diacritics=escape_diacritics,
          escape_markup=escape_markup,
          attachment_path=attachment_path))
    return '\n'.join(formatted)

def dict2bib(obj,
        escape_diacritics=False,
        escape_markup=True,
        attachment_path='.'):
    """converts a single python dict to a bibtex
    entry
    """
    lines = []
    obj = citeulike_api.clean_article(obj)
    # import pdb; pdb.set_trace()
    key = citeulike_api.create_key(obj)
    lines.append('@%s{%s,' % (citeulike_api.CUL_FIELDS[obj['type']], key))
    bib_fields = defaultdict(list)
    pages = ''
    filters = strip_wrapping_braces,
    do_not_escape = set(['Local-Url', 'keywords', 'tags', 'doi'])
    if escape_diacritics:
        filters += tex_diacriticize,
    if escape_markup:
        filters += tex_escape,
    def filt(v):
        for f in filters:
            v = f(v)
        return v
    
    for k,v in obj.iteritems():

        #fields not requiring translation
        if k in ("title", "volume", "journal",
                "chapter", "issue", "citation",
                "institution", "organization",
                "booktitle", "series", "publisher",
                "location", "issn", "isbn",
                "address", "how_published",
                "edition", "school", "doi", "citation"):
            bib_fields[k].append(v)
        elif k in ('type', 'citation_keys',
                'username', 'posted_count',
                'article_id'): 
            pass #wilfully ignore dull fields
        elif k in ('notes', 'date', 
                'priority', 'rating', 'date_other'): 
            pass #too complicated or confusing for now
        elif k=='abstract':
            bib_fields['abstract'].append(
              strip_tex_nonsense(strip_html_tags(v)))
        elif k=="authors":
            bib_fields['author'].append( u" and ".join(v))
        elif k=="editors":
            bib_fields['editor'].append( u" and ".join(v))
        elif k=="start_page":
            pages = v + (bib_fields['pages'] or '-')
        elif k=="end_page":
            pages = (pages or '-') + v
        elif k=="tags":
            bib_fields['keywords'].append(u"; ".join(v))
            bib_fields['tags'].append(u", ".join(v))
            bib_fields['Tags'].append(u"; ".join(v))
        elif k=="published":
            try:
                bib_fields['year'].append(v[0])
                bib_fields['month'].append(
                  citeulike_api.month_name[int(v[1])][:3])
                bib_fields['day'].append(v[2])
            except IndexError:
                pass
        elif k=='linkouts':
            for lo in v:
                bib_fields['Url'].append( lo['url'])
        elif k=='userfiles':
            for uf in v:                
                bib_fields['Local-Url'].append(
                  os.path.join(attachment_path, uf['name'])
                )
        elif k=='href':
            if not v in bib_fields['Url']:
                bib_fields['Url'].insert(0, v)
        else:
            print u"unhandled field : %s: %s" % (k, unicode(v))
    if pages:
        bib_fields['pages'].append(pages)
    for k, v_list in bib_fields.iteritems():
        for v in v_list:
            if k not in do_not_escape:
                escaped_line = filt(v)
            else:
                escaped_line = v
            has_quotes, has_braces, has_non_numeric = False, False, False
            try:
                v = unicode(int(v))
            except ValueError:
                has_non_numeric = True
            if v.find('"')>=0:
                has_quotes = True
            if v.find('{')>=0:
                has_braces = True
            if has_braces or has_non_numeric:
                escaped_line = escaped_line.join(['"', '"'])
            if has_quotes:
                escaped_line = escaped_line.join(['{', '}'])
            if has_quotes and has_braces:
                print "warning: field with quotes and braces:", escaped_line
            next_line = u'    %s = %s,' % (k, escaped_line)
            lines.append(next_line)
        
    lines.append(u'}')
    return u'\n'.join(lines)

def tex_escape(field):
    """
    convert unicode field into a TeX-macro'd unicode field with tricky chars
    escaped such that an ascii or utf-8 representation won't choke old
    BibTeX. (eg. <, {, \, " are cleaned up)
    
    We assume that there is no TeX markup already.
    
    A smart-type-guessing thingy might be necessary for, e.g. abstracts.
    See:
    http://www.astro.rug.nl/~kuijken/latex.html
    or
    http://www.math.uiuc.edu/~hildebr/tex/course/intro1.html
    for a guide to escaping
    """
    return unicode(field).translate(texescape.tex_escape_map)
    # return codecs.encode(
    #   unicode(field).translate(texescape.tex_escape_map),
    # 'utf-8') #don't presume ascii safe because of non-eng chars

def tex_diacriticize(field):
    """take a unicode field and convert it to ASCII-safe using latex
    escaping"""
    field = codecs.encode(field, 'utf-8')
    translated, length = tex_codec.encode(field, 'replace')
    return unicode(translated)

