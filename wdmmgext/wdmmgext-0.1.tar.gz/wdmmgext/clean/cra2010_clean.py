#############################################################
# Tidies up two CRA2010 Excel tables into a single csv file.
# Table 9 has regional breakdown, while table 10 has COFOG2 codes.
# This script combines them and deals with inconsistencies.
#############################################################
import csv
import xlrd
import copy

filename1 = "pesa_2010_database_tables_chapter9.xls"
filename2 = "pesa_2010_database_tables_chapter10.xls"

def tidy_and_decode(x):
    ''' 
    Clean up Excel rows. 
    '''
    return unicode(str(x).decode("mac_roman").strip())

def clean_region(region):
    '''
    Put region names in standard format expected by the Flash.
    Keys are CRA2010 region names, values are CRA2009 names.
    '''
    standard_names = { 
        'ENGLAND_Yorkshire and the Humber': 'ENGLAND_Yorkshire and The Humber',
        'Northern Ireland': 'NORTHERN IRELAND',
        'Not Identifiable': 'NON-IDENTIFIABLE',
        'Not identifiable': 'NON-IDENTIFIABLE',
        'Outside UK': 'OUTSIDE UK',
        'Scotland': 'SCOTLAND', 
        'Wales': 'WALES' }
    if region in standard_names:
        region = standard_names[region]
    return region

###############################################
# Load up original data.
###############################################
sheet9 = xlrd.open_workbook(filename=filename1)
table9 = sheet9.sheet_by_index(0)
entries9 = [] 

table10 = xlrd.open_workbook(filename=filename2)
table10 = table10.sheet_by_index(0)
entries10 = [] 

for row in range(0,table9.nrows):
    if row==0:
        continue
    else:      
        fields = {}
        fields['dept_code'] = tidy_and_decode(table9.cell(row,0).value)
        fields['dept_name'] = tidy_and_decode(table9.cell(row,1).value)
        fields['cofog_1'] = tidy_and_decode(table9.cell(row,2).value)
        fields['hmt_1'] = tidy_and_decode(table9.cell(row,3).value)
        fields['pog'] = tidy_and_decode(table9.cell(row,4).value)
        fields['pog_alias'] = tidy_and_decode(table9.cell(row,5).value)
        fields['id_or_non_id'] = tidy_and_decode(table9.cell(row,6).value)
        fields['cap_or_cur'] = tidy_and_decode(table9.cell(row,7).value)
        fields['cg_lg_or_pc'] = tidy_and_decode(table9.cell(row,8).value)
        fields['nuts_region']  = clean_region(tidy_and_decode(table9.cell(row,9).value))
        fields['spending_04_05'] = tidy_and_decode(table9.cell(row,10).value)
        fields['spending_05_06'] = tidy_and_decode(table9.cell(row,11).value)
        fields['spending_06_07'] = tidy_and_decode(table9.cell(row,12).value)
        fields['spending_07_08'] = tidy_and_decode(table9.cell(row,13).value)
        fields['spending_08_09'] = tidy_and_decode(table9.cell(row,14).value)
        fields['spending_09_10'] = tidy_and_decode(table9.cell(row,15).value)
        fields['spending_10_11'] = tidy_and_decode(table9.cell(row,16).value)
        entries9.append(fields)

for row in range(0,table10.nrows): 
    if row==0:
        continue
    else:   
        fields = {}   
        fields['dept_code'] = tidy_and_decode(table10.cell(row,0).value)
        fields['dept_name'] = tidy_and_decode(table10.cell(row,1).value)
        fields['cofog_1'] = tidy_and_decode(table10.cell(row,2).value)
        fields['hmt_1'] = tidy_and_decode(table10.cell(row,3).value)
        fields['cofog_2'] = tidy_and_decode(table10.cell(row,4).value)
        fields['hmt_2'] = tidy_and_decode(table10.cell(row,5).value)
        fields['pog'] = tidy_and_decode(table10.cell(row,6).value)
        fields['pog_alias'] = tidy_and_decode(table10.cell(row,7).value)
        fields['id_or_non_id'] = tidy_and_decode(table10.cell(row,8).value)
        fields['cap_or_cur'] = tidy_and_decode(table10.cell(row,9).value)
        fields['cg_lg_or_pc'] = tidy_and_decode(table10.cell(row,10).value)
        fields['nuts_region']  = clean_region(tidy_and_decode(table10.cell(row,11).value))
        fields['spending_04_05'] = tidy_and_decode(table10.cell(row,12).value)
        fields['spending_05_06'] = tidy_and_decode(table10.cell(row,13).value)
        fields['spending_06_07'] = tidy_and_decode(table10.cell(row,14).value)
        fields['spending_07_08'] = tidy_and_decode(table10.cell(row,15).value)
        fields['spending_08_09'] = tidy_and_decode(table10.cell(row,16).value)
        fields['spending_09_10'] = tidy_and_decode(table10.cell(row,17).value)
        entries10.append(fields)        

###############################################
# Compare each row & create lists 
# of matched and unmatched items.
###############################################
print "Number in Table 9: " + str(len(entries9))
print "Number in Table 10: " + str(len(entries10))

joint_items = [] 
unmatched_items_9 = list(entries9)
unmatched_items_10 = list(entries10)

for counter9,entry9 in enumerate(entries9):
    for counter10, entry10 in enumerate(entries10):
        if entry9['pog_alias'].lower()==entry10['pog_alias'].lower() \
        and entry9['cofog_1'].lower()==entry10['cofog_1'].lower() \
        and entry9['dept_name'].lower()==entry10['dept_name'].lower() \
        and entry9['spending_09_10']==entry10['spending_09_10'] \
        and entry9['spending_08_09']==entry10['spending_08_09'] \
        and entry9['spending_07_08']==entry10['spending_07_08'] \
        and entry9['spending_06_07']==entry10['spending_06_07'] \
        and entry9['spending_05_06']==entry10['spending_05_06'] \
        and entry9['spending_04_05']==entry10['spending_04_05'] \
        and entry9['nuts_region'][0:7]==entry10['nuts_region'][0:7]:
            joint_item = copy.deepcopy(entry9)
            joint_item['cofog_1'] = copy.deepcopy(entry10['cofog_1']) 
            joint_item['hmt_1'] = copy.deepcopy(entry10['hmt_1']) 
            joint_item['cofog_2'] = copy.deepcopy(entry10['cofog_2'])
            joint_item['hmt_2'] = copy.deepcopy(entry10['hmt_2'])
            joint_items.append(joint_item)
            unmatched_items_9.remove(entry9)
            unmatched_items_10.remove(entry10)
            entries10.remove(entry10)
            break

for item in unmatched_items_9:
    item['cofog_2'] = "LA data sub_function"
    item['hmt_2'] = "LA data sub_function"
for item in unmatched_items_10:
    item['spending_10_11'] = ""

###############################################
# Take all the ENG_LA items from Table 9
# and the ENG_HRA items with the POG mismatch.
###############################################
temp_items = []
for unmatched_item in unmatched_items_9:
    if unmatched_item['dept_name']=="ENG_LA" \
       or (unmatched_item['dept_name']=="ENG_HRA" and \
           unmatched_item['pog_alias']==\
           'LA dummy sprog 6. Housing and community amenities'):
        joint_items.append(unmatched_item)
    else: 
        temp_items.append(unmatched_item)
unmatched_items_9 = list(temp_items)

del temp_items[:]
for unmatched_item in unmatched_items_10:
    if unmatched_item['dept_name']!="ENG_LA" and \
       unmatched_item['pog_alias']!=\
        'LA dummy 6. Housing and community amenities':
        temp_items.append(unmatched_item)
unmatched_items_10 = list(temp_items)

print "Number of matched items found: " + str(len(joint_items))
print "Number unmatched from Table 9: " + str(len(unmatched_items_9))
print "Number unmatched from Table 10: " + str(len(unmatched_items_10))
    
# Check any remaining rows & fix by hand (I found 4 rows with typos).
# The Treasury says that Table 10's spending figures are the ones to 
# use in the case of mismatches.

#####################################
# Write matched items to csv.
#####################################
cleancsv = csv.writer(open('cra_2010.csv', 'wb'))

cleancsv.writerow(['Dept Code', 'Dept Name', 'COFOG Level 1', \
    'HMT Functional Classification', 'COFOG Level 2', \
    'HMT Sub-functional Classification', \
    'Programme Object Group', 'Programme Object Group Alias', \
    'ID or non-ID', 'CAP or CUR', 'CG, LG or PC', 'NUTS 1 region', \
    '2004-05', '2005-06', '2006-07', '2007-08', '2008-09', '2009-10', '2010-11'])

for joint_item in joint_items:
    row = [joint_item['dept_code'], joint_item['dept_name'], 
           joint_item['cofog_1'], joint_item['hmt_1'],
           joint_item['cofog_2'], joint_item['hmt_2'], joint_item['pog'],
           joint_item['pog_alias'], joint_item['id_or_non_id'], 
           joint_item['cap_or_cur'], joint_item['cg_lg_or_pc'], 
           joint_item['nuts_region'], joint_item['spending_04_05'], 
           joint_item['spending_05_06'], joint_item['spending_06_07'], 
           joint_item['spending_07_08'], joint_item['spending_08_09'], 
           joint_item['spending_09_10'], joint_item['spending_10_11']]
    cleancsv.writerow(row)

#####################################
# Write unmatched items to CSV.
#####################################
unmatched_9 = csv.writer(open('unmatched_table9.csv', 'wb'))
unmatched_10 = csv.writer(open('unmatched_table10.csv', 'wb'))

unmatched_9.writerow(['Dept Code', 'Dept Name', 'COFOG Level 1', 
    'HMT Functional Classification', 'Programme Object Group',  \
    'Programme Object Group Alias', 'ID or non-ID', 'CAP or CUR', \
    'CG, LG or PC', 'NUTS 1 region', '2004-05', '2005-06', '2006-07', \
    '2007-08', '2008-09', '2009-10', '2010-11'])

for unmatched_item in unmatched_items_9:
    row = [unmatched_item['dept_code'], unmatched_item['dept_name'], 
           unmatched_item['cofog_1'], unmatched_item['hmt_1'],
           unmatched_item['pog'], unmatched_item['pog_alias'],
           unmatched_item['id_or_non_id'], unmatched_item['cap_or_cur'], 
           unmatched_item['cg_lg_or_pc'], unmatched_item['nuts_region'],
           unmatched_item['spending_04_05'], 
           unmatched_item['spending_05_06'], 
           unmatched_item['spending_06_07'], 
           unmatched_item['spending_07_08'], 
           unmatched_item['spending_08_09'], 
           unmatched_item['spending_09_10'], 
           unmatched_item['spending_10_11']]
    unmatched_9.writerow(row)

unmatched_10.writerow(['Dept Code', 'Dept Name', 'COFOG Level 1', 
    'HMT Functional Classification', 'COFOG Level 2', \
    'HMT Sub-functional Classification', 'Programme Object Group',  \
    'Programme Object Group Alias', 'ID or non-ID', 'CAP or CUR', \
    'CG, LG or PC', 'NUTS 1 region', '2004-05', '2005-06', '2006-07', \
    '2007-08', '2008-09', '2009-10'])

for entry in unmatched_items_10:
    row = [entry['dept_code'], entry['dept_name'], entry['cofog_1'], 
           entry['hmt_1'], entry['cofog_2'], entry['hmt_2'], entry['pog'],
           entry['pog_alias'], entry['id_or_non_id'], entry['cap_or_cur'], 
           entry['cg_lg_or_pc'], entry['nuts_region'], 
           entry['spending_04_05'], entry['spending_05_06'],
           entry['spending_06_07'], entry['spending_07_08'],
           entry['spending_08_09'], entry['spending_09_10']]
    unmatched_10.writerow(row)