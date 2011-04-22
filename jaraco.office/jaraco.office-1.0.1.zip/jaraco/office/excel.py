
def sheet_as_dict(worksheet):
	"""
	Take an xsrd worksheet and convert it to a dict, using the first
	row as a header (to create keys for the subsequent rows).
	"""
	keys = worksheet.row_values(0)
	value_range = range(1, worksheet.nrows)
	to_dict = lambda values: dict(zip(keys, values))
	return [
		to_dict(worksheet.row_values(n))
		for n in value_range
		]
