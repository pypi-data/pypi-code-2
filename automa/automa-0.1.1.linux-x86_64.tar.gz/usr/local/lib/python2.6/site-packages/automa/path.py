# -*- coding: utf-8 -*-

import os
import sys
import shutil
import fnmatch

try:
    import jinja2
    _has_jinja2 = True
except ImportError:
    _has_jinja2 = False

from automa import log

def _guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

if _has_jinja2:
    class _TemplatePathLoader(jinja2.BaseLoader):
        def __init__(self, encoding='utf-8'):
            self.encoding = encoding

        def get_source(self, environment, template):
            if not os.path.exists(template):
                raise jinja2.TemplateNotFound(template)
            mtime = os.path.getmtime(template)
            with file(template) as f:
                source = f.read().decode(self.encoding)
            def uptodate():
                try:
                    return os.path.getmtime(template) == mtime
                except OSError:
                    return False
            return source, template, uptodate

class Path(object):
    def __init__(self, pathname_or_path):
        if isinstance(pathname_or_path, Path):
            self.pathname = pathname_or_path.pathname
        else:
            self.pathname = pathname_or_path

    def __str__(self):
        return self.pathname

    def __repr__(self):
        return "<Path pathname:%r>" % self.pathname

    # ------------------------------------------------------------------------
    #   os.path wrappers
    # ------------------------------------------------------------------------

    @property
    def abspath(self):
        return Path(os.path.abspath(self.pathname))

    @property
    def basename(self):
        return os.path.basename(self.pathname)

    @property
    def dirname(self):
        return Path(os.path.dirname(self.pathname))

    @property
    def exists(self):
        return os.path.exists(self.pathname)

    @property
    def lexists(self):
        return os.path.lexists(self.pathname)

    @property
    def expanduser(self):
        return Path(os.path.expanduser(self.pathname))

    @property
    def expandvars(self):
        return Path(os.path.expandvars(self.pathname))

    @property
    def atime(self):
        return os.path.getatime(self.pathname)
    @property
    def ctime(self):
        return os.path.getctime(self.pathname)
    @property
    def mtime(self):
        return os.path.getmtime(self.pathname)

    @property
    def size(self):
        return os.path.getsize(self.pathname)

    @property
    def isabs(self):
        return os.path.isabs(self.pathname)

    @property
    def isfile(self):
        return os.path.isfile(self.pathname)

    @property
    def isdir(self):
        return os.path.isdir(self.pathname)

    @property
    def islink(self):
        return os.path.islink(self.pathname)

    @property
    def ismount(self):
        return os.path.ismount(self.pathname)

    @property
    def normcase(self):
        return Path(os.path.normcase(self.pathname))

    @property
    def normpath(self):
        return Path(os.path.normpath(self.pathname))

    @property
    def normalized(self):
        return Path(os.path.normcase(os.path.normpath(self.pathname)))

    def normalize(self):
        self.pathname = os.path.normcase(os.path.normpath(self.pathname))
        return self

    @property
    def realpath(self):
        return Path(os.path.realpath(self.pathname))

    @property
    def relpath(self):
        return Path(os.path.relpath(self.pathname))

    def split(self):
        t = os.path.split(self.pathname)
        return (Path(t[0]), t[1])

    def join(self, other):
        if isinstance(other, Path):
            return Path(os.path.join(self.pathname, other.pathname))
        return Path(os.path.join(self.pathname, other))

    def splitext(self):
        t = os.path.splitext(self.pathname)
        return (Path(t[0]), t[1])

    @property
    def ext(self):
        t = os.path.splitext(self.pathname)
        ext = t[1]
        if ext and ext.startswith('.'):
            ext = ext[1:]
        return ext

    def samefile(self, other):
        if not isinstance(other, Path):
            other = Path(other)
        return os.path.samefile(self.pathname, other.pathname)

    def same(self, other):
        if not isinstance(other, Path):
            other = Path(other).normalize()
        this = self.normalized
        return (this.pathname == other.pathname)

    def __eq__(self, other):
        if isinstance(other, Path):
            return self.pathname == other.pathname
        return False

    def __add__(self, other):
        return self.join(other)

    def __div__(self, other):
        return self.join(other)

    def __abs__(self):
        return self.abspath

    def __coerce__(self, other):
        if isinstance(other, basestring):
            return (self, Path(other))
        elif isinstance(other, Path):
            return (self, other)
        return None

    def __iter__(self):
        fh = self.open()
        return fh

    # ------------------------------------------------------------------------
    #   os wrappers
    # ------------------------------------------------------------------------

    def chdir(self):
        try:
            os.chdir(self.pathname)
        except Exception, exc:
            log.error("executing os.chdir(%r)" % self.pathname)
        return self

    def access(self, mode):
        return os.access(self.pathname, mode)

    def chroot(self):
        try:
            os.chroot(self.pathname)
        except Exception, exc:
            log.error("executing os.chroot(%r)" % self.pathname)
        return self

    def chflags(self, flags):
        try:
            os.chflags(self.pathname, flags)
        except Exception, exc:
            log.error("executing os.chflags(%r, %r)" % (self.pathname, flags))
        return self

    def lchflags(self, flags):
        try:
            os.lchflags(self.pathname, flags)
        except Exception, exc:
            log.error("executing os.lchflags(%r, %r)" % (self.pathname, flags))
        return self

    def chmod(self, mode):
        try:
            os.chmod(self.pathname, mode)
        except Exception, exc:
            log.error("executing os.chmod(%r, %r)" % (self.pathname, mode))
        return self

    def lchmod(self, mode):
        try:
            os.lchmod(self.pathname, mode)
        except Exception, exc:
            log.error("executing os.lchmod(%r, %r)" % (self.pathname, mode))
        return self

    def chown(self, uid, gid):
        try:
            os.chown(self.pathname, uid, gid)
        except Exception, exc:
            log.error("executing os.chown(%r, %r, %r)" % (self.pathname, uid, gid))
        return self

    def lchown(self, uid, gid):
        try:
            os.lchown(self.pathname, uid, gid)
        except Exception, exc:
            log.error("executing os.lchown(%r, %r, %r)" % (self.pathname, uid, gid))
        return self

    def link(self, link_name):
        try:
            os.link(self.pathname, link_name)
        except Exception, exc:
            log.error("executing os.link(%r, %r)" % (self.pathname, link_name))
        return self

    def listdir(self):
        try:
            l = os.listdir(self.pathname)
        except Exception, exc:
            log.error("executing os.listdir(%r)" % self.pathname)
        else:
            for entry in l:
                yield entry

    def mkdir(self, mode=0777):
        try:
            os.mkdir(self.pathname, mode)
        except Exception, exc:
            log.error("executing os.mkdir(%r, %r)" % (self.pathname, mode))
        return self

    def makedirs(self, mode=0777):
        try:
            os.makedirs(self.pathname, mode)
        except Exception, exc:
            log.error("executing os.makedirs(%r, %r)" % (self.pathname, mode))
        return self

    @property
    def readlink(self):
        try:
            return os.readlink(self.pathname)
        except Exception, exc:
            log.error("executing os.readlink(%r)" % self.pathname)
        return None

    def remove(self):
        try:
            os.remove(self.pathname)
        except Exception, exc:
            log.error("executing os.remove(%r)" % self.pathname)
        return self

    def rename(self, dst):
        if not isinstance(dst, Path):
            dst = Path(dst)
        try:
            os.rename(self.pathname, dst.pathname)
        except Exception, exc:
            log.error("executing os.rename(%r, %r)" % (self.pathname, dst.pathname))
        return self

    def renames(self, dst):
        if not isinstance(dst, Path):
            dst = Path(dst)
        try:
            os.renames(self.pathname, dst.pathname)
        except Exception, exc:
            log.error("executing os.renames(%r, %r)" % (self.pathname, dst.pathname))
        return self

    def rmdir(self):
        try:
            os.rmdir(self.pathname)
        except Exception, exc:
            log.error("executing os.rmdir(%r)" % self.pathname)
        return self

    @property
    def stat(self):
        try:
            return os.stat(self.pathname)
        except Exception, exc:
            log.error("executing os.stat(%r)" % self.pathname)
        return None

    @property
    def lstat(self):
        try:
            return os.lstat(self.pathname)
        except Exception, exc:
            log.error("executing os.stat(%r)" % self.pathname)
        return None

    def symlink(self, link_name):
        try:
            os.symlink(self.pathname, link_name)
        except Exception, exc:
            log.error("executing os.symlink(%r, %r)" % (self.pathname, link_name))
        return self

    def unlink(self):
        try:
            os.unlink(self.pathname)
        except Exception, exc:
            log.error("executing os.unlink(%r)" % self.pathname)
        return self

    # ------------------------------------------------------------------------
    #   file read & write helpers
    # ------------------------------------------------------------------------

    def read(self, mode='rb', encoding=None):
        try:
            fh = open(self.pathname, mode)
        except Exception, exc:
            log.error("executing open(%r, %r)" % (self.pathname, mode))
            return ""
        r = fh.read()
        fh.close()
        if encoding is not None:
            r = r.decode(encoding)
        return r

    def readlines(self, mode='r', encoding='utf-8'):
        try:
            fh = open(self.pathname, mode)
        except Exception, exc:
            log.error("executing open(%r, %r)" % (self.pathname, mode))
            return []
        r = fh.readlines()
        fh.close()
        if encoding is not None:
            r = [line.decode(encoding) for line in r]
        return r

    def write(self, text, mode='wb'):
        try:
            fh = open(self.pathname, mode)
        except Exception, exc:
            log.error("executing open(%r, %r)" % (self.pathname, mode))
            return self
        fh.write(text)
        fh.close()
        return self

    def writelines(self, lines, mode='w'):
        return self.write("\n".join(lines), mode=mode)

    def open(self, mode='r'):
        try:
            return open(self.pathname, mode)
        except Exception, exc:
            log.error("executing open(%r, %r)" % (self.pathname, mode))
        return None

    # ------------------------------------------------------------------------
    #   shutil wrappers and various helpers
    # ------------------------------------------------------------------------

    def copy(self, dst):
        if not isinstance(dst, Path):
            dst = Path(dst)
        try:
            shutil.copy(self.pathname, dst.pathname)
        except Exception, exc:
            log.error("executing shutil.copy(%r, %r)" % (self.pathname, dst.pathname))
        return self

    def copy_with_perms(self, dst):
        if not isinstance(dst, Path):
            dst = Path(dst)
        try:
            shutil.copy2(self.pathname, dst.pathname)
        except Exception, exc:
            log.error("executing shutil.copy2(%r, %r)" % (self.pathname, dst.pathname))
        return self

    def copy_contents(self, dst):
        if not isinstance(dst, Path):
            dst = Path(dst)
        try:
            shutil.copyfile(self.pathname, dst.pathname)
        except Exception, exc:
            log.error("executing shutil.copyfile(%r, %r)" % (self.pathname, dst.pathname))
        return self

    def move(self, dst):
        if not isinstance(dst, Path):
            dst = Path(dst)
        try:
            shutil.move(self.pathname, dst.pathname)
        except Exception, exc:
            log.error("executing shutil.move(%r, %r)" % (self.pathname, dst.pathname))
        return self

    def copytree(self, dst, symlinks=True, ignore=None):
        if not isinstance(dst, Path):
            dst = Path(dst)
        try:
            shutil.copytree(self.pathname, dst.pathname, symlinks=symlinks,
                            ignore=ignore)
        except Exception, exc:
            log.error("executing shutil.copytree(%r, %r)" % (self.pathname, dst.pathname))
        return self

    def rmtree(self, ignore_errors=False):
        try:
            shutil.rmtree(self.pathname)
        except Exception, exc:
            log.error("executing shutil.rmtree(%r)" % self.pathname)
        return self

    # ------------------------------------------------------------------------
    #   various helpers
    # ------------------------------------------------------------------------

    def startswith(self, text):
        return self.pathname.startswith(text)
    def endswith(self, text):
        return self.pathname.endswith(text)

    def walkfiles(self, pattern="*"):
        try:
            l = os.listdir(self.pathname)
        except Exception, exc:
            log.error("executing os.listdir(%r)" % self.pathname)
        else:
            for entry in l:
                if fnmatch.fnmatch(entry, pattern):
                    yield Path(os.path.join(self.pathname, entry))

    @classmethod
    def _get_template(cls, template_path, encoding='utf-8'):
        from opts import options
        if not _has_jinja2:
            log.error("jinja2 is not installed")
            return None
        if not isinstance(template_path, Path):
            template_path = Path(template_path)
        loader = _TemplatePathLoader(encoding=encoding)
        environment = jinja2.Environment(autoescape=_guess_autoescape,
                                         loader=loader,
                                         extensions=['jinja2.ext.autoescape'])
        environment.globals = options
        return environment.get_template(template.pathname)

    def render_to_string(self, context={}, encoding='utf-8'):
        tpl = Path._get_template(self, encoding)
        return tpl.render(context)

    def render_from_string(self, template, context={}, encoding='utf-8'):
        from opts import options
        if not _has_jinja2:
            log.error("jinja2 is not installed")
            return None
        tpl = jinja2.Template(template,
                              autoescape=_guess_autoescape,
                              extensions=['jinja2.ext.autoescape'])
        tpl.globals = options
        return self.write(tpl.render(context))

    def render_to(self, dst, context={}, encoding='utf-8'):
        if not isinstance(dst, Path):
            dst = Path(dst)
        tpl = Path._get_template(self, encoding)
        return dst.write(tpl.render(context))

    def render_from(self, template, context={}, encoding='utf-8'):
        tpl = Path._get_template(template, encoding)
        return self.write(tpl.render(context))
