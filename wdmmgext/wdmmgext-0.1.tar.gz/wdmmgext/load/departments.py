# Import all departmental spending files, one at a time.
# Identify department and subunit (if any) from filename.
import csv
from datetime import date
import glob
import os
import re
import sys
import time
import xlrd
import urllib2
import util

from pylons import config
import wdmmg.model as model
from wdmmg.model import Dataset, Entry, Entity, Classifier
from wdmmg.lib import loader

DATASET_NAME = u'departments'
SCHEME = u'departments'

dataset_long_name = u'UK central government department spending over 25,000' 
dataset_currency = u'gbp'
dataset_notes = u'UK central government department spending over 25,000'
names_root = util.Node('')

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    
    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)

def load_file(filepath, department, subunit, department_loader):
    '''
    Loads a file into a dataset with name 'departments'.
    - filepath - name of file to load  
    - department - which department's spending it is
    - subunit - sub-unit within that department
    '''
    def describe_key(key, label, description=None):
        Entry.describe_key(key, label, context=DATASET_NAME, description=description)
    # Semaphore to prevent the data being loaded twice.
    # We check by filename, not dataset as in other loaders.
    filename = unicode(filepath.split("/")[-1])
    describe_key(u'filename', 'Filename', description=u'''\
Name of data spending file.''')

    describe_key(u'from', 'Paid by', description=u'''\
The entity that the money was paid from.''')
    describe_key(u'to', "Paid to", description=u'''\
The entity that the money was paid to.''')
    describe_key(u'time', "Time", description=u'''\
The accounting period in which the spending happened.''')
    describe_key(u'row_id', "Row ID", description=u'''\
Row number within the file.''')
    describe_key(u'sub_unit', "Sub-unit", description=u'''\
Department sub-unit.''')
    describe_key(u'dept_family', "Dept family", description=u'''\
Department family.''')
    describe_key(u'dept_entity', "Dept entity", description=u'''\
Department entity.''')
    describe_key(u'expense_type', "Expense type", description=u'''\
Expense type.''')
    describe_key(u'expense_area', "Expense area", description=u'''\
Expense area.''')
    describe_key(u'transaction_number', "Transaction number", description=u'''\
Departmental transaction number.''')
    describe_key(u'description', "Internal description", description=u'''\
Internal description.''')
    describe_key(u'vat_number', "VAT number", description=u'''\
VAT registration number.''')
    describe_key(u'notes', "Notes", description=u'''\
Any additional notes from the department.''')

    department_entity = department_loader.create_entity(name=unicode(slugify(department)), 
        label = department,
        description = department
        )

    items = []
    is_csv = True
    # Some 'csv' files are actually Excel, deal with this.
    # Skip any blank rows at the beginning of fhe file.
    try:
        reader = csv.reader(open(filepath, "rU"))
        header = reader.next()
        while not [word for word in header if 'amount' in word.lower()]:
            header = reader.next()
    except csv.Error, e:
        print 'CSV error, not opening: %s' % e
        return 1
        # In case these spreadsheets don't get fixed, dummy loading code.
        is_csv = False
        book = xlrd.open_workbook(filename=filepath)
        sheet = book.sheet_by_index(0)
        header = [sheet.cell(0,col).value.strip() for col in range(0,sheet.ncols)]
        header_row = 0
        while not [word for word in header if 'amount' in word.lower()]:
            header_row += 1
            header = [sheet.cell(header_row,col).value.strip() for col in range(0,sheet.ncols)]
    # Tidy up and print the header.
    header = [h.lower() for h in header]
    header = [h.replace("_", " ") for h in header]
    print header
    def find_idx(matchword, required=False):
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
    try:
        date_index = find_idx('date',required=True)
        supplier_index = find_idx('supplier',required=True)
        amount_index = find_idx('amount',required=True)
    except Exception, e:
        return 0
    # TODO: tidy this up.
    try:
        dept_family_index = find_idx('family',required=False)
    except IndexError, e:
        dept_family_index = None
    try:
        entity_index = find_idx('entity',required=False)
    except IndexError, e:
        entity_index = None
    try:
        description_index = [ i for i, word in enumerate(header) \
                       if 'description' in word \
                       or 'narrative' in word][0]
    except IndexError, e:
        description_index = None
    try:
        vat_index = find_idx('vat',required=False)
    except IndexError, e:
        vat_index = None
    try:
        transaction_index = [ i for i, word in enumerate(header) \
                       if 'transaction' in word \
                       or 'transation' in word][0]
    except IndexError, e:
        transaction_index = None
    try:
        expense_type_index = find_idx('expense type',required=False)
    except IndexError, e:
        expense_type_index = None
    try:
        expense_area_index = find_idx('expense area',required=False)
    except IndexError, e:
        expense_area_index = None
    count = 0
    for row_index, row in enumerate(reader):
    #for row_index in range(header_row+1,sheet.nrows):
         #row = [sheet.cell(row_index,col).value for col in range(0,sheet.ncols)]
         row = [unicode(r.decode("mac_roman").strip()) for r in row]
         print row
         if not row:
             continue
         # Don't assume that ordering or wording is standard. 
         # Report any files that are missing standard columns. Skip blank columns.
         if (len(row) < 3) or (not row[0] and not row[1]):
             continue
         try:
             date = row[date_index]
             supplier_value = row[supplier_index]
             amount = util.to_float(row[amount_index].replace(u'\u00A3',''))
             # Make Entity for supplier.
             supplier_entity = department_loader.create_entity(name=unicode(slugify(supplier_value)), 
                label = supplier_value,
                description = supplier_value
                )
             if not supplier_value and date and amount:
                 continue
         except IndexError:
             print 'WARNING! Row missing standard entry in %s' % filename
             print row
             break
         # Convert date from Excel serial format if necessary.
         if date.isdigit():
             date = xlrd.xldate_as_tuple(int(date),0)
             date = '%s/%s/%s' % (date[2], date[1], date[0])
         # Also load optional columns if present. TODO: tidy this up.
         if description_index is not None:
             description_value = row[description_index]
         else:
             description_value = None   
         if vat_index is not None:
             try:
                 vat_number_value = row[vat_index]
             except IndexError: 
                 vat_number_value = None
         else:
             vat_number_value = None
         if dept_family_index is not None:
             department_family_value = row[dept_family_index]
         else:
             department_family_value = None
         if entity_index is not None:
             entity_value = row[entity_index]
         else:
             entity_value = None
         if expense_type_index is not None:
             expense_type_value = row[expense_type_index]
         else:
             expense_type_value = None
         if expense_area_index is not None:
             expense_area_value = row[expense_area_index]
         else:
             expense_area_value = None
         if transaction_index is not None:
             transaction_number_value = row[transaction_index]
         else:
             transaction_number_value = None   
         row_id_value = row_index + 1

         ex = {
             'name': DATASET_NAME + '-r' + str(row_id_value),
             'from': department_entity.to_ref_dict(),
             'to': supplier_entity.to_ref_dict(),
             'time': unicode(date),
             'department_family': department_family_value,
             'transaction_number': transaction_number_value,
             'dept_entity': entity_value,
             'row_id': row_id_value,
             'filename': filename,
             'sub_unit': subunit,
             'vat_number': vat_number_value,
             'notes': description_value,
             'expense_type': expense_type_value,
             'expense_area': expense_area_value
             }

         e = department_loader.create_entry(amount, **ex)
         count += 1

    print count
    return count






dept_dictionary = { 
'A': 'Administration',
'AGO': 'Attorney General\'s Office',
'BIS': 'Department for Business, Innovation and Skills',
'CLG': 'Department for Communities and Local Government',
'CO': 'Cabinet Office',
'COI': 'Central Office of Information',
'CPS': 'Crown Prosecution Service',
'DCMS': 'Department for Culture, Media and Sport',
'DECC': 'Department for Energy & Climate Change',
'DEFRA': 'Department of the Environment, Food & Rural Affairs',
'DFE': 'Department for Education',
'DFT': 'Department for Transport',
'DH': 'Department of Health',
'DWP': 'Department for Work and Pensions',
'DfID': 'Department for International Development',
'GEO': 'Government Equalities Office',
'HMRC': 'HM Revenue & Customs',
'HMT': 'HM Treasury',
'HO': 'Home Office',
'HSE': 'Health & Safety Executive',
'MOD': 'Ministry of Defence',
'MoJ': 'Ministry of Justice',
'NIO': 'Northern Ireland Office',
'NOMS': 'National Offender Management Service',
'NSG': 'National School of Government',
'OAG': 'Office of the Advocate-General',
'UKTI-A': 'UK Trade & Industry - Administration',
'UKTI-P': 'UK Trade & Industry - Programme',
'Probation': 'Probation Trusts',
'SO': 'Scotland Office',
'TSol': 'Treasury Solicitor\'s Department',
'WO': 'Wales Office',
}

def not_duplicate(filename, spending_files):
    '''
    Some departments have issued sheets with and without descriptive notes.
    We should always use the versions with descriptive notes, if they exist.
    For a given file, check whether there is another, more descriptive versions.
    '''
    if 'with-descriptions-' in filename:
        return True
    test_filename = filename.replace("Spend-Transactions-","Spend-Transactions-with-descriptions-")
    if test_filename in spending_files:
        return False
    return True

def get_department(filename):
    '''
    Use filename codes to find the full department name.
    '''
    filename = filename.split("/")[-1]
    filename = filename.replace("Spend-Transactions-with-descriptions-","")
    filename = filename.replace("Spend-Transactions-","")
    parts = filename.split("-")
    try: 
        dept_name = dept_dictionary[parts[0]]
        dept_subcode = parts[1]
        if dept_subcode.isdigit():
            subunit = "Central department"
        else:
            # Handle UKTI's various subunits as a special case.
            if dept_subcode=="UKTI":
                dept_subcode = parts[1] + "-" + parts[2]
            subunit = dept_dictionary[dept_subcode]
    except: 
        raise RuntimeError('Filename %s not mapped in departmental names' % filename)
    return dept_name, subunit

def load(*args):
    starttime = time.time()
    path = os.path.join(config['getdata_cache'], 'departments')
    if not os.path.exists(path):
        assert len(args) >= 1, 'You need to supply a url to retrieve from'
        retrieve(args[0], path)
    total = 0
    spending_files = sorted(glob.glob(os.path.join(path, '*.csv')))
    # If dataset does not already exist...
    # Make a suitably configured Loader (this also creates the Dataset).
    #if not model.Dataset.find({ 'name': DATASET_NAME}):
    department_loader = loader.Loader(DATASET_NAME, dataset_long_name,
            dataset_currency, dataset_notes)
    for spending_file in spending_files:
        print "=== Looking at file %s" % spending_file
        # Don't load files with and without descriptions twice.
        if not_duplicate(spending_file, spending_files):
            #spending_file = 'Spend-Transactions-AGO-TSol-09-Sep-2010.csv'
            dept_name, subunit = get_department(spending_file)
            filepath = os.path.join(path, spending_file)
            count = load_file(unicode(filepath), unicode(dept_name), unicode(subunit), department_loader)
            total += count
            elapsed = time.time() - starttime
            print('*** Total: %s (%ss) (last file: %s)' % (total, elapsed, count))
        else:
            print('Skipping file %s as there is another version with notes.') % (spending_file)
    
def retrieve(index_url, basepath):
    '''
    Get all CSV spending files.
    '''
    from BeautifulSoup import BeautifulSoup, SoupStrainer
    if not os.path.exists(basepath):
        os.makedirs(basepath)

    page = urllib2.urlopen(index_url)

    for link in BeautifulSoup(page, parseOnlyThese=SoupStrainer('a')):
        if link.has_key('href') and link['href'][-4:]==".csv":
            url = link['href']
            try:
                f = urllib2.urlopen(url)
                file_name = url.split("/")[-1]
                file_path = os.path.join(basepath, file_name)
                print "Downloading file %s to %s" % (file_name, file_path)
                local_file = open(file_path, "wb")
                try:
                    local_file.write(f.read())
                finally:
                    local_file.close()
            #handle errors
            except urllib2.HTTPError, e:
                print "HTTP Error:",e.code, url
            except urllib2.URLError, e:
                print "URL Error:", e.reason, url

