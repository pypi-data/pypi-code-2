# py2exe setup program
from distutils.core import setup
import py2exe
import sys
import os
import glob, shutil
import game.common
import pygame
import glob
import zipfile

sys.argv.append("py2exe")
 
VERSION = game.common.version
AUTHOR_NAME = 'Paul Paterson'
AUTHOR_EMAIL = 'ppaterson@gmail.com'
AUTHOR_URL = "http://www.perpetualpyramid/wordgolf.html"
PRODUCT_NAME = "Word Golf"
SCRIPT_MAIN = 'wordgolf.py'
VERSIONSTRING = PRODUCT_NAME + " " + VERSION
ICONFILE = os.path.join('graphics', 'wordgolf.ico')
 
# Remove the build tree on exit automatically
REMOVE_BUILD_ON_EXIT = True
PYGAMEDIR = os.path.split(pygame.base.__file__)[0]
 
SDL_DLLS = glob.glob(os.path.join(PYGAMEDIR,'*.dll')) 

 
if os.path.exists('dist/'): shutil.rmtree('dist/')
 
extra_files = [   ('', glob.glob('*.txt')),
                  ('graphics', glob.glob('graphics/*.png')),
                  ('sound', glob.glob('sound/*.*')),
                  ('words', glob.glob('words/*.*')),
                  ('pygame', glob.glob(os.path.join(PYGAMEDIR,'*.ttf')))]
 
# List of all modules to automatically exclude from distribution build
# This gets rid of extra modules that aren't necessary for proper functioning of app
# You should only put things in this list if you know exactly what you DON'T need
# This has the benefit of drastically reducing the size of your dist
 
MODULE_EXCLUDES =[
'email',
'AppKit',
'Foundation',
'bdb',
'difflib',
'tcl',
'Tkinter',
'Tkconstants',
'curses',
'distutils',
'setuptools',
'urllib',
'urllib2',
'urlparse',
'BaseHTTPServer',
'_LWPCookieJar',
'_MozillaCookieJar',
'ftplib',
'gopherlib',
'_ssl',
'htmllib',
'httplib',
'mimetools',
'mimetypes',
'rfc822',
'tty',
'webbrowser',
'socket',
'base64',
'compiler',
'pydoc']
 
INCLUDE_STUFF = ['encodings',"encodings.latin_1","pygame._view", "pygame.font"]
 
setup(windows=[
             {'script': SCRIPT_MAIN,
               'other_resources': [(u"VERSIONTAG",1,VERSIONSTRING)]}],
               'icon_resources': [(1,ICONFILE)],
         options = {"py2exe": {
                             "dist_dir" : "WordGolf",
                             "optimize": 2,
                             "includes": INCLUDE_STUFF,
                             "compressed": 1,
                             "ascii": 1,
                             "bundle_files": 2,
                             "ignores": ['tcl','AppKit','Numeric','Foundation'],
                             "excludes": MODULE_EXCLUDES} },
          name = PRODUCT_NAME,
          version = VERSION,
          data_files = extra_files,
         # zipfile = None,
          author = AUTHOR_NAME,
          author_email = AUTHOR_EMAIL,
          url = AUTHOR_URL)
 
# Create the /save folder for inclusion with the installer
#shutil.copytree('save','dist/save')
 
if os.path.exists('WordGolf/tcl'): shutil.rmtree('WordGolf/tcl') 
 
# Remove the build tree
if REMOVE_BUILD_ON_EXIT:
     shutil.rmtree('build/')
 
if os.path.exists('WordGolf/tcl84.dll'): os.unlink('WordGolf/tcl84.dll')
if os.path.exists('WordGolf/tk84.dll'): os.unlink('WordGolf/tk84.dll')
 
for f in SDL_DLLS:
    fname = os.path.basename(f)
    try:
        shutil.copyfile(f,os.path.join('WordGolf',fname))
    except: pass

with zipfile.ZipFile(os.path.join('WordGolf', 'library.zip'), 'a') as z:
     z.write(os.path.join(PYGAMEDIR,'freesansbold.ttf'), os.path.join('pygame', 'freesansbold.ttf'))

