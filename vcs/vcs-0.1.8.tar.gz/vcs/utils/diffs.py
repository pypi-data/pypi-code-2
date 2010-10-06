# -*- coding: utf-8 -*-
# original copyright: 2007-2008 by Armin Ronacher
# licensed under the BSD license.
from difflib import unified_diff
from mercurial import patch
from mercurial.mdiff import diffopts
from itertools import tee
from vcs.exceptions import VCSError
from vcs.nodes import FileNode, NodeError
import difflib
import logging
import re

def get_udiff(filenode_old, filenode_new):
    """
    Returns unified diff between given ``filenode_old`` and ``filenode_new``.
    """
    try:
        filenode_old_date = filenode_old.last_changeset.date
    except NodeError:
        filenode_old_date = None
        
    try:
        filenode_new_date = filenode_new.last_changeset.date
    except NodeError:
        filenode_new_date = None
    
    for filenode in (filenode_old, filenode_new):
        if not isinstance(filenode, FileNode):
            raise VCSError("Given object should be FileNode object, not %s"
                % filenode.__class__)
            
    if filenode_old_date and filenode_new_date:        
        if not filenode_old_date < filenode_new_date:
            logging.debug("Generating udiff for filenodes with not increasing "
                "dates")

    vcs_udiff = unified_diff(filenode_old.content.splitlines(True),
                               filenode_new.content.splitlines(True),
                               filenode_old.name,
                               filenode_new.name,
                               filenode_old_date,
                               filenode_old_date)
    return vcs_udiff


def get_gitdiff(filenode_old, filenode_new):
    """Returns mercurial style git diff between given 
    ``filenode_old`` and ``filenode_new``.
    """
    
    for filenode in (filenode_old, filenode_new):
        if not isinstance(filenode, FileNode):
            raise VCSError("Given object should be FileNode object, not %s"
                % filenode.__class__)
    
    repo = filenode_new.changeset.repository    
    return patch.diff(repo.repo, filenode_old.changeset.raw_id,
                      filenode_new.changeset.raw_id, opts=diffopts(git=True))


class DiffProcessor(object):
    """
    Give it a unified diff and it returns a list of the files that were
    mentioned in the diff together with a dict of meta information that
    can be used to render it in a HTML template.
    """
    _chunk_re = re.compile(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)')

    def __init__(self, udiff, differ='udiff'):
        """
        :param udiff:   a text in udiff format
        """
        
        self.__udiff = udiff
        if isinstance(self.__udiff, basestring):
            udiff = self.__udiff.splitlines(1)
        else:
            udiff_copy = self.copy_iterator()
            
        self.lines = map(self.escaper, udiff_copy)
        
        # Select a differ.
        if differ == 'difflib':
            self.differ = self._highlight_line_difflib
        else:
            self.differ = self._highlight_line_udiff

    def escaper(self, string):
        return string.replace('<', '&lt;').replace('>', '&gt;')

    def copy_iterator(self):
        """
        make a fresh copy of generator, we should not iterate thru 
        an original as it's needed for repeating operations on 
        this instance of DiffProcessor
        """ 
        self.__udiff, iterator_copy = tee(self.__udiff)
        return iterator_copy
        
    def _extract_rev(self, line1, line2):
        """
        Extract the filename and revision hint from a line.
        """
        try:
            if line1.startswith('--- ') and line2.startswith('+++ '):
                l1 = line1[4:].split(None, 1)
                old_filename = l1[0] if len(l1) >= 1 else None
                old_rev = l1[1] if len(l1) == 2 else 'old'

                l2 = line1[4:].split(None, 1)
                #new_filename = l2[0] if len(l2) >= 1 else None
                new_rev = l2[1] if len(l2) == 2 else 'new'

                return old_filename, new_rev, old_rev
        except (ValueError, IndexError):
            pass

        return None, None, None

    def _highlight_line_difflib(self, line, next):
        """
        Highlight inline changes in both lines.
        """

        if line['action'] == 'del':
            old, new = line, next
        else:
            old, new = next, line

        oldwords = re.split(r'(\W)', old['line'])
        newwords = re.split(r'(\W)', new['line'])

        sequence = difflib.SequenceMatcher(None, oldwords, newwords)

        oldfragments, newfragments = [], []
        for tag, i1, i2, j1, j2 in sequence.get_opcodes():
            oldfrag = ''.join(oldwords[i1:i2])
            newfrag = ''.join(newwords[j1:j2])
            if tag != 'equal':
                if oldfrag:
                    oldfrag = '<del>%s</del>' % oldfrag
                if newfrag:
                    newfrag = '<ins>%s</ins>' % newfrag
            oldfragments.append(oldfrag)
            newfragments.append(newfrag)

        old['line'] = "".join(oldfragments)
        new['line'] = "".join(newfragments)

    def _highlight_line_udiff(self, line, next):
        """
        Highlight inline changes in both lines.
        """
        start = 0
        limit = min(len(line['line']), len(next['line']))
        while start < limit and line['line'][start] == next['line'][start]:
            start += 1
        end = -1
        limit -= start
        while - end <= limit and line['line'][end] == next['line'][end]:
            end -= 1
        end += 1
        if start or end:
            def do(l):
                last = end + len(l['line'])
                if l['action'] == 'add':
                    tag = 'ins'
                else:
                    tag = 'del'
                l['line'] = '%s<%s>%s</%s>%s' % (
                    l['line'][:start],
                    tag,
                    l['line'][start:last],
                    tag,
                    l['line'][last:]
                )
            do(line)
            do(next)

    def _parse_udiff(self):
        """
        Parse the diff an return data for the template.
        """
        lineiter = iter(self.lines)
        files = []
        try:
            line = lineiter.next()
            #skip first context
            skipfirst = True
            while 1:
                # continue until we found the old file
                if not line.startswith('--- '):
                    line = lineiter.next()
                    continue

                chunks = []
                filename, old_rev, new_rev = \
                    self._extract_rev(line, lineiter.next())
                files.append({
                    'filename':         filename,
                    'old_revision':     old_rev,
                    'new_revision':     new_rev,
                    'chunks':           chunks
                })

                line = lineiter.next()
                while line:
                    match = self._chunk_re.match(line)
                    if not match:
                        break

                    lines = []
                    chunks.append(lines)

                    old_line, old_end, new_line, new_end = \
                        [int(x or 1) for x in match.groups()[:-1]]
                    old_line -= 1
                    new_line -= 1
                    context = len(match.groups()) == 5
                    old_end += old_line
                    new_end += new_line


                    if context:
                        if not skipfirst:
                            lines.append({
                                'old_lineno': '...',
                                'new_lineno': '...',
                                'action': 'context',
                                'line': line,
                            })
                        else:
                            skipfirst = False

                    line = lineiter.next()
                    while old_line < old_end or new_line < new_end:
                        if line:
                            command, line = line[0], line[1:]
                        else:
                            command = ' '
                        affects_old = affects_new = False

                        # ignore those if we don't expect them
                        if command in '#@':
                            continue
                        elif command == '+':
                            affects_new = True
                            action = 'add'
                        elif command == '-':
                            affects_old = True
                            action = 'del'
                        else:
                            affects_old = affects_new = True
                            action = 'unmod'

                        old_line += affects_old
                        new_line += affects_new
                        lines.append({
                            'old_lineno':   affects_old and old_line or '',
                            'new_lineno':   affects_new and new_line or '',
                            'action':       action,
                            'line':         line
                        })
                        line = lineiter.next()

        except StopIteration:
            pass

        # highlight inline changes
        for file in files:
            for chunk in chunks:
                lineiter = iter(chunk)
                #first = True
                try:
                    while 1:
                        line = lineiter.next()
                        if line['action'] != 'unmod':
                            nextline = lineiter.next()
                            if nextline['action'] == 'unmod' or \
                               nextline['action'] == line['action']:
                                continue
                            self.differ(line, nextline)
                except StopIteration:
                    pass

        return files

    def prepare(self):
        """
        Prepare the passed udiff for HTML rendering. It'l return a list
        of dicts
        """
        return self._parse_udiff()

    def raw_diff(self):
        """
        Returns raw string as udiff
        """
        return ''.join(self.copy_iterator())

    def as_html(self, table_class='code-difftable', line_class='line',
                new_lineno_class='lineno old', old_lineno_class='lineno new',
                code_class='code'):
        """
        Return udiff as html table with customized css classes
        """

        def _link_to_if(condition, label, url):
            """
            Generates a link if condition is meet or just the label if not.
            """

            if condition:
                return '''<a href="%(url)s">%(label)s</a>''' % {'url': url,
                                                                'label':label}
            else:
                return label

        diff_lines = self.prepare()
        _html_empty = True
        _html = '''<table class="%(table_class)s">\n''' \
                                            % {'table_class':table_class}
        for diff in diff_lines:
            for line in diff['chunks']:
                _html_empty = False
                for change in line:
                    _html += '''<tr class="%(line_class)s %(action)s">\n''' \
                        % {'line_class':line_class, 'action':change['action']}
                    anchor_old_id = ''
                    anchor_new_id = ''
                    anchor_old = "%(filename)s_OLD%(oldline_no)s" % \
                                             {'filename':diff['filename'],
                                             'oldline_no':change['old_lineno']}
                    anchor_new = "%(filename)s_NEW%(oldline_no)s" % \
                                             {'filename':diff['filename'],
                                             'oldline_no':change['new_lineno']}
                    cond_old = change['old_lineno'] != '...' and \
                                                        change['old_lineno']
                    cond_new = change['new_lineno'] != '...' and \
                                                        change['new_lineno']
                    if cond_old:
                        anchor_old_id = 'id="%s"' % anchor_old
                    if cond_new:
                        anchor_new_id = 'id="%s"' % anchor_new
                    ############################################################
                    # OLD LINE NUMBER
                    ############################################################
                    _html += '''\t<td %(a_id)s class="%(old_lineno_cls)s">''' \
                                    % {'a_id':anchor_old_id,
                                       'old_lineno_cls':old_lineno_class}

                    _html += '''<pre>%(link)s</pre>''' \
                        % {'link':
                        _link_to_if(cond_old, change['old_lineno'], '#%s' \
                                                                % anchor_old)}
                    _html += '''</td>\n'''
                    ############################################################
                    # NEW LINE NUMBER
                    ############################################################

                    _html += '''\t<td %(a_id)s class="%(new_lineno_cls)s">''' \
                                    % {'a_id':anchor_new_id,
                                       'new_lineno_cls':new_lineno_class}

                    _html += '''<pre>%(link)s</pre>''' \
                        % {'link':
                        _link_to_if(cond_new, change['new_lineno'], '#%s' \
                                                                % anchor_new)}
                    _html += '''</td>\n'''
                    ############################################################
                    # CODE
                    ############################################################
                    _html += '''\t<td class="%(code_class)s">''' \
                                                    % {'code_class':code_class}
                    _html += '''\n\t\t<pre>%(code)s</pre>\n''' \
                                                    % {'code':change['line']}
                    _html += '''\t</td>'''
                    _html += '''\n</tr>\n'''
        _html += '''</table>'''
        if _html_empty:return None
        return _html


