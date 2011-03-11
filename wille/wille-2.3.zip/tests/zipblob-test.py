import sys; sys.path.append('..')

from wille.zipblob import Zipblob
import os

debug = False

if debug: print('Single files are working fine..')
a = Zipblob()
a.debug = debug

if debug: print('..although checking out an empty zip causes an error:')
try:
    temp_folder = a.check_out()
    assert( len(temp_folder)>0 )
except Exception, e:
    #raise e
    pass

# Add file
result = a.add_file('data/mvc.png', 'mvc.png', 'w')

# Checkout file
temp_folder = a.check_out()
assert( len(temp_folder)>0 )

if debug: print('Adding a directory, however, does not seem to be working.')

if debug: print('Testing with a non-empty directory:')
files = os.walk('data/image')
count = 0
for f in files:
	if debug: print(f)
	count += 1
assert(count>0)

b = Zipblob()
b.add_dir('data/image')
try:
    if debug: print('Zip contents: ' + b.check_out())
except:
    if debug: print('Any idea why this happens?')
    
if debug: print "Done."
