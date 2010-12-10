'''tabola - XLS Support.'''

import cStringIO

import xlrd
import xlwt

import tabola.core

title = 'xls'
extensions = ('xls',)

def export_set(dataset):
    '''Returns XLS representation of Dataset.'''
    wb = xlwt.Workbook(encoding='utf8')
    ws = wb.add_sheet(dataset.title if dataset.title else 'Tabbed Dataset')
    for i, row in enumerate(dataset._package(False)):
        for j, col in enumerate(row): ws.write(i, j, col)
    stream = cStringIO.StringIO()
    wb.save(stream)
    return stream.getvalue()

def export_book(databook):
    '''Returns XLS representation of DataBook.'''
    wb = xlwt.Workbook(encoding='utf8')
    for i, dset in enumerate(databook._datasets):
        ws = wb.add_sheet(dset.title if dset.title else 'Sheet%s' % (i))
        for i, row in enumerate(dset._package(False)):
            for j, col in enumerate(row): ws.write(i, j, col)
    stream = cStringIO.StringIO()
    wb.save(stream)
    return stream.getvalue()

def import_set(dset, sheet, headers=True):
    '''Returns dataset from CSV stream.'''
    dset.clear()
    dset.title = sheet.name
    for row in xrange(sheet.nrows):
        new_row = list()
        for col in xrange(sheet.ncols):
            new_row.append(sheet.cell_value(row, col))
        if row == 0 and headers:
            dset.headers = new_row
        else:
            dset.append_row(new_row)
    
def import_book(databook, in_stream, headers=True):
    '''Returns dataset from CSV stream.'''
    databook.clear()
    wb = xlrd.open_workbook(file_contents=in_stream)
    for sheet in wb.sheets():
        dataset = tabola.core.Dataset()
        dataset.title = sheet.name
        for row in xrange(sheet.nrows):
            new_row = list()
            for col in xrange(sheet.ncols):
                new_row.append(sheet.cell_value(row, col))
            if row == 0 and headers:
                dataset.headers = new_row
            else:
                dataset.append_row(new_row)
        databook.append_dataset(dataset)