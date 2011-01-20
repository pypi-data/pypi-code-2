import codecs
import re
import logging
import os
from os.path import join
from pprint import pprint
from lxml import html

from wdmmg.lib.loader import Loader
from wdmmg.model import Dataset, Entity, Classifier, Entry
import parse


log = logging.getLogger(__name__)


def dataset_from_dir(path, year):
    context = {}
    
    if path.endswith('/'):
        path = path[:len(path)-1]
    base_url = parse.BASE_URL % year
    
    basename = os.path.basename(path)
    if not basename.startswith('bundeshaushalt'):
        log.error("Invalid budget folder")
        return
    
    loader = Loader(u'bmf', label=u'Bundeshaushalt des Finanzministeriums', 
                    currency=u'EUR',
                    metadata={'html_link': unicode(base_url + "html/ep00.html")}, 
                    fresh_only=False)
    
    state_budget = loader.create_entity('budget', label=u'Bundeshaushalt')
    
    context['time'] = year
    context['from'] = state_budget.to_ref_dict()
    context['base_url'] = base_url
    load_einzelplaene(join(path, 'html'), context, loader)


def load_einzelplaene(html_dir, context, loader):
    doc = parse.file_to_doc(join(html_dir, 'ep00.html'))
    for (href, label) in parse.anchors(doc, "ep\d{2,}/ep\d{2,}.html"):
        fname = os.path.join(html_dir, href)
        name = re.match('.*ep(\d*).html', fname).group(1)
        html_link = context['base_url'] + "html/ep" + name + "/ep" + name + ".html",
        pdf_link = context['base_url'] + "pdf/epl" + name + ".pdf"
        ep = loader.create_entity(name, label=label.strip(), 
            html_link=html_link, pdf_link=pdf_link)
        ep_context = context.copy()
        ep_context['einzelplan'] = ep.to_ref_dict()
        load_kapitel(join(html_dir, href), ep_context, loader)


def load_kapitel(fname, context, loader):
    doc = parse.file_to_doc(fname)
    exp = "ep" + context.get('einzelplan').get('name') + "kp\d{2,}.html"
    print fname
    for (href, label) in parse.anchors(doc, exp):
        _fname = join(os.path.dirname(fname), href)
        ep_name = context.get('einzelplan').get('name')
        name_part = re.match('.*kp(\d*).html', _fname).group(1)
        name = ep_name + name_part
        
        html_link = context['base_url'] + "html/ep" + ep_name + "/ep" + \
            ep_name + "kp" + name_part + ".html"
        pdf_link = context['base_url'] + "pdf/epl" + ep_name + "/s" + \
            name + ".pdf"
        kapitel = loader.create_classifier(name, 'bund', label=label.strip(), html_link=html_link,
            pdf_link=pdf_link, einzelplan=context.get('einzelplan'))
        
        kp_context = context.copy()
        kp_context['kapitel'] = kapitel
        
        fname = join(os.path.dirname(_fname), href)
        doc = parse.file_to_doc(fname)
        exp = ".*kp" + name_part + "nr[ae].*.html"
        for (href, label) in parse.anchors(doc, exp):
            group_file = join(os.path.dirname(fname), href)
            load_titelgruppe(group_file, label, kp_context, loader)


def load_titelgruppe(fname, label, context, loader):
    group = {}
    doc = parse.file_to_doc(fname)
    match = re.match('.*nr([ae])(\d*).html', fname)
    name = context.get('kapitel').get('name') + "-" + match.group(2)
    
    flow = 'revenue' if match.group(1) == 'e' else 'spending'
    
    group = loader.create_classifier(name, 'bund', label=label.strip(), 
        flow=flow, 
        parent=context.get('kapitel').get('_id'),
        kapitel=context.get('kapitel'),
        einzelplan=context.get('einzelplan'))
    
    context['titelgruppe'] = group
    for row in doc.findall('.//tr'):
        load_posten_row(row, context, loader)


def load_posten_row(row, context, loader):
    year = int(context.get('time'))
    entries = []
    for i, column in enumerate(row.findall('./td')):
        if i == 0:
            name = column.xpath("string()")
            if not len(name):
                break
            if 'Tgr' in name:
                break
            if name.startswith('F '):
                context['flexible'] = True
                name = name[1:]
            else: 
                context['flexible'] = False
            name = [c for c in name if c in '-0123456789']
            if not len(name) == 9:
                break
            name = context.get('kapitel').get('name') + "".join(name)
            context['name'] = name.strip()
        if i == 1:
            context['label'] = column.text.strip() if column.text else None
            context['sections'] = []
            section = ""
            for elem in column:
                if elem.tag == 'hr': 
                    context['sections'].append(section)
                    section = ""
                elif 'title' in elem.keys() and \
                    elem.get('title').startswith('PDF Dokument'):
                    context['pdf_link'] = elem.get('href')
                else:
                    section += html.tostring(elem).strip()
            if len(section):
                context['sections'].append(section)
        if i == 2:
            entries.append(parse_posten(column, False, year, context))
        if i == 3:
            entries.append(parse_posten(column, True, year - 1, context))
        if i == 4:
            entries.append(parse_posten(column, True, year - 2, context))
    if not context.get('name'):
        return
    pcontext = context.copy()
    del pcontext['base_url']
    stelle = pcontext.copy()
    del stelle['sections']
    del stelle['time']
    del stelle['from']
    del stelle['einzelplan']
    del stelle['titelgruppe']
    del stelle['kapitel']
    stelle['parent'] = pcontext.get('kapitel').get('_id') 
    stelle['taxonomy'] = 'bund'
    posten = loader.create_classifier(**stelle)
    
    
    loader.classify_entry(pcontext, posten, 'posten')
    
    kap = pcontext['kapitel'].copy()
    del kap['einzelplan']
    loader.classify_entry(pcontext, kap, 'kapitel')
    
    tgr = pcontext['titelgruppe'].copy()
    del tgr['kapitel']
    del tgr['einzelplan']
    loader.classify_entry(pcontext, tgr, 'titelgruppe')
    
    name = pcontext['name']
    fkz1 = loader.get_classifier(name[10:11], 'fkz')
    fkz2 = loader.get_classifier(name[10:12], 'fkz')
    fkz3 = loader.get_classifier(name[10:13], 'fkz')
    
    gpl1 = loader.get_classifier(name[4:5], 'gpl')
    gpl2 = loader.get_classifier(name[4:6], 'gpl')
    gpl3 = loader.get_classifier(name[4:7], 'gpl')
    
    loader.classify_entry(pcontext, fkz1, 'fkz1')
    loader.classify_entry(pcontext, fkz2, 'fkz2')
    loader.classify_entry(pcontext, fkz3, 'fkz3')
    
    loader.classify_entry(pcontext, gpl1, 'gpl1')
    loader.classify_entry(pcontext, gpl2, 'gpl2')
    loader.classify_entry(pcontext, gpl3, 'gpl3')
    
    for entry in entries:
        e = pcontext.copy()
        e['to'] = pcontext['einzelplan']
        e['flow'] = e['titelgruppe']['flow']
        if e['flow'] != 'spending':
            e['to'], e['from'] = e['from'], e['to']
        e.update(entry)
        
        q = {'name': e['name'], 'projection': e['projection'], 
             'time': e['time']}
        loader.create_entry(**e)
      
def parse_posten(column, is_projection, year, context):
    p = {'projection': is_projection, 'time': year, 'amount': 0.0}
    if column.text: 
        try:
            val = column.text
            val = "".join([c for c in val if c in '-0123456789'])
            val = int(val) * 1000
            p['amount'] = float(val)
        except: pass
    return p
        
        