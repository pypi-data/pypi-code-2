# Copyright (C) 2010-2011 Michal Nowikowski <godfryd@gmail.com>
# All rights reserved.
#
# Permission  is  hereby granted,  free  of charge,  to  any person
# obtaining a  copy of  this software  and associated documentation
# files  (the  "Software"),  to   deal  in  the  Software   without
# restriction,  including  without limitation  the  rights to  use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies  of  the  Software,  and to  permit  persons  to  whom the
# Software  is  furnished  to  do  so,  subject  to  the  following
# conditions:
#
# The above copyright  notice and this  permission notice shall  be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS  IS", WITHOUT WARRANTY OF ANY  KIND,
# EXPRESS OR IMPLIED, INCLUDING  BUT NOT LIMITED TO  THE WARRANTIES
# OF  MERCHANTABILITY,  FITNESS   FOR  A  PARTICULAR   PURPOSE  AND
# NONINFRINGEMENT.  IN  NO  EVENT SHALL  THE  AUTHORS  OR COPYRIGHT
# HOLDERS  BE LIABLE  FOR ANY  CLAIM, DAMAGES  OR OTHER  LIABILITY,
# WHETHER  IN AN  ACTION OF  CONTRACT, TORT  OR OTHERWISE,  ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import os
import pickle
import logging
import re
import time
from mako.template import Template
from killableprocess import Popen, PIPE, STDOUT

#try:
#    import mercurial
#    from mercurial import node, commands, hg, ui
#except ImportError:
#    mercurial = None

try:
    import git
except ImportError:
    git = None


log = logging.getLogger("rj.triggers")
log = logging


class Trigger(object):
    def __init__(self, project, trigger_type, name, trigger):
        self.project = project
        self.trigger_type = trigger_type
        self.name = name
        self._load_state()

    def prepare(self, project):
        pass

    def get_changes(self):
        raise Exception("not implemented")

    def _load_state(self):
        self.state = self.project.load_trigger_state(self.name)

    def _save_state(self):
        self.project.save_trigger_state(self.name, self.state)

class GitRepo(Trigger):
    def __init__(self, project, trigger_type, name, repo_info):
        Trigger.__init__(self, project, trigger_type, name, repo_info)

        if git == None:
            raise Exception("missing git")

        self.url = repo_info['url']
        self.directory = repo_info['directory']

#        return dumper.represent_mapping(cls.yaml_tag, dict(url=repo.url, directory=repo.directory))

    def prepare(self):
        log.info("Preparing Git repository for project %s" % self.project.name)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        elif not os.path.isdir(self.directory):
            raise Exception("%s should be a directory" % self.directory)

        if not os.path.exists(os.path.join(self.directory, ".git")):
            log.info("Cloning Git repo")
            g = git.cmd.Git(self.directory)
            g.clone(self.url, self.directory)

        self.repo = git.Repo(self.directory)

        self._update_state()
        log.info("Preparation completed")

    def _update_state(self):
        tip = self.repo.heads[0].commit.id
        self.state["tip"] = tip
        self._save_state()

    def _parse_changes(self, changes):
        changesets = []
        for rev, change in changes:
            # parse author and his email
            author = change.author.name
            email = change.author.email
            # parse date
            date = time.strftime("%Y.%m.%d<br/>%H:%M", change.authored_date)
            files = change.stats.files.keys()
            c = {"revision": rev, "author": author, "email": email, "date": date, "comment": change.message,
                 "files": files}
            changesets.append(c)
            #repo.manifest.read(change[0])
        return changesets

    def _get_changes(self):
        # do git pull
        self.repo.git.pull()
        prev_tip = self.state["tip"]
        tip = self.repo.heads[0].commit
        changes = []
        for r in self.repo.commits_between(prev_tip, tip):
            c = self.repo.commit(r)
            changes.append((r, c))
        log.info("%s: repo %s changes %d" % (self.project.name, self.url, len(changes)))

        if len(changes) > 0:
            self._update_state()
            return self._parse_changes(changes)

        return []

    def get_changes(self):
        changesets = []
        try:
            changesets = self._get_changes()
        except Exception, e:
            log.exception(e)
        return {"info": "Git repository %s" % self.url, "changesets": changesets}

class MercurialRepo(Trigger):
    def __init__(self, project, trigger_type, name, repo_info):
        Trigger.__init__(self, project, trigger_type, name, repo_info)

# TODO: replace it with command
#        if mercurial == None:
#            raise Exception("missing mercurial")

        self.url = repo_info['url']
        self.directory = repo_info['directory']

#        return dumper.represent_mapping(cls.yaml_tag, dict(url=repo.url, directory=repo.directory))

    def prepare(self):
        log.info("Preparing Mercurial repository for project %s" % self.project.name)
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        elif not os.path.isdir(self.directory):
            raise Exception("%s should be a directory" % self.directory)

#        self.ui = ui.ui()

        if not os.path.exists(os.path.join(self.directory, ".hg")):
            log.info("Cloning Mercurial repo")
            #commands.clone(self.ui, self.url, self.directory)
            cmd = "hg -y clone %s %s" % (self.url, self.directory)
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            p.wait()

        #self.repo = hg.repository(self.ui, self.directory)
        self._update_state()
        log.info("Preparation completed")

    def _get_tip(self):
        cmd = "hg -y log -r tip --template \"{rev}:{node}\""
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, cwd=self.directory)
        p.wait()
        tip_rev = p.stdout.read().strip()
        return tip_rev

    def _update_state(self):
        #tip = self.repo.changelog.tip()
        #tip_info = self.repo.changelog.read(tip)
        #tip_rev = node.hex(tip)
        tip_rev = self._get_tip()
        
        self.state["tip"] = tip_rev
        self._save_state()

    def _get_changes(self):
        log.info("pulling repo")
        cmd = "hg -y pull -u"
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, cwd=self.directory)
        out, err = p.communicate()
        log.info("hg pull: %s" % out)
        
        old_tip = self.state["tip"]
        new_tip = self._get_tip()
        
        log.info("old tip: %s,  new tip %s" % (old_tip, new_tip))

        sep = "#@##@##@##@##@##@##@#"
        cmd = "hg -y log "
        cmd += "--template \"{rev}:{node}\\n{author|user}\\n{author|email}\\n{date|isodate}\\n{files}\\n{desc}\\n%s\\n\" " % sep
        cmd += "-r %s:%s" % (old_tip, new_tip)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT, cwd=self.directory)
        text, err = p.communicate()
        text = text.strip()
        entries = text.split(sep)[:-1]

        changes = []
        for e in entries:
            log.debug(e)
            e = e.split("\n")
            rev = e[0]
            author = e[1]
            email = e[2]
            date = e[3]
            files = e[4]
            comment = "\n".join(e[5:])
            if rev == old_tip:
                continue
            log.info("%s, %s, %s, %s" % (rev, author, date, comment))
            #date = time.strftime("%Y.%m.%d<br/>%H:%M", time.localtime(t))
            c = {"revision": rev, "author": author, "email": email, "date": date, "comment": comment,
                 "branch": "[branch-TODO]", "files": files}
            changes.append(c)

        log.info("%s: repo %s changes %d" % (self.project.name, self.url, len(changes)))
        if len(changes) > 0:
            self._update_state()
            return changes

        return []

    def get_changes(self):
        changesets = []
        try:
            changesets = self._get_changes()
        except Exception, e:
            log.exception(e)
        return {"info": "Mercurial repository %s" % self.url, "changesets": changesets}

trigger_classes = {"git": GitRepo,
                   "mercurial": MercurialRepo}
