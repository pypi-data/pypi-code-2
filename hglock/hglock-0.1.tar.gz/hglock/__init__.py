# cooperative file locking extension
#
# Copyright 2011 aragost Trifork
#
# This software may be used and distributed according to the terms of
# the GNU General Public License version 2 or any later version.

"""cooperative file locking"""

import os, errno, random, time, socket, email.Utils, email.Generator, cStringIO

from mercurial import hg, util, pushkey, extensions, ignore
from mercurial import commands as hgcmds, encoding, node, error, mail
from mercurial import filemerge, match as matchmod
from mercurial.i18n import _

# Careful imports to keep compatibility with Mercurial 1.8.x and 1.9
try:
    from mercurial import cmdutil
    matcher = cmdutil.match
except AttributeError:
    from mercurial import scmutil
    matcher = scmutil.match

from unrepr import unrepr

#### Utility functions ####

def report(ui, match, path, errmsg, hint=""):
    if path in match.files():
        # explicit match
        raise util.Abort(errmsg, hint=hint)
    else:
        # implicit match
        if hint:
            hint = " (%s)" % hint
        ui.warn(_('%s, modifications ignored%s\n') % (errmsg, hint))

def findaddr(ui):
    user = ui.config('email', 'from') or ui.username()
    name, addr = email.Utils.parseaddr(user)
    if not addr:
        raise util.Abort(_('found no email address in %r') % user,
                         hint=_('configure ui.username or email.from'))
    return addr

class NoLockRepo(util.Abort):
    pass

def remoterepo(ui, repo, opts):
    path = ui.expandpath('default-lock', 'default')
    if path == 'default-lock':
        raise NoLockRepo(_('no lock repository configured'))
    return hg.repository(hg.remoteui(repo, opts), path)

def age(timestamp):
    periods = [(_('y'), 365 * 24 * 60 * 60),
               (_('w'),   7 * 24 * 60 * 60),
               (_('d'),       24 * 60 * 60),
               (_('h'),            60 * 60),
               (_('m'),                 60),
               (_('s'),                  1)]

    now = time.time()
    diff = int(now - timestamp)

    result = ""
    if diff < 0:
        result = "-"
        diff = -diff

    for i, (unit, period) in enumerate(periods):
        if diff >= period:
            result += '%d%s' % (diff // period, unit)
            if i + 1 < len(periods):
                diff = diff % period
                unit, period = periods[i+1]
                result += '%02d%s' % (diff // period, unit)
            return result

    return _("now")

def readhglocks(repo):
    return ignore.ignore(repo.root, [repo.wjoin('.hglocks')], repo.ui.warn)


#### Error channel protocol functions ####

commands = {}

def command(func):
    commands[func.__name__] = func

def nullpush(repo, key, old, new):
    return False

def nulllist(repo):
    return {}

def registercallbacks(repo):
    if not os.path.isdir(repo.join('lock-errs')):
        return
    for errid in os.listdir(repo.join('lock-errs')):
        registercallback(errid)

def registermsg(repo, errid, errmsg):
    errfile = os.path.join(repo.join('lock-errs'), errid)
    fp = open(errfile, 'w')
    fp.write(errmsg)
    fp.close()
    registercallback(errid)

def registercallback(errid):
    namespace = 'locks-err-%s' % errid

    def listfunc(repo):
        del pushkey._namespaces[namespace]
        errfile = os.path.join(repo.join('lock-errs'), errid)
        fp = open(errfile)
        errmsg = fp.read()
        fp.close()
        os.unlink(errfile)
        return dict(msg=errmsg.encode('string-escape'))

    pushkey.register(namespace, nullpush, listfunc)

def dispatchcmd(repo, cmd, arg, errid):
    try:
        args = unrepr(arg)
    except ValueError, e:
        registermsg(repo, errid, 'could not decode argument: %s' % e)
        return False
    except UnicodeEncodeError, e:
        registermsg(repo, errid, 'args: %r' % args)
        return False

    func = commands.get(cmd)
    if func:
        try:
            func(repo, *args)
            return True
        except Exception, e:
            registermsg(repo, errid, str(e)) # + '\n' + traceback.format_exc())
    else:
        registermsg(repo, errid, 'unknown cmd: %s' % cmd)
    return False

def sendcmd(ui, remote, cmd, *args):
    ui.debug("lock: sending %s%r\n" % (cmd, args))
    arg = repr(args)
    errid = hex(random.getrandbits(80))[2:-1]
    if remote.pushkey('locks-cmd', cmd, arg, errid):
        return None
    else:
        err = remote.listkeys('locks-err-%s' % errid)
        msg = err.get('msg', '')
        return encoding.tolocal(msg.decode('string-escape'))

#### Lock class ####

class Locks(dict):
    def __init__(self, repo, emptyok=False):
        self.dirty = False
        if repo.local():
            repo.ui.debug("lock: reading locks from local %s\n" % repo.root)
            self.repo = repo
            try:
                lockfile = repo.opener('locks', 'r')
                for line in lockfile:
                    key, value = unrepr(line)
                    self[key] = value
                lockfile.close()
            except IOError, inst:
                if inst.errno != errno.ENOENT:
                    raise
                if emptyok:
                    self.dirty = True
                else:
                    raise util.Abort(_('%s is not a lock repository') % repo.root,
                                     hint=_('run "hg init-lock" inside it '
                                            'to initialize it'))
        else:
            repo.ui.debug("lock: reading locks from remote %s\n" % repo.path)
            self.repo = None
            data = repo.listkeys('locks')
            # This extension always inserts the empty string as a key
            # in the data dictionary, so we can use this to detect if
            # a remote repository has the extension enabled.
            if '' not in data:
                raise util.Abort(_('%s is not a lock repository') % repo.path,
                                 hint=_('enable the extension on the server'))
            del data['']
            for key, value in data.iteritems():
                self[unrepr(key)] = unrepr(value)

    def notify(self, branch, path, owner, thief):
        root = os.path.basename(self.repo.root)
        fromaddr = mail.addressencode(self.repo.ui, thief)
        toaddr = mail.addressencode(self.repo.ui, owner)
        subject = "%s: Lock stolen on %s" % (root, path)
        body = ("A lock of yours was stolen by %s:\n\n"
                "Repository: %s\n"
                "Branch:     %s\n"
                "Path:       %s\n") % (thief, root, branch, path)
        now = time.time()
        msg = mail.mimeencode(self.repo.ui, body)
        msg['From'] = fromaddr
        msg['To'] = toaddr
        msg['Cc'] = fromaddr
        msg['Subject'] = mail.headencode(self.repo.ui, subject)
        msg['User-Agent'] = 'Mercurial-lock/%s' % util.version()
        msg['Message-Id'] = '<lock-%s.%s@%s>' % (node.hex(os.urandom(8)),
                                                 now, socket.getfqdn())
        msg['Date'] = email.Utils.formatdate(now, localtime=True)

        fp = cStringIO.StringIO()
        generator = email.Generator.Generator(fp, mangle_from_=False)
        generator.flatten(msg)
        try:
            sendmail = mail.connect(self.repo.ui)
            sendmail(thief, [owner, thief], fp.getvalue())
        except util.Abort, e:
            self.repo.ui.warn("warning: no mail sent: %s\n" % e)

    def set(self, branch, path, addr, filehex, userctxhex, locktime, force):
        key = (branch, path)
        if key in self:
            lockaddr = self[key][0]
            if addr != lockaddr:
                if force:
                    self.notify(branch, path, lockaddr, addr)
                else:
                    raise Exception(_('the file is locked by %s') % lockaddr)
        else:
            try:
                # Lookup user's filectx first since this uses the
                # oldest revision number, and so the server might have
                # this changeset even though the user has made other
                # changesets since.
                userfctx = self.repo[filehex]
                fctx = self.repo[branch][path]
                repoctx = self.repo[fctx.linkrev()]
                if repoctx != userfctx:
                    # The user's fctx does not match our ctx. This can
                    # be caused by a merge combining branches with
                    # identical changes made to path. We detect this
                    # by checking that the user's ctx is a descendent
                    # of our fctx.
                    userctx = self.repo[userctxhex]
                    if repoctx.ancestor(userctx) != repoctx:
                        raise Exception(_('your revision %s is outdated, '
                                          'latest revision is %s\n'
                                          '(pull and then lock it)')
                                        % (userctx, repoctx))
            except error.RepoLookupError:
                raise Exception(_('your new revision %s is not in the '
                                  'lock repository yet\n'
                                  '(push before locking it)')
                                % node.short(node.bin(filehex)))
        self[key] = (addr, locktime)
        self.dirty = True

    def unset(self, branch, path, addr, force):
        key = (branch, path)
        if key not in self:
            raise Exception(_('not locked'))
        else:
            lockaddr, locktime = self[key]
            if lockaddr != addr:
                if force:
                    self.notify(branch, path, lockaddr, addr)
                else:
                    raise Exception(_('the file is locked by %s') % lockaddr)
            del self[key]
            self.dirty = True

    def write(self):
        if not self.repo:
            raise Exception(_('can only write locks to local repository'))
        if not self.dirty:
            return
        wlock = self.repo.wlock()
        try:
            lockfile = self.repo.opener('locks', 'w', atomictemp=True)
            for key, value in sorted(self.iteritems()):
                lockfile.write(repr((key, value)) + '\n')
            lockfile.rename()
        finally:
            wlock.release()

#### pushkey commands ####

@command
def setlock(repo, path, addr, branch, filehex, userctxhex, date, force):
    wlock = repo.wlock()
    try:
        locks = Locks(repo)
        locks.set(branch, path, addr, filehex, userctxhex, date, force)
        locks.write()
    finally:
        wlock.release()

@command
def clearlock(repo, path, addr, branch, force):
    wlock = repo.wlock()
    try:
        locks = Locks(repo)
        locks.unset(branch, path, addr, force)
        locks.write()
    finally:
        wlock.release()

def listlocks(repo):
    locks = Locks(repo)
    # Insert marker that will tell the client that the extension is
    # enabled. An empty dictionary is not enough: it could mean that
    # there are no locks or it could mean that the extension is not
    # enabled. The empty string is something that repr cannot return.
    data = {'': ''}
    for key, value in locks.iteritems():
        data[repr(key)] = repr(value)
    return data

#### Client-side Mercurial commands ####

def initlock(ui, repo, **opts):
    """initialize lock storage"""
    util.makedirs(repo.join('lock-errs'))
    locks = Locks(repo, emptyok=True)
    locks.write()

def locks(ui, repo, **opts):
    """show locked files"""
    wantedbranches = opts.get('branch')
    if not wantedbranches:
        wantedbranches = [repo.dirstate.branch()]
    remote = remoterepo(ui, repo, opts)
    locks = Locks(remote)
    for branch, path in sorted(locks):
        if branch in wantedbranches:
            addr, locktime = locks[branch, path]
            ui.write("%s%s %s%s %6s %s\n"
                     % (addr, ' ' * (16 - encoding.colwidth(addr)),
                        branch, ' ' * (8 - encoding.colwidth(branch)),
                        age(locktime), path))

def setremotelock(ui, remote, repo, ctx, branch, path, addr, date, force):
    fctx = ctx[path]
    latestctx = repo[fctx.linkrev()]
    return sendcmd(ui, remote, 'setlock', path, encoding.fromlocal(addr),
                   encoding.fromlocal(branch), latestctx.hex(), ctx.hex(),
                   date, force)

def lock(ui, repo, path, *pats, **opts):
    """lock the specified files"""
    exitcode = 0
    force = opts.get('force')
    addr = findaddr(ui)
    remote = remoterepo(ui, repo, opts)
    branch = repo.dirstate.branch()
    date = int(time.time())

    # need both ctx and wctx since we cannot pass a workingctx to
    # setremotelock because is calls workingfilectx.linkrev, which
    # crashes as files in the working copy has no linkrev
    ctx = repo['.']
    wctx = repo[None]
    changed = set(wctx.added() + wctx.modified() +
                  wctx.removed() + wctx.deleted())

    oldlocks = Locks(remote)
    m = matcher(repo, (path,) + pats, opts)
    for path in repo.walk(m):
        hint = None
        if path in changed:
            errmsg = _('file has local changes')
            hint = _("revert the file and then lock it")
        elif path not in wctx:
            errmsg = _("no such file in revision %s") % ctx
            hint = _("add, commit, and push it before attempting to lock it")
        else:
            errmsg = setremotelock(ui, remote, repo, ctx, branch, path,
                                   addr, date, force)
        if errmsg:
            report(ui, m, path,
                   _('could not lock %s: %s') % (path, errmsg), hint)
            exitcode = 1
        else:
            lockaddr = oldlocks.get((branch, path), (None, 0))[0]
            if lockaddr and lockaddr != addr and force:
                ui.write(_("%s: lock has been stolen, notification "
                           "sent to %s\n") % (path, lockaddr))
            else:
                ui.note(_("locked %s\n") % path)
    return exitcode

def unlock(ui, repo, path, *pats, **opts):
    """unlock the specified files"""
    exitcode = 0
    force = opts.get('force')
    addr = findaddr(ui)
    remote = remoterepo(ui, repo, opts)
    branch = repo.dirstate.branch()

    oldlocks = Locks(remote)
    m = matcher(repo, (path,) + pats, opts)
    wctx = repo[None]
    changed = set(wctx.added() + wctx.modified() +
                  wctx.removed() + wctx.deleted())
    for path in repo.walk(m):
        if (branch, path) not in oldlocks:
            ui.note(_("%s was not locked\n") % path)
            continue

        hint = None
        if path in changed:
            errmsg = _('file has local changes')
            hint = _("revert the file and then unlock it")
        elif path not in wctx:
            errmsg = _("no such file in revision %s") % repo['.']
            hint = _("add, commit, and push it before attempting to unlock it")
        else:
            errmsg = sendcmd(ui, remote, 'clearlock', path,
                             encoding.fromlocal(addr),
                             encoding.fromlocal(branch),
                             force)
        if errmsg:
            report(ui, m, path,
                   _('could not unlock %s: %s') % (path, errmsg), hint)
            exitcode = 1
        else:
            lockaddr = oldlocks.get((branch, path), (None, 0))[0]
            if lockaddr and lockaddr != addr and force:
                ui.write(_("%s: file has been unlocked, notification "
                           "sent to %s\n") % (path, lockaddr))
            else:
                ui.note(_("unlocked %s\n") % path)
    return exitcode

def push(orig, *args, **opts):
    if opts.get('force'):
        raise util.Abort(_("the lock extension does not allow pushing "
                           "new heads, even with the force option"),
                         hint=_("you must pull and merge, then push again"))
    try:
        return orig(*args, **opts)
    except util.Abort, inst:
        if inst.hint.endswith(_("use push -f to force")):
            inst.hint = _("you must pull and merge, then push again")
        raise inst

def update(orig, ui, repo, *args, **kwargs):

    try:
        remote = remoterepo(ui, repo, {})
        locks = Locks(remote)
    except NoLockRepo:
        locks = {}

    addr = findaddr(ui)
    branch = repo.dirstate.branch()
    hglocks = readhglocks(repo)
    modified = repo[None].modified()

    def picktool(orig, repo, ui, path, binary, symlink):
        if path in modified:
            key = (branch, path)
            if key in locks and locks[key][0] == addr:
                # we hold the lock -- the other messed up
                ui.debug("%s is locked by us, but modified in remote\n" % path)
                return ('internal:dump', None)
            if hglocks(path):
                # we should hold the lock, but don't -- we messed up
                ui.debug("%s should have been locked by us\n" % path)
                ui.write(_("merging %s (was unlocked, local version saved as "
                           "%s.orig)\n") % (path, path))
                util.copyfile(path, path + '.orig')
                return ('internal:other', None)
        return orig(repo, ui, path, binary, symlink)

    oldpicktool = extensions.wrapfunction(filemerge, '_picktool', picktool)
    try:
        return orig(ui, repo, *args, **kwargs)
    finally:
        filemerge._picktool = oldpicktool

#### Server-side hook ####

def checklocks(ui, repo, node, **kwargs):
    if kwargs.get('source') == 'pull':
        return

    locks = Locks(repo, emptyok=True)
    hglocks = readhglocks(repo)
    if not locks and hglocks == util.never:
        return

    start = repo[node].rev()

    badfiles = set()
    tounlock = {}

    for rev in xrange(start, len(repo)):
        ctx = repo[rev]
        branch = ctx.branch()
        name, addr = email.Utils.parseaddr(ctx.user())
        for f in ctx.files():
            key = (branch, f)
            if key in locks:
                lockholder = locks[key][0]
                ui.debug('lock: %s is locked by %s, modified by %s in %s\n'
                         % (f, lockholder, addr, ctx))
                if lockholder == addr:
                    if key not in tounlock:
                        tounlock[key] = (addr, ctx)
                else:
                    badfiles.add(f)
            else:
                ui.debug('lock: %s is not locked\n' % f)
                if hglocks(f):
                    # f should have been locked but isn't -- this can
                    # happen if Bob steals Alice's lock and unlocks
                    # the file after Alice made a local commit to it.
                    badfiles.add(f)
                    ui.debug('lock: %s should have been locked\n' % f)

    if badfiles:
        raise util.Abort(_("rejecting push because of unlocked files: %s")
                         % ", ".join(sorted(badfiles)),
                         hint=_("pull to get the latest versions of the files, "
                                "lock, merge your changes, push again"))
    elif tounlock:
        wlock = repo.wlock()
        try:
            for (branch, f), (addr, ctx) in tounlock.iteritems():
                ui.write('releasing lock on %s (changed in %s)\n' % (f, ctx))
                locks.unset(branch, f, addr, force=True)
            locks.write()
        finally:
            wlock.release()

#### Setup ####

def reposetup(ui, repo):
    if repo.local():
        registercallbacks(repo)
        ui.setconfig('hooks', 'pretxnchangegroup.check-locks', checklocks)

        class lockrepo(repo.__class__):

            _hide_unlocked = False

            def status(self, *args, **kwargs):
                changes = super(lockrepo, self).status(*args, **kwargs)
                if not self._hide_unlocked:
                    return changes
                self.ui.debug('lock: will hide unlocked modified files\n')
                try:
                    remote = remoterepo(self.ui, self, {})
                except NoLockRepo:
                    self.ui.debug('lock: no lock repository, no hiding\n')
                    return changes

                locks = Locks(remote)
                addr = findaddr(self.ui)
                ctx = self['.']
                date = int(time.time())
                branch = ctx.branch()
                match = kwargs.get('match')
                if not match:
                    match = matchmod.always(self.root, self.getcwd())
                hglocks = readhglocks(self)

                # we are only interested in modified and removed
                # files, not added files
                for status in changes[0], changes[2]:
                    filtered = []
                    for path in status:
                        mustlock = hglocks(path)
                        islocked = (branch, path) in locks
                        if islocked:
                            # update lock timestamp
                            errmsg = setremotelock(ui, remote, self, ctx,
                                                   branch, path,
                                                   addr, date, force=False)
                            if errmsg:
                                report(ui, match, path,
                                       "%s: %s" % (path, errmsg))
                            else:
                                self.ui.note(_("updated lock timestamp for %s\n")
                                             % path)
                                filtered.append(path)
                        else:
                            # not locked
                            if mustlock:
                                report(ui, match, path,
                                       _("%s: file has been modified without "
                                         "being locked, while locking is "
                                         "mandatory for this file") % path,
                                       hint=_("to commit the file, revert "
                                              "and then lock it"))
                            else:
                                filtered.append(path)

                    status[:] = filtered
                return changes

            def commit(self, *args, **kwargs):
                # flip status switch
                self._hide_unlocked = True
                try:
                    return super(lockrepo, self).commit(*args, **kwargs)
                finally:
                    self._hide_unlocked = False
        repo.__class__ = lockrepo


def extsetup(ui):
    pushkey.register('locks', nullpush, listlocks)
    pushkey.register('locks-cmd', dispatchcmd, nulllist)
    extensions.wrapcommand(hgcmds.table, 'update', update)
    extensions.wrapcommand(hgcmds.table, 'push', push)


cmdtable = {
    "init-lock":
        (initlock,
         [],
         _('hg init-lock')),
    "locks":
        (locks,
         [('b', 'branch', [],
           _('show only locks on a specific branch'), _('BRANCH'))],
         _('hg locks [OPTIONS]')),
    "lock":
        (lock,
         [('f', 'force', None, _('steal lock'))],
         _('hg lock FILE... [OPTIONS]')),
    "unlock":
        (unlock,
         [('f', 'force', None, _('steal lock'))],
         _('hg unlock FILE... [OPTIONS]')),
}
