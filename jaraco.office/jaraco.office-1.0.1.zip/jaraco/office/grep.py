from win32com.client import Dispatch
from itertools import takewhile
import re

app = Dispatch('Excel.Application')
#wb = app.Workbooks.Open(filename)

default_pattern = 'Total'

def CleanRow(row):
	return filter(None, row.Value[0])

def HasPattern(row, pattern = default_pattern):
	strings = map(unicode, CleanRow(row))
	pattern = re.compile(pattern, re.I)
	return bool(filter(pattern.search, strings))

def NotHasPattern(row, pattern = default_pattern):
	return not HasPattern(row, pattern)

def IsNotBlank(row):
	return bool(CleanRow(row))

def IsBlank(row):
	return not IsNotBlank(row)

def DeleteUnmatchedRows():
	"""
	Delete rows that don't match the pattern; you'll have to run this
	multiple times if you want to get consecutive matches
	"""
	# excel doesn't support iteration
	#valueRows = takewhile(IsNotBlank, app.Rows)
	#map(DeleteRow, filter(NotHasPattern, valueRows))
	for row in GetPopulatedRows():
		if NotHasPattern(row):
			print 'deleting row', CleanRow(row)
			row.Delete()

def GetPopulatedRows():
	for row in app.Rows:
		if IsBlank(row): break
		yield row

def FixBlankWPNCD(row):
	if row.Cells(1,1).Value is None:
		app.Cells(row.Row, row.Column).Value = app.Cells(row.Row-1, row.Column).Value
