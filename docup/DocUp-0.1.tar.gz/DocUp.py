#! /usr/bin/env python

# DocUp.py- a script that uses Markdown to make HTML 4 files from plaintext
# files in Markdown format and zip them up for uploading to pypi.
#
# See the Readme for pre-requisites and install info.
#
# In the future, support will be added for multiple files and automatic
# uploading to pypi.
#
# Author: Anthony Darius Bashi
# email: bashia@uvic.ca

import sys
import os
import socket
import httplib
import base64
import urlparse
import cStringIO as StringIO

from distutils import log
#from distutils.command.upload import upload
from distutils.errors import DistutilsOptionError

def readargs():				# readargs gets all the command-line
	if (len(sys.argv) < 4):		# arguments and returns them in a list.
		print "Usage: DocUp [FILE1,FILE2,...] <project-name> username:password"	# More command-line args
	else:								# may be added in the future.
		return sys.argv[1:]
	

def getfiles():				# getfiles returns a list of the filenames
	try:
		return readargs()[0].split(",")	# given in the command-line arguments
	except TypeError:
		return

def downmark(filename):		# downmark uses markdown on a file filename
	cond = ""		# and, with some mild trickery,
	if (filename[0]=="-"):	# results in an html file with the same name
		cond = "--"	# minus the original extension plus '.html'

	newfilename = filename.split(".")[0] + ".html"

	formatting = "markdown " + cond + " " + filename + " -o html4" + " >> " + newfilename

	os.system(formatting)

	return newfilename	# downmark returns the name of the new html file for use by other functions


def movefile(filename):			# movefile simply moves file filename to /tmp/smoooog for zipping
	formatted = "mv " + filename + " /tmp/smoooog"

	os.system(formatted)

def fileops():				# fileops performs the file and directory movement and deletion
					# necessary before anything can be zipped
	os.system("rm -rf /tmp/smoooog")	#Removes any previous smoooogs that might get in the way
	os.system("mkdir /tmp/smoooog")
	try:		
		for phile in getfiles():		#This moves all the files that downmark has converted to /tmp/smoooog
			movefile(downmark(phile))
	except TypeError:
		return

def zipify():				# zipify zips /tmp/smoooog's contents into a .zip file named in the
	try:				# arguments and moves the .zip file to the user's working directory.
		archname = sys.argv[2]
		origdir = os.getcwd()
		zipdir = "cd /tmp/smoooog;" + " zip -r -q " + archname + " *" + "; mv " + archname + ".zip " + origdir
		os.system(zipdir)
		return archname
	except IndexError:
		return

def upload(filename, username, password):		# upload uploads file filename to pypi under 
	if type(filename) != str:			# project projname as user username with
		return					# password password.
        content = open(filename + ".zip",'rb').read()
        projname = sys.argv[2]
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
            if type(value) != type([]):						# I communized the bulk of this function from
                value = [value]							# Sphinx-PyPI-upload. See license details.
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
        except socket.error, e:
            return
	

def main():
	try:
		username = sys.argv[3].split(":")[0]	# Get user details
		password = sys.argv[3].split(":")[1]	
	except IndexError:
		print "Usage: DocUp [FILE1,FILE2,...] <project-name> username:password"
		return
	fileops()				# Consolodate files into one zip archive	
	upload(zipify(),username,password)	# Upload the zip file
	cleanup = "rm " + sys.argv[2] + ".zip"
	os.system(cleanup)			# Delete the zip archive
	

if __name__ == "__main__":
    main()
