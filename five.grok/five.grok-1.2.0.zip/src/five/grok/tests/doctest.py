# -*- coding: utf-8 -*-
"""
five.grok

$Id: doctest.py 88531 2008-07-18 16:30:30Z jfroche $
"""
import re
import os.path


def doctestToPython(filenameInput, filenameOutput):
    assert os.path.exists(filenameInput)
    docFileR = open(filenameInput, 'r')
    newLines = []
    originalLines = []
    for line in docFileR.readlines():
        originalLines.append(line)
        if '<<<' in line:
            match = re.match(re.compile('(\s+<<<\s)(.*)'), line)
            if match:
                grokCodeFlag = True
                newLines.append("%s\n" % match.groups()[1])
        elif '...' in line and grokCodeFlag == True:
            match = re.match(re.compile('(\s+\.\.\.\s)(.*)'), line)
            if match:
                newLines.append("%s\n" % match.groups()[1])
        elif '<<<' not in line or '...' not in line: # handle comments
            grokCodeFlag = False
            newLines.append('#%s' % line)

    docFileR.close()

    docFileW = open(filenameOutput, 'w')
    for newLine in newLines:
        if newLine.strip() != '#':
            docFileW.write('%s' % newLine)
        else:
            docFileW.write('\n')
    docFileW.close()


if __name__ == '__main__':
    doctestToPython('../README.txt', '../README.txt.out')
