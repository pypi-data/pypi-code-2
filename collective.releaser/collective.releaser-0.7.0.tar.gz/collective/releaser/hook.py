# -*- coding: utf-8 -*-
import os
import sys
import smtplib
import pkg_resources
import re
import tempfile
import shutil
import datetime

from ConfigParser import ConfigParser
from email.MIMEText import MIMEText
from zc.buildout.buildout import _recipe

from collective.releaser.config import DistutilsMultiConfig
from collective.releaser.packet import (_run_setup, _get_setup,
                                        _get_svn_paths, get_name)
from collective.releaser.packet import get_version, get_metadata
from collective.releaser import base

def mail_hook(cmd, name):
    config = DistutilsMultiConfig()
    if 'mail_hook' not in config:
        return
    local_config = config['mail_hook']
    emails = local_config.get('emails')
    if emails is None:
        return
    host = local_config.get('host', 'localhost')
    port = local_config.get('port', '25')
    server = smtplib.SMTP(host, int(port))

    subject = local_config.get('subject',
                               '[Release] %(name)s %(version)s')
    subject = subject.strip() % dict(name=get_name(),
                                     version=local_config.get('version',''))
    mfrom = local_config.get('from', 'tarek@ziade.org').strip()
    emails = local_config['emails'].split()
    emails = [e.strip() for e in emails]

    if os.path.isfile('CHANGES'):
        CHANGES = 'CHANGES'
    elif os.path.isfile('CHANGES.txt'):
        CHANGES = 'CHANGES.txt'
    else:
        return

    version = local_config.get('version', 'trunk')
    kicker = '%(name)s %(version)s has been released !'
    kicker = kicker % dict(name=get_name(),
                           version=version)

    contents = [kicker, '', 'Work done in this version:']

    # extract the right section in CHANGES
    changes = open(CHANGES).read().split('\n')
    start = 0
    end = -1
    for no, line in enumerate(changes):
        if line.startswith(version) and start == 0:
            start = no + 2
        if start != 0 and no > start + 1 and line.startswith('='):
            end = no - 1
            break
    if start < len(changes):
        contents.extend(changes[start:end])

    base.display('Sending mails')
    for mto in emails:
        email = MIMEText('\n'.join(contents), 'plain')
        email['From'] = mfrom
        email['To'] = mto
        email['Subject'] = subject
        server.sendmail(mfrom, mto, email.as_string())


def create_tag(cmd=None, name=None):
    """creates a tag for the current version"""
    if not base.has_svn_support():
        raise base.ReleaseError('You need Subversion client')

    version = get_version()
    paths = _get_svn_paths()
    root = paths['root']
    tag_root = paths['tag_root']
    tag = paths['tag']
    trunk = paths['trunk']

    base.display('Creating tag for %s' % version)
    # commiting trunk
    base.svn_commit('preparing release %s' % version)

    # checking if tag_root exists
    base.svn_mkdir(tag_root)

    # checking if the tag exists, if so, override it
    base.svn_remove(tag)
    base.svn_copy(trunk, tag, 'tag for %s release' % version)

    # now let's work on the tag: making a few changes in setup.cfg
    rep = tempfile.mkdtemp()
    old_rep = os.getcwd()
    try:
        os.chdir(rep)
        base.svn_checkout(tag, rep)
        setup_file = os.path.join(rep, 'setup.cfg')
        if os.path.exists(setup_file):
            setup_cfg = ConfigParser()
            setup_cfg.read([setup_file])
            changed = False
            if 'egg_info' in setup_cfg.sections():
                for option in ('tag_build', 'tag_svn_revision'):
                    if option in setup_cfg.options('egg_info'):
                        setup_cfg.remove_option('egg_info', option)
                        changed = True
            if changed:
                setup_cfg.write(open(setup_file, 'w'))
            base.svn_commit('fixed setup.cfg for %s' % version)
    finally:
        os.chdir(old_rep)
        shutil.rmtree(rep, ignore_errors=True)

def upgrade_change_file(cmd, name):
    """Increment changes."""
    author = get_metadata('maintainer')
    if author == 'UNKNOWN':
        author = get_metadata('author')
    if author == 'UNKNOWN':
        author = get_metadata('contact')
    if author != 'UNKNOWN':
        author = '[%s]' % author
    else:
        author = ''

    version = get_version()
    locations = (os.path.join(os.getcwd(), 'CHANGES'),
                 os.path.join(os.getcwd(), 'CHANGES.txt'))
    CHANGES = locations[0]
    if not os.path.exists(CHANGES) and os.path.exists(locations[1]):
        CHANGES = locations[1]

    year = datetime.datetime.now().strftime('%Y')
    now = datetime.datetime.now().strftime('%Y-%m-%d')
    trunk_re = re.compile(r'^trunk \(.*\)$', re.DOTALL)
    trunk_line = 'trunk (%s)' % now
    bootstrap = [trunk_line, len(trunk_line) * '=', '',
                 '  - xxx ' + author, '']

    if os.path.exists(CHANGES):
        content = open(CHANGES).read()
        # let's replace the trunk with the current version and date
        version_line = '%s (%s)' % (version, now)
        underline = len(version_line) * '='
        content = content.split('\n')
        for index, line in enumerate(content):
            if trunk_re.match(line):
                content[index] = version_line
                content[index+1] = underline
                break
        content = bootstrap + content
    else:
        # no CHANGES file, let's create it
        content = bootstrap

    f = open(CHANGES, 'wb')
    try:
        f.write('\n'.join(content))
    finally:
        f.close()

re_version = re.compile(r"""^version\s*=\s*(?:"|')(.*?)(?:"|')""",
                        re.MULTILINE|re.DOTALL)

def raise_version(cmd, name):
    """Raises the version."""
    version = get_version()
    new_version = False
    base.display('This package is version %s' % version)
    release = True
    if not cmd.auto:
        if not cmd.release:
            release = base.yes_no_input('Do you want to create a release ? ')
    if not release:
        return
    if not cmd.auto and cmd.version == '':
       new_version = base.safe_input('Enter a version', version)
    else:
        if cmd.version != '':
            new_version = cmd.version
        else:
            new_version = str(float(version)+.1)

    if version == new_version:
        return
    base.display('Raising the version...')
    # check version.txt
    for root, dirs, files in os.walk(os.getcwd()):
        for dirname in dirs:
            if not os.path.isdir(os.path.join(root, dirname, 'tests')):
                continue
            filename = os.path.join(root, dirname, 'version.txt')
            if not os.path.isfile(filename):
                continue
            f = open(filename, 'wb')
            try:
                f.write(new_version)
            finally:
                f.close()
    # check setup.py
    new_setup = re_version.sub("version = '%s'" % new_version, _get_setup())
    setup_py = os.path.join(os.getcwd(), 'setup.py')
    f = open(setup_py, 'wb')
    try:
        f.write(new_setup)
    finally:
        f.close()

    if base.has_svn_support():
        base.display('Commiting changes...')
        base.svn_commit('bumped revision')

    cmd.new_version = new_version

