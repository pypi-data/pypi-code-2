#!/usr/bin/python2

''' Gitolite config file manager
'''

import os.path
import re

from etc import config
import glgroup
import glrule
import gllock

REGEXP_SET = {
    'comment' : r'^\s*#.*$',
    'group'   : r'^\s*(?P<name>@\w+)\s*=\s*(?P<member_list>.*)\s*(?:#.*)?$',
    'repo'    : r'^\s*repo\s+(?P<name>\w+)\s*(?:#.*)?$',
    'rule'    : (r'^\s*(?P<perm>-|R|RW\+?C?D?)\s+(?P<refex_list>[^=]*)'
                 + r'=\s*(?P<member_list>.*)\s*(?:#.*)?$'),
    'valid_repo_name' : r'\w+',
    }

class GLConfig:
    ''' Gitolite config file manager '''
    def __init__(self, reponame):
        self.filename = os.path.join(config.GITOLITE_ADMIN_REPO_PATH,
                                     'conf',
                                     reponame + '.conf')
        self.locker = gllock.GLLock(self.filename)
        self.reponame_in_config = ''
        self.reponame = reponame
        self.group_list = []
        self.rule_list = []
        self.check_parameters()

    def check_parameters(self):
        ''' Checks if parameters are valid '''
        if not isinstance(self.reponame, (str, unicode)):
            raise TypeError('Parameters type invalid.')
        if not (self.reponame and
                re.match(REGEXP_SET['valid_repo_name'], self.reponame) != None):
            raise ValueError('Repository name is not valid.')

    @staticmethod
    def index():
        ''' List all repo name '''
        dirpath = os.path.join(config.GITOLITE_ADMIN_REPO_PATH, 'conf')
        if not os.access(dirpath, os.R_OK):
            raise RuntimeError('Permission denied for directory %s'
                               % os.path.dirname(dirpath))
        repo_list = filter(lambda x: x.endswith('.conf'), os.listdir(dirpath))
        repo_list = [x[:-5] for x in repo_list]
        return repo_list

    def load(self):
        ''' Load and parse content from file, will raise ParseError '''
        # Initialize
        self.reponame_in_config = ''
        self.group_list = []
        self.rule_list = []
        # Get content
        fdr = open(self.filename, 'r')
        content = fdr.read()
        fdr.close()
        # Parsing
        for idx, line in enumerate(content.splitlines()):
            if not line:
                continue
            # parse comment line
            result = re.match(REGEXP_SET['comment'], line)
            if result:
                continue
            
            # parse group line
            result = re.match(REGEXP_SET['group'], line)
            if result:
                group_name = result.group('name')
                group_member_list = result.group('member_list').strip().split()
                self.group_list.append(glgroup.GLGroup(group_name,
                                                       group_member_list))
                continue
            
            # parse repo line
            result = re.match(REGEXP_SET['repo'], line)
            if result:
                if self.reponame_in_config:
                    raise SyntaxError('Duplicate repo lines at line %d \
                    of file %s' % (idx + 1, os.path.basename(self.filename)))
                self.reponame_in_config = result.group('name')
                if self.reponame != self.reponame_in_config:
                    raise SyntaxError('Error matching repo name \
                    file: %s repo: %s' % (os.path.basename(self.filename),
                                          self.reponame_in_config))
                continue

            # parse rule line
            result = re.match(REGEXP_SET['rule'], line)
            if result:
                if not self.reponame_in_config:
                    raise SyntaxError('Rule lines occur before repo at line %d \
                    of file %s' % (idx + 1, os.path.basename(self.filename)))
                rule_perm = result.group('perm')
                rule_refex_list = result.group('refex_list').strip().split()
                rule_member_list = result.group('member_list').strip().split()
                try:
                    rule = glrule.GLRule(rule_perm,
                                         rule_refex_list,
                                         rule_member_list)
                except ValueError:
                    raise SyntaxError('Refex syntax error at line %d \
                    of file %s' % (idx, os.path.basename(self.filename)))
                self.rule_list.append(rule)
                continue

            # match nothing! syntax error
            raise SyntaxError('Syntax error at line %d of file %s' % (
                idx + 1, os.path.basename(self.filename)))
        # Assertion
        if not self.reponame_in_config:
            raise SyntaxError('No repo name specified of file %s' %
                             os.path.basename(self.filename))

    def save(self):
        ''' Save the content to file. '''
        # Generate content
        content = ''
        for group in self.group_list:
            content += group.dumps()
        content += 'repo %s\n' % self.reponame
        for rule in self.rule_list:
            content += rule.dumps()
        # Write to file
        try:
            fdw = open(self.filename, 'w')
            fdw.write(content)
        finally:
            fdw.close()
        return True

    def exists(self):
        ''' Check if the key exists '''
        return (os.path.exists(self.filename) and
                (not self.locker.locked or not self.locker.is_created))

    def create(self):
        ''' Create a new config '''
        assert self.locker.locked
        if not self.exists():
            result = self.save()
            return result
        else:
            raise RuntimeError('File %s already exists.' % self.filename)

    def delete(self):
        ''' Delete config file of the repo '''
        assert self.locker.locked
        if not self.exists():
            raise RuntimeError('File %s not exists when deleting'
                               % self.filename)
        try:
            os.remove(self.filename)
        except Exception:
            raise RuntimeError('Error when removing file %s' % self.filename)
        return True

    def lock(self, description='No description'):
        ''' Dispatch to GLLock '''
        return self.locker.lock(description)

    def unlock(self, sync=True):
        ''' Dispatch to GLLock '''
        return self.locker.unlock(sync)

    def find_rule(self, refex_list, member_list):
        ''' Find a rule '''
        result = None
        for rule in self.rule_list:
            if (sorted(refex_list) == sorted(rule.refex_list) and
                sorted(member_list) == sorted(rule.member_list)):
                result = rule
                break
        return result

    def match_rule(self, ref, member):
        ''' Match a rule '''
        result = []
        for rule in self.rule_list:
            if (member in glgroup.GLGroup.expand(rule.member_list,
                                                 self.group_list) and
                any([re.match(refex, ref) for refex in rule.refex_list])):
                result.append(rule)
                break
        return result

    def find_group(self, name):
        ''' Find a group '''
        result = None
        for group in self.group_list:
            if group.name == name:
                result = group
                break
        return result
        
