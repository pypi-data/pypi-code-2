import os
from os.path import basename, join, isfile
from Globals import DTMLFile
from cStringIO import StringIO

myPermission = 'Do QuickImport'

max_limit_zexp_size = 100000000 # change here as you like

addForm = DTMLFile('dtml/quickImporterForm', globals())

def _getImportFileFullPath(filename):
	return join( INSTANCE_HOME, 'import', filename)

def _deleteFileInImportDirectory(filename):
	""" use with care! """
	deletefilepath = _getImportFileFullPath(filename)
	if isfile(deletefilepath):
		os.remove(deletefilepath)

def _writeFileInImportDirectory(file, filename=None):
	if not filename:
		filename = basename(file.filename)
	writefilepath = _getImportFileFullPath(filename)
	writefile = open(writefilepath, "wb")
	writefile.write(file.read())
	writefile.close()

def _getFileSize(file):
	pos = file.tell()
	file.seek(0,2)
	filesize = file.tell()
	file.seek(pos)
	return filesize

def manage_doQuickImport(self, file, set_owner=0, leave=0, REQUEST=None):
	""" do quick import """
	origfilename = basename(file.filename)
	filesize = _getFileSize(file)
	if filesize > max_limit_zexp_size:
		return 'over max size %i.\n' %(max_limit_zexp_size)
	if leave:
		savefilename = origfilename
	else:
		savefilename = 'qi_tmp_' + origfilename
	_writeFileInImportDirectory(file, savefilename)
	self.manage_importObject(file=savefilename, set_owner=set_owner)
	if not leave:
		_deleteFileInImportDirectory(savefilename)
	if REQUEST:
		return self.manage_main(self, REQUEST)
