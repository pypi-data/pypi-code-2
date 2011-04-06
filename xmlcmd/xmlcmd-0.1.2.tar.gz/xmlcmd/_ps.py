"""
# view processes which are using more than 2.5% CPU
ps --xml aux | xpath '//process/command/text()[../../cpu > 2.5]'
"""

import sys
import os
from xml.etree import cElementTree as ET
import subprocess
import string
from xml.sax.saxutils import escape

def main(args=None,orig_cmd_path=None):
    if args is None:
        args = sys.argv

    ps_out = subprocess.Popen([orig_cmd_path] + args[1:], stdout=subprocess.PIPE).communicate()[0]
    ps_lines = ps_out.splitlines()
    headings = ps_lines[0].split()
    root = ET.Element('ps')
    for process in ps_lines[1:]:
        p = ET.SubElement(root, 'process')
        for heading,item in zip(headings, process.split(None, len(headings))):
            if not heading[0] in string.letters:
                heading = heading[1:]
            ET.SubElement(p, escape(heading.lower())).text = escape(item)
    ET.ElementTree(root).write(sys.stdout, 'utf-8')
    sys.stdout.write('\n')

if __name__ == '__main__':
    main()

