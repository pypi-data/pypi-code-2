#!/opt/python/python-2.4/bin/python
# YOU PROBABLY NEED TO ADJUST THIS PATH

# Define here the patterns for all error messages you want to ignore
messages_to_ignore = [
  '.*?entry ignored',
  '^msgfmt: found .*',
]

import os
import sys
import re
from popen2 import popen3

ignore = [re.compile(patt) for patt in messages_to_ignore]

if len(sys.argv)<2:
  sys.exit('You must specify a file name or pattern (regex).\nExample: ".*?napo.*"')
pattstr = sys.argv[1]
patt = re.compile(pattstr)

filenames = [x for x in os.listdir('.') if x.endswith('po')]
names =  [x for x in filenames if patt.match(x)]

for name in names:
  print "\nchecking", name
  cmd = "msgfmt -C %s" %(name)
  stout, stdin, stderr = popen3(cmd)
  err = stderr.read()
  if err:
    problems = list()
    lines = err.split('\n')
    for line in lines:
      if line.strip() == '':
        continue
      do_print = True
      for patt_ignore in ignore:
        if patt_ignore.match(line):
          do_print = False
          break
      if do_print:
        problems.append(line)

    if problems:
      print "\n".join(problems)

