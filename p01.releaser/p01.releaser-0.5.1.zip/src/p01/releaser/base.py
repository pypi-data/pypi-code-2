###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""Internals

$Id:$
"""
__docformat__ = 'ReStructuredText'

import datetime
import logging
import optparse
import os
import pkg_resources
import re
import subprocess
import sys

logger = logging.Logger('p01.releaser')
formatter = logging.Formatter('%(levelname)s - %(message)s')

RE_SETUP_URL = re.compile("url ?= ?'(.*)',")


_marker = object()

def do(cmd, cwd=None, captureOutput=True, defaultOnError=_marker):
    logger.debug('command: ' + cmd)
    if captureOutput:
        stdout = stderr = subprocess.PIPE
    else:
        stdout = stderr = None
    p = subprocess.Popen(
        cmd, stdout=stdout, stderr=stderr,
        shell=True, cwd=cwd)
    stdout, stderr = p.communicate()
    if stdout is None:
        stdout = "see output above"
    if stderr is None:
        stderr = "see output above"
    if p.returncode != 0:
        if defaultOnError == _marker:
            logger.debug(u'an error occurred while running command: %s' %cmd)
            logger.debug('error output: \n%s' % stderr)
            sys.exit(p.returncode)
        else:
            return defaultOnError
    logger.debug('output: \n%s' % stdout)
    return stdout


class SVN(object):
    """SVN command wrapper"""

    user = None
    passwd = None
    forceAuth = False

    #TODO: spaces in urls+folder names???

    def __init__(self, user=None, passwd=None, forceAuth=False):
        self.user = user
        self.passwd = passwd
        self.forceAuth = forceAuth

    def _addAuth(self, command):
        auth = ''
        if self.user:
            auth = '--username %s --password %s' % (self.user, self.passwd)
            if self.forceAuth:
                auth += ' --no-auth-cache'
        command = command.replace('##__auth__##', auth)
        return command

    def info(self, url, defaultOnError=_marker):
        command = 'svn info --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return do(command, defaultOnError=defaultOnError)

    def ls(self, url):
        command = 'svn ls --non-interactive ##__auth__## --xml %s' % url
        command = self._addAuth(command)
        return do(command)

    def cp(self, fromurl, tourl, comment):
        command = 'svn cp --non-interactive ##__auth__## -m "%s" %s %s' %(
            comment, fromurl, tourl)
        command = self._addAuth(command)
        do(command)

    def co(self, url, folder):
        command = 'svn co --non-interactive ##__auth__## %s %s' % (url, folder)
        command = self._addAuth(command)
        do(command)

    def add(self, folder):
        command = 'svn add --non-interactive ##__auth__## %s' % folder
        command = self._addAuth(command)
        do(command)

    def ci(self, folder, comment):
        command = 'svn ci --non-interactive ##__auth__## -m "%s" %s' % (
            comment, folder)
        command = self._addAuth(command)
        do(command)

    def up(self, folder):
        command = 'svn up --non-interactive ##__auth__## "%s"' % folder
        command = self._addAuth(command)
        do(command)

    def status(self, pkgDir):
        command = 'svn status --non-interactive ##__auth__## --xml %s' % pkgDir
        command = self._addAuth(command)
        return do(command)


def guessNextVersion(version):
    pieces = pkg_resources.parse_version(version)
    newPieces = []
    for piece in pieces:
        try:
            newPieces.append(int(piece))
        except ValueError:
            break
    newPieces += [0]*(3-len(newPieces))
    newPieces[-1] += 1
    newVersion = '.'.join([str(piece) for piece in newPieces])
    logger.debug('Last Version: %s -> %s' %(version, newVersion))
    return newVersion


# TODO: if we improve something, use a simpler nested structure pattern like:
#    lines = [{'version':'0.5.0.
#              'date': date,
#              'items': [{'text': text}
#                        {'text': text]}]
# this makes it simpler for replace items if we can get them by version as key
class ChangeDoc(object):
    """Wrapper for CHANGES.txt file"""

    def __init__(self, path):
        if not os.path.exists(path):
            raise ValueError("Missing CHANGES.txt file at %s"  % path)
        self.path = path
        self._load(self.path)

    def _load(self, path):
        """Load data for each line"""
        pattern = re.compile(r"""
        (?P<version>.+)  # Version string
        \(               # Opening (
        (?P<date>.+)     # Date
        \)               # Closing )
        \W*$             # Possible whitespace at end of line.
        """, re.VERBOSE)
        f = open(self.path, 'rb')
        content = f.read()
        f.close()
        self.lines = []
        number = 0
        content = content.replace('\r', '')
        for line in content.split('\n'):
            match = pattern.search(line)
            if match:
                result = {'type': 'headline',
                          'version': match.group('version').strip(),
                          'date': match.group('date'.strip()),
                          'line': number}
                logger.debug("Found heading: %r", result)
            else:
                result = {'type': 'text',
                          'text': line,
                          'line': number}
                logger.debug("Found test: %r", result)
            self.lines.append(result)
            number += 1

    def getVersionText(self, version='unreleased'):
        """Check if the unreleased version has text or .. (three dots)
        and return them if any get found otherwise return an empty list
        """
        observe = False
        content = []
        append = content.append
        for data in self.lines:
            # 2. observe version text
            if observe:
                # 3. collect text
                text = data.get('text', None)
                # start collecting version text
                if text == '- ...':
                    # 4. stop, empty text marker found
                    return None
                elif text:
                    # 3.1, text or empty line, append and continue
                    append(text)
                elif text is None:
                    # 4. stop, this is the next version
                    break
            # 1. start observing
            elif data.get('version') == version or data.get('date') == version:
                observe = True

        # 5. return text
        if content and content[0] == '------------------':
            content.pop(0)
        return '\n'.join(content)

    def _insertText(self, insertAt, text):
        """internals method for replace/insert text"""
        data = self.lines[insertAt]
        # check if we found '- ...' or existing text
        t = data.get('text')
        if t is not None and t.startswith('- ...'):
            # replace content
            if '\n' in text:
                text = text.replace('\r', '')
                # remove current line
                self.lines.pop(insertAt)
                # text lines
                if not text.startswith('-'):
                    text = '- %s' % text
                lns = text.split('\n')
                # insert lines
                lns.reverse()
                for ln in lns:
                    if not (ln.startswith('- ') or ln.startswith('  ')):
                        ln = '  %s' % ln
                    self.lines[insertAt:insertAt] = [{'type': 'text',
                                                      'text': ln,
                                                      'line': insertAt}]
            else:
                if not text.startswith('-'):
                    text = '- %s' % text
                data['text'] = text

        elif t is not None:
            # we just prepend our text to the line data
            # prepend empty line
            self.lines[insertAt:insertAt] = [{'type': 'text',
                                              'text': '',
                                              'line': insertAt}]
            # prepend new text
            if '\n' in text:
                # text lines
                text = text.replace('\r', '')
                if not text.startswith('-'):
                    text = '- %s' % text
                lns = text.split('\n')
                # insert lines
                lns.reverse()
                for ln in lns:
                    if not (ln.startswith('- ') or ln.startswith('  ')):
                        ln = '  %s' % ln
                    self.lines[insertAt:insertAt] = [{'type': 'text',
                                                      'text': ln,
                                                      'line': insertAt}]
            else:
                if not text.startswith('-'):
                    text = '- %s' % text
                self.lines[insertAt:insertAt] = [{'type': 'text',
                                                  'text': text,
                                                  'line': insertAt}]

    def setVersion(self, version='unreleased', text=None):
        """Set given version with some comment"""
        hasText = self.getVersionText(version)
        observe = False
        changed = False
        insertAt = None
        for data in self.lines:
            if data.get('date') == 'unreleased' or data.get('version') == version:
                data['version'] = version
                data['date'] = datetime.datetime.today().strftime('%Y-%m-%d')
                changed = True
                if text is not None:
                    # continue with inserting given text at line
                    insertAt = data['line'] + 3
                    
                # we are done for now
                break
                    
        if insertAt:
            self._insertText(insertAt, text)

        number = 0
        for data in self.lines:
            data['line'] = number
            number += 1

        return changed

    def revert(self):
        self._load(self.path)
        # find first version in file
        start = 0
        numbers = []
        for i, data in enumerate(self.lines):
            headline = data.get('version', False)
            if headline and start == 0:
                # found first headline
                # start after underline and first empty line
                start = i + 2
            elif start > 0 and headline:
                # found next headline, remove last collected empty line
                break
            elif start > 0 and i > start:
                numbers.append(i)

        if numbers:
            # keep last empty line
            numbers.pop(-1)

        # remove collected lines
        self.lines = [item for i, item in enumerate(self.lines)
                      if i not in numbers]

        # now bring marker text back, insert empty text marker
        data = {'type': 'text',
                'text': '- ...',
                'line': 4}
        self.lines[7:7] = [data]

        number = 0
        for data in self.lines:
            data['line'] = number
            number += 1

    def save(self):
        """Set given version with some comment"""
        # first ensure that we allways update the version
        lines = []
        append = lines.append
        for data in self.lines:
            if data['type'] == 'text':
                append(data['text'])
            else:
                append('%s (%s)' % (data['version'], data['date']))
        content = '\n'.join(lines)
        if os.path.exists(self.path):
            os.remove(self.path)
        f = open(self.path, 'w')
        f.write(content)
        f.close()    

    def back2Dev(self, nextVersion=None):
        """Add unreleased version info and text based on last version in doc"""
        if nextVersion is None:
            # get last version (must be at line 4)
            data = self.lines[4]
            if data is not None and data.get('type') == 'headline':
                version = data['version']
                nextVersion = guessNextVersion(version)
        if nextVersion != 'unreleased':
            # insert the following text block

            # 0.5.1 (unreleased)
            # ------------------
            #
            # - ...
            #

            # insert empty line
            data = {'type': 'text',
                    'text': '',
                    'line': 4}
            self.lines[4:4] = [data]
            # insert empty text marker
            data = {'type': 'text',
                    'text': '- ...',
                    'line': 4}
            self.lines[4:4] = [data]
            # insert empty line
            data = {'type': 'text',
                    'text': '',
                    'line': 4}
            self.lines[4:4] = [data]
            # insert underlines
            data = {'type': 'text',
                    'text': '------------------',
                    'line': 4}
            self.lines[4:4] = [data]
            # insert unreleased marker
            data = {'type': 'headline',
                    'version': nextVersion,
                    'date': 'unreleased',
                    'line': 4}
            self.lines[4:4] = [data]
            # renumber
            number = 0
            for data in self.lines:
                data['line'] = number
                number += 1
            return True
        else:
            return False


def getPYPIURLFromPKG(pkgDir, pkgName, private=True):
    url = None
    path = os.path.join(pkgDir, 'setup.py')
    if os.path.exists(path):
        f = open(path, 'rb')
        content = f.read()
        f.close()
        match = re.search(RE_SETUP_URL, content)
        if match is not None:
            url = match.group(1)
            url = url[:-(len(pkgName)+1)]
    return url


def getInput(prompt, default, useDefaults=False):
    if useDefaults:
        return default
    defaultStr = ''
    if default:
        defaultStr = ' [' + default + ']: '
    value = raw_input(prompt + defaultStr)
    if not value:
        return default
    return value


# options
usage = "usage: release [options] <package-name>"
parser = optparse.OptionParser(usage)

parser.add_option(
    "-q", "--quiet", action="store_true",
    dest="quiet", default=False,
    help="When specified, no messages are displayed.")

parser.add_option(
    "-v", "--verbose", action="store_true",
    dest="verbose", default=False,
    help="When specified, debug information is created.")

parser.add_option(
    "-d", "--use-defaults", action="store_true",
    dest="useDefaults", default=False,
    help="When specified, less user input is required and the defaults are used.")

parser.add_option(
    "-n", "--next-version", action="store_true",
    dest="nextVersion", default=None,
    help="When set, the system uses this version.")
