#! /usr/bin/env python

# DocUp.py- a script that uses Markdown to make HTML 4 files from plaintext
# files in Markdown format and zip them up for uploading to pypi.
#
# See the Readme for pre-requisites and install info.
#
# Author: Anthony Darius Bashi
# email: bashia@uvic.ca

import sys
import os
import socket
import httplib
import base64
import urlparse
import tempfile
import cStringIO as StringIO

from distutils import log
from distutils.errors import DistutilsOptionError
from ConfigParser import ConfigParser

def getcreds():
	option = ''
	if "[pypi]" in open(os.path.expanduser('~/.pypirc')).read():
		option = 'pypi'
	if "[server-login]" in open(os.path.expanduser('~/.pypirc')).read():
		option = 'server-login'

	config = ConfigParser()
	config.readfp(open(os.path.expanduser('~/.pypirc')))
	creds = [config.get(option,'username'),config.get(option,'password')]
	if option == '':
		print "Something went wrong in getting pypi user credentials"
		return
	return creds

def readargs():						# readargs gets all the command-line
	if (len(sys.argv) > 5) or (len(sys.argv) < 3):	# arguments and returns them in a list.
		print "Usage: DocUp <FILE1>[,FILE2,...] <project-name> [--creds username:password]"	# More command-line args
	else:											# may be added in the future.
		return sys.argv[1:]
	
def markdir(target):					# markdir recursively goes through a directory tree
	for item in os.listdir(target):			# rooted at target, converting any file with a .txt
		fullpath = target + "/"+ item		# extension to html using markdown and deletes the original
		if "txt" in item:
			tohtml = "markdown " + fullpath + " -f " + target + "/" + item.split(".")[0] + ".html -q"
			os.system(tohtml)
			cleanup = "rm " + fullpath
			os.system(cleanup)

		if os.path.isdir(fullpath):
			markdir(fullpath)

def dirhandle(target, tempdir):				# dirhandle copies the contents of the specified directory into
	for f in os.listdir(target):			# the temporary directory for zippage and uploading.
		movement = "cp -r " + target + "/* " + tempdir
		os.system(movement)
	markdir(tempdir)
	return tempdir

def getfnames():					# getfnames returns a list of the filenames
	try:						# given in the command-line arguments
		return readargs()[0].split(",")
	except TypeError:
		return

def downmark(filename, tempdir):			# downmark uses markdown on a file filename
	cond = ""					# and puts the results into an html file of
	if (filename[0]=="-"):				# the same name in the temporary directory
		cond = "--"

	newfilename = filename.split(".")[0] + ".html"

	if (len(sys.argv[1].split(",")) == 1):
		newfilename = "index.html"

	formatting = "markdown " + cond + " " + filename + " -o html4" + " >> " + tempdir + "/" + newfilename

	os.system(formatting)

	return newfilename				# downmark returns the name of the new html file for use by other functions

def fileops(tempdir):					# fileops performs the file and directory movement and deletion
							# necessary before anything can be zipped
	a = len(getfnames())
	try:		
		for phile in getfnames():		# This downmarks all the files in the comma-seperated field in the
				if not os.path.isfile(os.path.abspath(phile)):
					a = a - 1
					print "'" + phile + "'" + " is not a valid file/directory."
					continue
				if a == 0:
					return 0
				downmark(phile, tempdir)# command-line arguments, moving them all to the temp directory	
	except TypeError:
		return 0				# This assumes that all files are in markdown format

def zipify(tempdir):					# zipify zips the temp file's contents into a .zip 
	if len(os.listdir(tempdir)) == 0:
		return
	try:						# named after the project it is destined for.
		archname = sys.argv[2]
		origdir = os.getcwd()
		zipdir = "cd " + tempdir + ";" + " zip -r -q " + archname + " *"
		os.system(zipdir)
		return tempdir + "/" + archname
	except IndexError:
		print "Usage: DocUp <FILE1>[,FILE2,...] <project-name> [--creds username:password]"
		return

def upload(filename, username, password):		# upload uploads file filename to pypi under 
	if type(filename) != str:			# project projname as user username with
		return					# password password.
	if os.path.isfile(os.path.abspath(filename + ".zip")):
		content = open(filename + ".zip",'rb').read()	
	else:
		return					# Thanks to the Sphinx-PyPI-upload project for a lot of this function.
	projname = sys.argv[2]				# Find them here: http://pypi.python.org/pypi/Sphinx-PyPI-upload/0.2.1
	data = {
	    ':action': 'doc_upload',
	    'name': projname,
	    'content': (os.path.basename(filename),content),
	}
	# set up the authentication
	auth = "Basic " + base64.encodestring(username + ":" + password).strip()

	# Build up the MIME payload for the POST data
	boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
	sep_boundary = '\n--' + boundary
	end_boundary = sep_boundary + '--'
	body = StringIO.StringIO()
	for key, value in data.items():
	    # handle multiple entries for the same name
	    if type(value) != type([]):						
		value = [value]							
	    for value in value:
		if type(value) is tuple:
		    fn = ';filename="%s"' % value[0]
		    value = value[1]
		else:
		    fn = ""
		value = str(value)
		body.write(sep_boundary)
		body.write('\nContent-Disposition: form-data; name="%s"'%key)
		body.write(fn)
		body.write("\n\n")
		body.write(value)
		if value and value[-1] == '\r':
		    body.write('\n')  # write an extra newline (lurve Macs)
	body.write(end_boundary)
	body.write("\n")
	body = body.getvalue()

	# build the Request
	http = httplib.HTTPConnection("pypi.python.org")

	data = ''
	loglevel = log.INFO
	try:
		http.connect()
		http.putrequest("POST", "http://pypi.python.org/pypi")
		http.putheader('Content-type',
				   'multipart/form-data; boundary=%s'%boundary)
		http.putheader('Content-length', str(len(body)))
		http.putheader('Authorization', auth)
		http.endheaders()
		http.send(body)
		errcode = http.getresponse().status
		if errcode == 403:
			print "Error! You either cannot edit '" + projname + "' or it does not exist.\nCheck your credentials or the project name and try again."
		if errcode == 401:
			print "Error! The wrong password was provided to pypi.\nCheck ~/.pypirc or your command-line arguments and try again."
	except socket.error, e:
		print "Upload failed."
		return

def confirmsuccess(tempdir,projname):	#This will compare the local index.html and the one on pypi. This is rough- Refine it
	os.system("curl http://packages.pypi.org/" + projname + "/ >> " + tempdir + "/" + "test.html")
	

def main():

	tempdir = tempfile.mkdtemp()			# Make a temporary directory in which to consolidate the html files
	if "--creds" not in sys.argv:
		try:
			username,password = getcreds()	# Get user details
		except IOError:
			print "No .pypirc file found. Try entering your credentials manually or registering with pypi."
			return
	else:
		try:
			username,password = sys.argv[4].split(":")
		except IndexError:
			print "Usage: DocUp <FILE1>[,FILE2,...] <project-name> [--creds username:password]"
			return
	try:
		if os.path.isdir(getfnames()[0]):		# This allows for directories to be markeddown
			abspath = os.path.abspath(getfnames()[0])
			dirhandle(abspath,tempdir)
		else:
			if fileops(tempdir) == 0:
				return			# Consolodate files into one zip archive	
	except TypeError:
		return
	upload(zipify(tempdir),username,password)	# Upload the zip file
	cleanup = "rm -rf " + tempdir
	os.system(cleanup)				# Delete the temporary directory
	

if __name__ == "__main__":
    main()
