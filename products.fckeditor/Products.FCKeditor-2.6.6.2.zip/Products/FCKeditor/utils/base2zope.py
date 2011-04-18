# -*- coding: UTF-8 -*-
# Authors: 
#!/usr/bin/env python
#BOILERPLATE###################################################################
#                                                                             #
#  This package wraps FCKeditor for use in the Zope web application server.   #
#  Copyright (C) 2005 Chad Whitacre < http://www.zetadev.com/ >               #
#                                                                             #
#  This library is free software; you can redistribute it and/or modify it    #
#  under the terms of the GNU Lesser General Public License as published by   #
#  the Free Software Foundation; either version 2.1 of the License, or (at    #
#  your option) any later version.                                            #
#                                                                             #
#  This library is distributed in the hope that it will be useful, but        #
#  WITHOUT ANY WARRANTY; without even the implied warranty of                 #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser    #
#  General Public License for more details.                                   #
#                                                                             #
#  You should have received a copy of the GNU Lesser General Public License   #
#  along with this library; if not, write to the Free Software Foundation,    #
#  Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA                #
#                                                                             #
#                                                                             #
###################################################################BOILERPLATE#

""" This script takes the FCKeditor base distribution in ../src/ and massages it
for use in Zope, outputting to ../skins/fckeditor/. Usage:

    $ ./base2zope.py
    $

"""

import os
import re
import shutil
import sys
import codecs


##
# Initialize some variables.
##

PRODUCT_ROOT = os.path.realpath(os.path.join(sys.path[0],'..'))
SRC_ROOT     = os.path.join(PRODUCT_ROOT, '_src', 'fckeditor')
DEST_ROOT    = os.path.join(PRODUCT_ROOT, 'skins', 'fckeditor')
SRC_SKINS_ADDONS_ROOT = os.path.join(PRODUCT_ROOT, '_addons','skins')
DEST_SKINS_ADDONS_ROOT = os.path.join(PRODUCT_ROOT, 'skins','fckeditor','editor','skins')
SRC_PLUGINS_ADDONS_ROOT = os.path.join(PRODUCT_ROOT, '_addons','plugins')
DEST_PLUGINS_ADDONS_ROOT = os.path.join(PRODUCT_ROOT, 'skins','fckeditor','editor','plugins')


##
# Decide what to do if DEST_ROOT is already there.
##

def rm_rf(path):
    """ equivalent to rm -rf on Unix
    """
    if os.path.realpath(path) == '/':
        print 'will not rm -rf /' # better safe than sorry :-)
        sys.exit(1)
    else:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

if os.path.exists(DEST_ROOT):
    force = sys.argv[1:2] == ['--force']
    if not force:
        answer = raw_input( "destination directory already exists; " +\
                            "delete and recreate? (y/n) [n] "
                            )
        force = answer.lower() == 'y'
    if force:   rm_rf(DEST_ROOT)
    else:       sys.exit(1)
else:
    os.makedirs(DEST_ROOT)





METADATA = """\
[default]
cache = HTTPCache"""

def metadata(filepath):
    """Given a filepath, write a complementary metadata file.
    """
    mdpath = '.'.join((filepath, 'metadata'))
    mdfile = file(mdpath,'w+')
    mdfile.write(METADATA)
    mdfile.close()

cache_me  = ('css','gif','html','js','xml','swf')
ext_unwanted = ('asp','aspx','cfc','cfm','cgi','exe','htaccess','php','pl','lasso','afp')
# files overloaded in fckeditor_plone layer, or files which depends on "_source" folder (unavailable in a skin layer)
files_unwanted = ('fckconfig.js','fckeditor.py','fckstyles.xml.pt','fcktemplates.xml.pt','fckdebug.html.pt')
# files changed (impossible to overload because of subdirectories in original skins)
files_changed = {'fck_link.html.pt':{'ResourceType':'File'},'fck_image.html.pt':{'ResourceType':'Image'},'fck_flash.html.pt':{'ResourceType':'Flash'}}
files_with_xhtml_errors =['fck_paste.html.pt','fckdialog.html.pt','fck_image.html.pt','fck_flash.html.pt','w.html.pt','tmpFrameset.html.pt']


def makeSkinDirs(srcDir ,destDir):
  """
  Now walk the tree and transfer data to our output directory.
  """
  for path, dirs, files in os.walk(srcDir):
  
      # Determine and maybe create the destination.
      relpath = path[len(srcDir)+1:]
      destpath = os.path.join(destDir, relpath)
      if not os.path.exists(destpath):
          os.mkdir(destpath)
  
      for filename in files:
  
          src = os.path.join(path, filename)
  
          # Alter the output filename if necessary.
          ext = filename.split('.')[-1]
          if ext.lower() in ('html', 'xml', 'htc'):
              filename += '.pt'
          dest = os.path.join(destpath, filename)
  
          # Create the new file if we want it.
          if (not filename.startswith('_')) and (ext not in ext_unwanted) and (filename not in files_unwanted):                                                               
                          
              if files_changed.has_key(filename) :
  
                  # add Title + Description fields in upload forms
  
                  inputfile = file(src)
                  outputfile = file(dest, 'w+')
                  
                  resourceType = files_changed[filename]['ResourceType']
                  sizeLines = ''
                  if resourceType=='Image':
                    sizeLines='''
                                    			<span>Size</span>&nbsp;
                                    			<input type="radio" name="size" value="small" />small&nbsp;
                                    			<input type="radio" name="size" value="medium" checked />medium&nbsp;
                                    			<input type="radio" name="size" value="full"/>full&nbsp;<br />                    
                              '''
  
                  for line in inputfile.readlines():
                      if '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">' in line :
                         # add charset=utf8 headers to avoid encoding errors with file upload forms
                         outputfile.write(line)
                         outputfile.write('''<metal:block tal:define="dummy python:request.RESPONSE.setHeader('Content-Type', 'text/html;;charset=utf-8')" />\n''')
                      elif '<input id="txtUploadFile" ' in line :   
                         outputfile.write(line)
                         outputfile.write('''
                                    			<input type="hidden" name="Type" value="%s" />
                                          <span  fckLang="DlgGenTitle">Title</span><br />
                                    			<input id="Title" name="Title" style="WIDTH: 200px" type="text" /><br />%s
                                    			<span  fckLang="DlgDocMeDescr">Description</span><br />
                                    			<textarea id="Description" name="Description" rows="2" cols="30"></textarea>                       
                                          ''' %(resourceType, sizeLines))
                      else:
                         outputfile.write(line)
                          
                  inputfile.close()
                  outputfile.close()

              # reduce a big frame in WSC Spellchecker
              elif filename=='tmpFrameset.html.pt':
                  inputfile = file(src)
                  outputfile = file(dest, 'w+')
                  for line in inputfile.readlines():
                      if "parseInt( oParams.thirdframeh, 10 )" in line :
                          newline = '    sFramesetRows = "27,*," + ( parseInt( oParams.thirdframeh, 10 ) || "150" ) + ",0" ;\r'
                          outputfile.write(newline)                                
                      else:
                          outputfile.write(line)
                          
                  inputfile.close()
                  outputfile.close()

              # changes in fr.js (french traduction)
              elif filename=='fr.js':
                  inputfile = file(src)
                  outputfile = file(dest, 'w+')
                  for line in inputfile.readlines():
                      if "FontFormats" in line :
                          newline = 'FontFormats			:  "Paragraphe;Formaté;Adresse;Titre 1;Titre 2;Titre 3;Titre 4;Titre 5;Titre 6;Bloc (DIV)", \r'
                          outputfile.write(unicode(newline,"utf8").encode("utf8","strict"))                                
                      else:
                          outputfile.write(line)
                          
                  inputfile.close()
                  outputfile.close()


              # add FCKeditor.Plone About tab in fck_about dialog box
              elif filename=='fck_about.html.pt':
                  inputfile = file(src)
                  outputfile = file(dest, 'w+')
                  nbLine=0
                  for line in inputfile.readlines():
                      nbLine+=1
                      if nbLine<30 :
                          outputfile.write(line)
                      elif nbLine==30:
                          newScript='''
	<script type="text/javascript"
          tal:define="label_fckplone_about python:context.translate('label_fckplone_about', default='About FCKEditor.Plone', domain='fckeditor')"
          tal:content="structure string:
      var oEditor = window.parent.InnerDialogLoaded() ;
      var FCKLang	= oEditor.FCKLang ;      
      window.parent.AddTab( 'About', FCKLang.DlgAboutAboutTab ) ;
      window.parent.AddTab( 'License', FCKLang.DlgAboutLicenseTab ) ;
      window.parent.AddTab( 'PloneAbout', '$label_fckplone_about' ) ;
      window.parent.AddTab( 'BrowserInfo', FCKLang.DlgAboutBrowserInfoTab ) ;      
      // Function called when a dialog tag is selected.
      function OnDialogTabChange( tabCode )
      {
      	ShowE('divAbout', ( tabCode == 'About' ) ) ;
      	ShowE('divLicense', ( tabCode == 'License' ) ) ;
      	ShowE('divPloneAbout', ( tabCode == 'PloneAbout' ) ) ;
      	ShowE('divInfo'	, ( tabCode == 'BrowserInfo' ) ) ;
      }      
      function SendEMail()
      {
      	var eMail = 'mailto:' ;
      	eMail += 'fredck' ;
      	eMail += '@' ;
      	eMail += 'fckeditor' ;
      	eMail += '.' ;
      	eMail += 'net' ;      
      	window.location = eMail ;
      }      
      window.onload = function()
      {
      	// Translate the dialog box texts.
      	oEditor.FCKLanguageManager.TranslatePage(document) ;      
      	window.parent.SetAutoSize( true ) ;
      }
      
      ">
	</script>
'''    
                          outputfile.write(newScript)
                      elif nbLine>=68 and nbLine<136 :    
                          outputfile.write(line)
                      elif nbLine==136 :        
                          newDiv = '''
	<div id="divPloneAbout" 
       style="display: none"
       i18n:domain="fckeditor">
		<table cellpadding="0" cellspacing="0" border="0">
			<tr>
				<td align="center">
          <br />
          <span i18n:translate="description_fckplone_about"
                style="font-size: 12px" dir="ltr">
                The FCKeditor.Plone product is developped under the GNU General Public License.<br/>
                Copyright (C)2007 Ingeniweb
          </span>      
				</td>
			</tr>
			<tr>
				<td align="center">
				  <br/>
					<span style="font-size: 12px" dir="ltr">
					<span fcklang="DlgAboutInfo">For further information go to</span> <a href="http://www.ingeniweb.com"
						target="_blank">http://www.ingeniweb.com/</a>.
				</td>
			</tr>
			<tr>
				<td align="center"
            tal:define="portal_url here/portal_url">
          <br /> 
					<a href="http://www.ingeniweb.com"
					   target="_blank">
            <img alt="" 
                 style="border:none !important;"
    				     tal:attributes="src string:$portal_url/ingeniweb_powered.png"
                 src="ingeniweb_powered.png" />
          </a>     
				</td>
			</tr>
		</table>
	</div>
'''
                          outputfile.write(newDiv)
                          outputfile.write(line)
                      elif nbLine > 130 :
                          outputfile.write(line)    

                  inputfile.close()
                  outputfile.close()        
  
              else:
                  shutil.copy(src, dest)
                  
              #remove BOM, a known bug on some fckeditor versions (ex: http://sourceforge.net/tracker/index.php?func=detail&aid=1685547&group_id=75348&atid=543653)
              if filename.endswith('.html.pt'):
                  fileObj = codecs.open( dest, "r", "utf-8" ) 
                  u = fileObj.read()   
                  fileObj.close()                        
                  if u.startswith( unicode( codecs.BOM_UTF8, "utf8" ) ) :      
                     fileObj = codecs.open( dest, "w", "utf-8" )
                     fileObj.write(u.lstrip(unicode( codecs.BOM_UTF8, "utf8" )))       
                     fileObj.close()
              
              # some specific errors which generate zpt compilation error
              # TODO regexp to fix these errors
              if filename in files_with_xhtml_errors :
                  fileObj = file(dest) 
                  content = fileObj.read()   
                  fileObj.close()  
                  content = content.replace('</$1>','<\/$1>')
                  content = content.replace("</iframe>'","<\/iframe>'")
                  content = content.replace("</div><p>","<\/div><p>")
                  content = content.replace("'</p>'","'<\/p>'")
                  content = content.replace('<font> tags','<font\/> tags') 
                  content = content.replace('></frame>',' />')   
                  fileObj = file(dest,"w")
                  fileObj.write(content)
                  fileObj.close()                  
              
              if ext in cache_me:
                  metadata(dest)
  
      # skip svn directories
      if '.svn' in dirs:
          dirs.remove('.svn')
  
      # also skip extra FCKeditor directories
      for dirname in dirs[:]:
          if dirname.startswith('_'):
              dirs.remove(dirname)
          #filemanager is Zope specific (in fckeditorplone layer)   
          #directory removed 
          elif dirname == 'filemanager':
              dirs.remove(dirname)

#Add base skin directory
makeSkinDirs(SRC_ROOT ,DEST_ROOT)
# Add new skins and plugins
# temporary removed since new skins are not compatibles
# makeSkinDirs(SRC_SKINS_ADDONS_ROOT,DEST_SKINS_ADDONS_ROOT)
makeSkinDirs(SRC_PLUGINS_ADDONS_ROOT,DEST_PLUGINS_ADDONS_ROOT)
