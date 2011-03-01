import zipfile

def change_zip(filename):
	package = zipfile.ZipFile(filename,"r")
	return package

if "__main__"==__name__:
	import sys
	p = change_zip(sys.argv[1])
