# -*- coding: UTF-8 -*-
# FTS Reporting system loader 

import os
import csv
from lxml import etree
from os.path import dirname, join
from wdmmg.model import Dataset, Entry, Entity, Classifier
from wdmmg.lib.loader import Loader
from wdmmg.lib.munge import to_name

from pylons import config

# OPEN ISSUES
#
# * Find and apply EC budget taxonomy
# * Consortium destination entities

DATASET_NAME = u'fts'
TAXONOMY = 'ec'

def load_countries(fn):
    countries = {}
    fh = open(fn, 'rb')
    for row in csv.reader(fh, delimiter=',', quotechar='"'):
        name, _, code, _, _ = row
        countries[code] = name
    return countries
    

def num_to_float(num):
    if num is None: 
        return None
    num = num.replace('%', '').strip().replace('.', '').replace(',', '')
    try:
        return float(num)
    except: 
        None

def load_report(loader, fn):
    doc = etree.parse(fn)
    for commitment in doc.findall('//commitment'):
        base_entry = {}
        base_entry['time'] = int(commitment.findtext('year'))
        base_entry['total'] = num_to_float(commitment.findtext('amount'))
        base_entry['cofinancing_rate'] = commitment.findtext('cofinancing_rate')
        base_entry['cofinancing_rate_pct'] = num_to_float(base_entry['cofinancing_rate'])
        base_entry['position_key'] = commitment.findtext('position_key')
        base_entry['grant_subject'] = commitment.findtext('grant_subject')
        base_entry['responsible_department'] = commitment.findtext('responsible_department')
        base_entry['source_file'] = fn
        base_entry['actiontype'] = commitment.findtext('actiontype')
        budget_line = commitment.findtext('budget_line')
        
        name, code = budget_line.rsplit('(', 1)
        base_entry['budget_item'] = name.strip()
        base_entry['budget_code'] = code.replace(')', '').replace('"', '').strip()
        
        dep_name = to_name(unicode(base_entry['responsible_department']))
        from_ = loader.create_entity(dep_name, label=base_entry['responsible_department'])
        base_entry['from'] = from_
        
        for beneficiary in commitment.findall('.//beneficiary'): 
            to = {}
            entry = base_entry.copy()
            #print dir(base_entry)
            #entry['line_no'] = base_entry.sourceline
            to['label'] = beneficiary.findtext('name')
            if '*' in to['label']:
                to['label'], to['alias'] = to['label'].split('*', 1)
            to['address'] = beneficiary.findtext('address')
            to['city'] = beneficiary.findtext('city')
            to['post_code'] = beneficiary.findtext('post_code')
            to['country'] = beneficiary.findtext('country')
            to['geozone'] = beneficiary.findtext('geozone')
            to['coordinator'] = beneficiary.findtext('coordinator') == "1"
            detail_amount = commitment.findtext('detail_amount')
            if detail_amount is None or not len(detail_amount): 
                entry['amount'] = num_to_float(commitment.findtext('detail_amount'))
            if entry['amount'] is None:
                entry['amount'] = base_entry['total']
            to_entity = loader.create_entity(to_name(unicode(to['label'])), **to)
            entry['to'] = to_entity
            e = loader.create_entry(**entry)
            #print e

def load_tsv(fn):
    fh = open(fn, 'rb')
    reader = csv.reader(fh, delimiter='\t')
    header = reader.next()
    #print header
    desc, columns = header[0], header[1:]
    rows, column_dim = desc.split('\\')
    row_dims = rows.split(',')
    cells = []
    for row in reader:
        row_header = row[0].split(',')
        row_data = dict(zip(row_dims, row_header))
        for i, column in enumerate(row[1:]):
            cell = row_data.copy()
            cell[column_dim] = columns[i].strip()
            try:
                cell['measure'] = float(column)
            except ValueError, ve: 
                cell['measure'] = None
            cells.append(cell)
    fh.close()
    return cells

def set_indicator(time, geo, key, value):
    print "Set Eurostat indicator: ", time, geo, key, value
    #print Entry.find({'time': time, 'to.country': geo}).count()
    Entry.c.update({'time': time, 'to.country': geo},
                   {'$set': {key: value}}) 

def load_unemployment(fn, countries, key='teilm020', 
    label='Employment - [teina300]; Percentage change q/q-1 (SA)', time_suffix='M12'):
    cells = load_tsv(fn)
    times = dict([(str(t) + time_suffix, t) for t in Entry.c.distinct('time')])
    for cell in cells:
        if not cell.get('sex') == 'T': 
            continue
        update_time = times.get(cell.get('time'))
        if not update_time: continue 
        update_geo = countries.get(cell.get('geo'))
        if not update_geo: continue 
        Entry.describe_key(key, label, DATASET_NAME)
        set_indicator(update_time, update_geo, key, cell.get('measure'))

def load_industrial_production(fn, countries, key='teiis080', 
    label='Industrial production - total industry (excluding construction) - [teiis080]; Percentage change m/m-1 (SA)', time_suffix='M12'):
    cells = load_tsv(fn)
    times = dict([(str(t) + time_suffix, t) for t in Entry.c.distinct('time')])
    for cell in cells:
        update_time = times.get(cell.get('time'))
        if not update_time: continue
        update_geo = countries.get(cell.get('geo'))
        if not update_geo: continue
        Entry.describe_key(key, label, DATASET_NAME)
        set_indicator(update_time, update_geo, key, cell.get('measure'))


def load():
    loader = Loader(DATASET_NAME, "EC Financial Transparency System", currency='EUR',
                    description = u'''Financial commitments by the European Commission''',
                    fresh_only=False) #DEBUG
    base_dir = os.path.join(config['getdata_cache'], 'fts')
    report_file_name = os.path.join(base_dir, "export_2009_en.xml")
    #recipients = load_report(loader, report_file_name)
    
    country_file_name = os.path.join(base_dir, "countries.csv")
    countries = load_countries(country_file_name)
    
    stat_file_name = os.path.join(base_dir, "teilm020.tsv")
    load_unemployment(stat_file_name, countries)
    
    stat_file_name = os.path.join(base_dir, "teiis080.tsv")
    load_industrial_production(stat_file_name, countries)
    
