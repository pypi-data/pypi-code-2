# -*- coding: utf-8 -*-
import os
import re
import sys
import time
import gzip
import shutil
import random
import urllib
import urllib2

try:
    import json
except ImportError:
    import simplejson as json
import markdown
import markdown.extensions.tables  # for py2exe

import trans
import utils

#~ if sys.platform in ['win32', 'cygwin']:
    #~ PADS_DIR = os.path.join(os.path.abspath(
        #~ utils.module_path()), 'pads.zenpad')
#~ else:
    #~ PADS_DIR = os.path.expanduser('~/pads.zenpad')
PADS_DIR = os.path.expanduser('~/pads.zenpad')
if __name__ == '__main__':
    PADS_DIR = 'var/tests/pad_class/root'  # for tests
AUTO_SLUG = 'new-page'
SYNC_URL = 'http://zenpad.ru/sync%s'
if len(sys.argv) == 2 and sys.argv[1] == 'test':
    SYNC_URL = 'http://localhost:8000/sync%s'


class PageNotFound(Exception): pass
class DirExists(Exception): pass
class BadPagePath(Exception): pass
class CanNotBeMoved(Exception): pass
class SyncError(Exception): pass

HTML_CONVERTERS = (
    ('markdown', lambda text: markdown.markdown(text, ['tables'])),
    ('plain text', utils.plaintext2html),
)


class Page(object):
    DIR_RE = re.compile(r'^[0-9A-Za-z\-]+$')
    PATH_RE = re.compile(r'^/([0-9A-Za-z\-]+/)*$')

    def __init__(self, root, path, content='', encoding='utf-8', gz=False):
        self.root = os.path.abspath(root)
        if self.is_avalible_path(path):
            self.path = path
        else:
            raise BadPagePath(u'bad page path: %s' % path)
        self.content = content
        self.encoding = encoding
        self.gz = gz
        self.file_ext = 'txt.gz' if self.gz else 'txt'
        self._title = None

    @classmethod
    def load(cls, *args, **kwargs):
        page = cls(*args, **kwargs)
        page._content = None
        if not os.path.isfile(page.filename):
            if page.path == '/':
                # create root page
                page.content = ''
            elif page.has_childs():
                # childs dir is exists, create default page
                page.content = ''
            else:
                raise PageNotFound(u'page not found: %s' % page.path)
            page.save()
        return page

    def save(self):
        if os.path.dirname(self.filename) == os.path.dirname(PADS_DIR):
            # HACK: not save beyond PADS_DIR
            return
        if (self.basename.startswith(AUTO_SLUG) and not self.has_childs()
                and (not os.path.exists(self.filename)
                    or not os.path.getsize(self.filename))):
            # first save auto-page
            try:
                index = self.load_config().__order__.index(self.basename)
            except ValueError:
                index = None
            if self.set_basename_by_title() and index is not None:
                cfg = self.load_config()
                cfg.__order__.insert(index, self.basename)
                cfg.save()
        dirname = os.path.dirname(self.filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        opener = gzip.open if self.gz else open
        file = opener(self.filename, 'w')
        file.write(self.content.encode(self.encoding))
        file.close()
        cfg = self.load_config()
        if self.basename not in cfg.__order__:
            cfg.__order__.append(self.basename)
            cfg.save()

    def set_basename_by_title(self):
        ''' 
            >>> root = 'var/tests/page_class/root'
            >>> p = Page(root, '/%s/' % AUTO_SLUG)
            >>> p.content = u'Foo'
            >>> p.save()
            >>> p.basename
            u'foo'
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        if self.path != '/' and self.content.strip():
            basename = name = ''.join([ch if self.DIR_RE.match(ch) else '-'
                for ch in self.title.encode('trans').lower()])
            if basename:
                self.delete()
                i = 1
                dir_list = self.dir_list[:-1]
                while 1:
                    self.path = self.path_as_str(dir_list + [basename])
                    if not os.path.exists(self.filename):
                        break
                    basename = '%s-%s' % (name, i)
                    i += 1
                return True
            
    def delete(self):
        if os.path.exists(self.filename):
            os.unlink(self.filename)
            if self.has_childs():
                shutil.rmtree(self.childs_dirname)
        cfg = self.load_config()
        cfg.pop(self.basename, None)
        if self.basename in cfg.__order__:
            cfg.__order__.remove(self.basename)
        cfg.save()

    @property
    def slug(self):
        return self.dir_list[-1]

    @property
    def basename(self):
        return self.dir_list[-1] or str(os.path.basename(self.root))

    @property
    def content(self):
        if self._content is None:
            file = gzip.open(self.filename) if self.gz else open(self.filename)
            self._content = file.read().decode(self.encoding)
            file.close()
        return self._content
        
    @content.setter
    def content(self, value):
        self._content = unicode(value)
    
    def content_html(self, converter=None):
        return dict(HTML_CONVERTERS)[converter](self.content)

    @property
    def title(self):
        ''' 
            >>> root = 'var/tests/page_class/root'
            >>> p = Page(root, '/')
            >>> p.save()
            >>> p = Page.load(root, '/')
            >>> p.title
            'root'
            >>> p.content = '\t# Title'
            >>> p.save()
            >>> p = Page.load(root, '/')
            >>> p.title
            u'Title'
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        if self._content is not None:
            title = self._content.lstrip(' #\n\r\t').split('\n', 1)[0].rstrip()
        else:
            if self._title is None:
                opener = gzip.open if self.gz else open
                file = opener(self.filename)
                for row in file:
                    row = row.lstrip(' #\n\r\t').rstrip()
                    if row:
                        self._title = row.decode(self.encoding)
                        break
                file.close()
            title = self._title
        if not title:
            title = self.basename
        return title

    @property
    def filename(self):
        return '%s.%s' % (
            os.path.join(self.root, *self.dir_list[1:]), self.file_ext)

    @property
    def childs_dirname(self):
        return self.filename[:-len(self.file_ext) - 1]
    
    def has_childs(self):
        return os.path.exists(self.childs_dirname)

    @property
    def dir_list(self):
        return self.path_as_list(self.path)
    
    @property
    def index(self):
        cfg = self.load_config()
        if self.basename in cfg.__order__:
            return cfg.__order__.index(self.basename)

    @staticmethod
    def is_avalible_dir(dir):
        '''
        Alnum and dash only
            >>> [Page.is_avalible_dir(d) for d in ['', ' ', 'a_b', 'aaa-111']]
            [False, False, False, True]
        '''
        return bool(Page.DIR_RE.match(dir))

    @staticmethod
    def is_avalible_path(path):
        '''
            >>> [Page.is_avalible_path(p) for p in [
            ...     '', '//', 'aa', '/aa', 'aa/', '/a_b/']]
            [False, False, False, False, False, False]
            
            >>> [Page.is_avalible_path(p) for p in ['/', '/a-b/1-2-3/']]
            [True, True]
        '''
        return bool(Page.PATH_RE.match(path))

    @staticmethod
    def path_as_list(path_str):
        '''
        >>> Page.path_as_list('/')
        ['']
        >>> Page.path_as_list('/aaa/bbb/')
        ['', 'aaa', 'bbb']
        '''
        return path_str.rstrip('/').split('/')

    @staticmethod
    def path_as_str(path_list):
        '''
        >>> for path in ['/', '/aaa/', '/aaa/bbb/1-2-3/']:
        ...     dir_list = Page.path_as_list(path)
        ...     Page.path_as_str(dir_list) == path
        True
        True
        True
        '''
        return '/'.join(path_list) + '/'

    def move_to(self, path, index=None):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> Page(root, '/aaa/').save()
            >>> Page(root, '/bbb/ccc/').save()
            >>> p = Page(root, '/aaa/ddd/')
            >>> p.save()
            >>> p.move_to('/bbb/eee/', 0)
            >>> [p.basename for p  in Page.load(root, '/aaa/').get_childs()]
            []
            >>> [p.basename for p  in Page.load(root, '/bbb/').get_childs()]
            ['eee', 'ccc']
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        if not self.is_avalible_path(path):
            raise BadPagePath(u'bad page path: %s' % path)
        if self.path == '/':
            raise CanNotBeMoved
        if path.startswith(self.path) and path != self.path:
            # move to subtree
            raise CanNotBeMoved
        page = Page(self.root, path, encoding=self.encoding, gz=self.gz)
        new_parent = page.get_parent()
        siblings_basenames = [p.basename for p in new_parent.get_childs()]
        if page.basename in siblings_basenames and path != self.path:
            raise DirExists
        if self.path != path:
            # move files
            new_dir = new_parent.childs_dirname
            if not new_parent.has_childs():
                os.makedirs(new_dir)
            if self.has_childs():
                shutil.move(self.childs_dirname, os.path.join(
                    new_dir, page.basename))
            shutil.move(self.filename, os.path.join(
                new_dir, '%s.%s' % (page.basename, page.file_ext)))
        # src config
        cfg = self.load_config()
        page_cfg = cfg.pop(self.basename, None)
        if page_cfg or self.basename in cfg.__order__:
            if self.basename in cfg.__order__:
                cfg.__order__.remove(self.basename)
            cfg.save()
            
        # dst config
        cfg = page.load_config()
        index = index if index is not None else len(cfg.__order__)
        cfg.__order__.insert(index, page.basename)
        if page_cfg:
            cfg[page.basename] = page_cfg
        cfg.save()
        
        self.path = path
    
    def move_up(self):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> Page(root, '/aaa/').save()
            >>> Page(root, '/bbb/').save()
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['aaa', 'bbb']
            >>> Page.load(root, '/bbb/').move_up()
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['bbb', 'aaa']
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        index = self.index
        if index:
            self.move_to(self.path, index - 1)

    def move_down(self):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> Page(root, '/aaa/').save()
            >>> Page(root, '/bbb/').save()
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['aaa', 'bbb']
            >>> Page.load(root, '/aaa/').move_down()
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['bbb', 'aaa']
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        cfg = self.load_config()
        order = cfg.__order__
        index = order.index(self.basename)
        if index + 1 < len(order):
            self.move_to(self.path, index + 1)

    def move_left(self):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> Page(root, '/aaa/').save()
            >>> Page(root, '/bbb/').save()
            >>> Page(root, '/bbb/ccc/').save()
            >>> Page(root, '/ddd/').save()
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['aaa', 'bbb', 'ddd']
            >>> Page.load(root, '/bbb/ccc/').move_left()
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['aaa', 'bbb', 'ccc', 'ddd']
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        parent = self.get_parent()
        new_parent = parent.get_parent()
        if new_parent:
            path = self.path_as_str(new_parent.dir_list + [self.basename])
            self.move_to(path, parent.index + 1)
    
    def move_right(self):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> Page(root, '/aaa/').save()
            >>> Page(root, '/aaa/bbb/').save()
            >>> Page(root, '/ccc/').save()
            >>> [p.basename for p  in Page.load(root, '/aaa/').get_childs()]
            ['bbb']
            >>> Page.load(root, '/ccc/').move_right()
            >>> [p.basename for p  in Page.load(root, '/aaa/').get_childs()]
            ['bbb', 'ccc']
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        cfg = self.load_config()
        order = cfg.__order__
        index = order.index(self.basename)
        if index:
            new_parent_name = order[index - 1]
            path = self.path_as_str(
                self.dir_list[:-1] + [new_parent_name, self.basename])
            self.move_to(path)
        
    def change_basename(self, new_basename):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> Page(root, '/aaa/').save()
            >>> Page(root, '/bbb/').save()
            >>> Page(root, '/ccc/').save()
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['aaa', 'bbb', 'ccc']
            >>> Page.load(root, '/bbb/').change_basename('ddd')
            >>> [p.basename for p  in Page.load(root, '/').get_childs()]
            ['aaa', 'ddd', 'ccc']
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        if self.basename != new_basename:
            path = self.path_as_str(self.dir_list[:-1] + [new_basename])
            self.move_to(path, self.index)
        
    def load_config(self):
        ext = 'json.gz' if self.gz else 'json'
        filename = os.path.join(
            os.path.dirname(self.filename), 'config.%s' % ext)
        ret = JsonDict(filename, gz=self.gz).load()
        ret.setdefault('__order__', [])
        return ret
    
    def get_parent(self):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> Page(root, '/aaa/').save()
            >>> Page(root, '/aaa/bbb/').save()
            >>> Page.load(root, '/').get_parent()
            >>> Page.load(root, '/aaa/').get_parent().basename
            'root'
            >>> Page.load(root, '/aaa/bbb/').get_parent().basename
            'aaa'
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        if self.path != '/':
            path = self.path_as_str(self.dir_list[:-1])
            return Page.load(self.root, path,
                encoding=self.encoding, gz=self.gz)

    def get_childs(self):
        '''
            >>> root = 'var/tests/page_class/root'
            >>> page = Page(root, '/')
            >>> page.save()
            
        No children:
            >>> page.get_childs()
            []
            >>> os.makedirs(page.childs_dirname)
            >>> page.get_childs()
            []
            
        Order by creation_time dir:
            >>> for i in xrange(5):
            ...     os.makedirs(os.path.join(page.childs_dirname, str(i)))
            ...     time.sleep(0.01)
            >>> [p.basename for p in page.get_childs()]
            ['0', '1', '2', '3', '4']
            >>> Page(root, '/5/').save()
            >>> [p.basename for p in page.get_childs()]
            ['0', '1', '2', '3', '4', '5']
            
        Order by config:
            >>> cfg = page.get_childs()[0].load_config()
            >>> cfg.__order__ = ['5', '4', '3', '2', '1']
            >>> cfg.save()
            >>> [p.basename for p in page.get_childs()]
            ['5', '4', '3', '2', '1', '0']
            
            >>> shutil.rmtree(os.path.dirname(root), ignore_errors=True)
        '''
        pages = []
        childs_dir = self.childs_dirname
        if os.path.isdir(childs_dir):
            # find all nested files and dirs
            items = []
            for name in os.listdir(childs_dir):
                full_name = os.path.join(childs_dir, name)
                if os.path.isfile(full_name):
                    if not name.endswith(self.file_ext):
                        continue
                    name = name[:-len(self.file_ext) - 1]
                elif os.path.isdir(full_name):
                    if os.path.isfile('%s.%s' % (full_name, self.file_ext)):
                        continue
                if not self.is_avalible_dir(name):
                    continue
                items.append((name, os.path.getctime(full_name)))
            if items:
                # sort by creation time
                items.sort(key=lambda x: x[1])
                pages = []
                for name, t in items:
                    path = '%s%s/' % (self.path, name)
                    page = Page.load(self.root, path,
                        encoding=self.encoding, gz=self.gz)
                    pages.append(page)
                # restore saved order
                cfg = pages[0].load_config()
                ordered = cfg.__order__
                items = []
                for page in pages:
                    name = page.basename
                    if name in ordered:
                        items.append((page, ordered.index(name)))
                    else:
                        items.append((page, pages.index(page) + len(ordered)))
                items.sort(key=lambda x: x[1])
                pages = [item[0] for item in items]
                names = [page.basename for page in pages]
                if set(ordered) != set(names):
                    cfg.__order__ = names
                    cfg.save()
        return pages
        
    def __unicode__(self):
        return self.title
    
    def __str__(self):
        return unicode(self).encode('utf-8')


class FilePad(Page):
    def __init__(self, name=None, root=None, **kwargs):
        '''
            >>> pad = FilePad('first')
            >>> pad.basename
            'first'
            >>> shutil.rmtree(os.path.dirname(PADS_DIR), ignore_errors=True)
        '''
        self.name = name
        path = '/%s/' % name if name else '/'
        super(FilePad, self).__init__(root or PADS_DIR, path, **kwargs)
        if name:
            if not os.path.exists(self.pages_root):
                os.makedirs(self.pages_root)
            cfg = FilePad.load_pads_config()
            cfg.__last_used__ = name
            cfg.save()
        self._content = None

    @property
    def pages_root(self):
        return os.path.join(self.root, self.name)

    @classmethod
    def load_pads_config(cls):
        return Page(PADS_DIR, '/aaa/').load_config()
    
    @classmethod
    def all_pads_names(cls):
        '''
            >>> pad = FilePad('first')
            >>> pad = FilePad('second')
            >>> FilePad.all_pads_names()
            ['first', 'second']
            >>> shutil.rmtree(os.path.dirname(PADS_DIR), ignore_errors=True)
        '''
        return [p.basename for p in cls().get_childs()]

    def create_page(self, path, content=''):
        return Page(self.pages_root, path, content,
            encoding=self.encoding, gz=self.gz)
    
    def load_page(self, path):
        '''
            >>> pad = FilePad('first')
            >>> pad.create_page('/aaa/').save()
            >>> pad.create_page('/bbb/').save()
            >>> [p.basename for p in pad.load_page('/').get_childs()]
            ['aaa', 'bbb']
            >>> shutil.rmtree(os.path.dirname(PADS_DIR), ignore_errors=True)
        '''
        return Page.load(self.pages_root, path,
            encoding=self.encoding, gz=self.gz)
    
    def get_free_child_path(self, parent):
        basename = AUTO_SLUG
        i = 1
        while True:
            path = Page.path_as_str(parent.dir_list + [basename])
            try:
                self.load_page(path)
            except PageNotFound:
                break
            basename = '%s-%s' % (AUTO_SLUG, i)
            i += 1
        else:
            raise Exception(u'can not find free child name for page:' % parent.path)
        return path

    def create_auto_child_page(self, page):
        '''
            >>> pad = FilePad('foo')
            >>> page = pad.create_page('/')
            >>> page.save()
            >>> pad.create_auto_child_page(page).save()
            >>> len(page.get_childs())
            1
            >>> shutil.rmtree(os.path.dirname(PADS_DIR), ignore_errors=True)
        '''
        path = self.get_free_child_path(page)
        return self.create_page(path)
        
    def create_auto_sibling_page(self, page):
        '''
            >>> pad = FilePad('foo')
            >>> page = pad.create_page('/aaa/')
            >>> page.save()
            >>> pad.create_auto_sibling_page(page).save()
            >>> len(pad.load_page('/').get_childs())
            2
            >>> shutil.rmtree(os.path.dirname(PADS_DIR), ignore_errors=True)
        '''
        parent = page.get_parent()
        if parent:
            path = self.get_free_child_path(parent)
            sibling = self.create_page(path)
            cfg = page.load_config()
            cfg['__order__'].insert(page.index + 1, sibling.basename)
            cfg.save()
            return sibling
    
    def sync_query(self, uri, **kwargs):
        if 'host' not in kwargs or 'code' not in kwargs:
            pad_cfg = self.load_pads_config().get(self.name)
            kwargs['host'] = kwargs.get('host', pad_cfg.get('host'))
            kwargs['code'] = kwargs.get('code', pad_cfg.get('access_code'))
        while True:
            if not kwargs['host'] or not kwargs['code']:
                data = {'error': 
                    u'Укажите домен и код доступа в настройках блокнота' +
                    u' (получить их можно на zenpad.ru).'}
                break
            try:
                #~ from om.pp import pp
                #~ pp(kwargs)
                kwargs['host'] = kwargs['host'].encode('idna')
                page = urllib2.urlopen(
                    SYNC_URL % uri, urllib.urlencode(kwargs)).read()
            except Exception, ex:
                data = {'error': u'Сервер временно недоступен.'}
                #~ data = {'error': str(ex)}
                break
            try:
                data = json.loads(page)
            except Exception:
                data = {'error': u'Ошибка сервера.'}
                break
            if not isinstance(data, dict):
                data = {'error': u'Ошибка сервера.'}
                break
            break
        if 'error' in data:
            raise SyncError(data['error'])
        return data
    
    def all_pages(self, page=None):
        '''
            >>> pad = FilePad('foo')
            >>> pad.create_page('/aaa/').save()
            >>> pad.create_page('/aaa/bbb/').save()
            >>> pad.create_page('/aaa/ccc/').save()
            >>> [c.path for c in pad.all_pages()]
            ['/', '/aaa/', '/aaa/bbb/', '/aaa/ccc/']
            >>> shutil.rmtree(os.path.dirname(PADS_DIR), ignore_errors=True)
        '''
        page = page or self.load_page('/')
        ret = [page]
        for child in page.get_childs():
            ret.extend(self.all_pages(child))
        return ret

    @property
    def html_converter(self):
        cfg = self.load_pads_config()
        pad_cfg = cfg.setdefault(self.name, {})
        return pad_cfg.get('converter', HTML_CONVERTERS[0][0])

class JsonDict(dict):
    def __init__(self, filename, enc='utf-8', gz=False, *args, **kwargs):
        super(JsonDict, self).__init__(*args, **kwargs)
        self.__dict__['enc'] = enc
        self.__dict__['filename'] = filename
        self.__dict__['gz'] = gz

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val

    def load(self):
        self.clear()
        opener = gzip.open if self.gz else open
        try:
            file = opener(self.filename)
        except IOError:
            pass
        else:
            self.update(json.loads(file.read().decode(self.enc)))
            file.close()
        return self

    def save(self):
        dir = os.path.dirname(self.filename)
        if not os.path.exists(dir):
            os.makedirs(dir)
        opener = gzip.open if self.gz else open
        json = str(self)
        file = opener(self.filename, 'w')
        file.write(json)
        file.close()
        
    def __str__(self):
        return json.dumps(dict(self), indent=1, sort_keys=True,
            ensure_ascii=False).encode(self.enc)


def main():
    pass


if __name__ == "__main__":
    #~ main()
    #~ return
    
    import doctest
    doctest.testmod()
