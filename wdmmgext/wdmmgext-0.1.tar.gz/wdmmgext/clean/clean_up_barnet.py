# -*- coding: UTF-8 -*-
''' 
Clean up the Barnet data. Does two important things: 
- Gets rid of aggregate rows in the file
- Converts payment amounts into a standard format
'''

import csv, string, xlrd
from itertools import groupby

def to_float(number):
    ''' Just convert everything to floats '''
    if not number:
        return 0.0
    return float(number.replace(',', ''))

def clean_up_amount(barnet_amount):
    ''' Clean up the £k/m figures that Barnet provided '''
    barnet_amount = barnet_amount.replace("U+00A3","")
    barnet_amount = filter(lambda x: x in string.printable, barnet_amount)
    if barnet_amount[-1].lower() == 'm':
        barnet_amount = to_float(barnet_amount[:-1])
        barnet_amount = barnet_amount*1e6
    elif barnet_amount[-1].lower() == 'k': 
        barnet_amount = to_float(barnet_amount[:-1])
        barnet_amount = barnet_amount*1e3
    else:
        barnet_amount = to_float(barnet_amount)   
    return str(barnet_amount)

filename = 'barnet_exampledata_v3.xls'
spreadsheet = xlrd.open_workbook(filename=filename)
table = spreadsheet.sheet_by_index(0)

level_1 = ''
level_2 = ''
level_3 = ''
items = []

for row in range(0, table.nrows):
    # ignore header row
    if row == 0:
        continue
    else:
        temp_array = []
        for col in range(table.ncols):
            x = table.cell_value(row, col)
            temp_array.append(x.strip())
        if len(temp_array) == 0:
            continue
        if temp_array[0] != '': 
            level_1 = temp_array[0]
            level_2 = ''
        elif temp_array[1] != '':
            level_2 = temp_array[1]
        else:
            assert "blank row"
        level_3 = ''
        amount = temp_array[3]
        if amount != "":
            amount = clean_up_amount(amount)
        else:
            continue
        description = temp_array[4]
        item = [level_1, level_2, level_3, amount, description]
        items.append(item)

print items
items_to_remove = []

# find aggregate rows and remove them
for i in range(len(items)):
    i -= 1
    if items[i]:
        if items[i][1] == "":
            for other_item in items:
                if items[i][0] == other_item[0] and other_item[1] != "":
                    items_to_remove.append(i)
                    continue
        elif items[i][2] == "":
            for other_item in items:
                if items[i][1] == other_item[1] and other_item[2] != "":
                    items_to_remove.append(i)
                    continue

new_items = [ key for key, _ in groupby(items_to_remove)]
new_items.sort(reverse=True)  
for number in new_items:
    temp_item = items[number]
    items.remove(temp_item)

# now write everything to a new csv file
cleancsv = csv.writer(open('barnet_clean.csv', 'wb'))
cleancsv.writerow(['Level 1', 'Level 2', 'Level 3', 'Amount', \
                   'Detailed Description'])

for item in items:
    item = [x.encode('mac_roman') for x in item]
    cleancsv.writerow(item)