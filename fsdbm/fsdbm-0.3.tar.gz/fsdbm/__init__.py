#!/usr/bin/python
# -*- coding: utf-8 -*-
'''File System based DBM, suitable for large data (such as images).'''
import os
import shutil
import base64
import marshal
try:
    import cPickle as pickle
except:
    import pickle
try:
    from hashlib import md5
except ImportError:
    from md5 import md5


class FSDBM(object):
    '''
        >>> db = FSDBM('var/test.fdb')
        >>> db.clear()
        >>> db['a'] = {'a': range(10)}
        >>> db['a'] == {'a': range(10)}
        True
        >>> db['b'] = 1
        >>> len(db)
        2
        >>> del db['a']
        >>> db.keys()
        ['b']
        >>> db.clear()
        >>> len(db)
        0
    '''
    def __init__(self, db_dir, depth=1, dumper='marshal'):
        '''
            *db_dir:    db dir
            **depth:    dir depth
            **dumper:   marshal | pickle
        '''
        self.db_dir = db_dir
        self.depth = depth
        if dumper == 'marshal':
            self.dumper = marshal
        elif dumper == 'pickle':
            self.dumper = pickle
        else:
            assert 0, 'unknown dumper'

    def __getitem__(self, key):
        return self._get_file_dict(self.fn(key))[key]
        
    def __setitem__(self, key, value):
        data = self._get_file_dict(self.fn(key))
        data[key] = value
        self._put_file_dict(self.fn(key), data)
        
    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True

    def __delitem__(self, key):
        data = self._get_file_dict(self.fn(key))
        del data[key]
        if data:
            self._put_file_dict(self.fn(key), data)
        else:
            os.unlink(self.fn(key))
        
    def __iter__(self):
        return self.iterkeys()

    def get(self, k, default=None):
        try:
            return self.__getitem__(k)
        except KeyError:
            return default

    def __len__(self):
        cnt = 0
        for k in self:
            cnt += 1
        return cnt

    def iteritems(self):
        for root, dirs, files in os.walk(self.db_dir):
            for fn in files:
                fn = os.path.join(root, fn)
                for k, v in self._get_file_dict(fn).iteritems():
                    yield (k, v)

    def iterkeys(self):
        for k, v in self.iteritems():
            yield k        

    def itervalues(self):
        for k, v in self.iteritems():
            yield v       
            
    def clear(self):
        shutil.rmtree(self.db_dir, ignore_errors=True)
        
    def keys(self):
        return list(self.iterkeys())
        
    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())

    def fn(self, key):
        hash = md5(key).hexdigest()
        path = [self.db_dir]
        for i in xrange(-1 - self.depth * 2, -1, 2):
            path.append(hash[i:i+2])
        path.append(hash)
        return os.path.join(*path)
        
    def _get_file_dict(self, fn):
        try:
            f = open(fn, 'rb')
        except IOError:
            return {}
        try:
            return self.dumper.load(f)
        except (EOFError, ValueError, TypeError):
            return {}
        finally:
            f.close()

    def _put_file_dict(self, fn, data):
        try:
            f = open(fn, 'wb')
        except IOError:
            try:
                os.makedirs(os.path.dirname(fn))
            except OSError:
                pass
            f = open(fn, 'wb')
        try:
            self.dumper.dump(data, f)
        except ValueError:
            os.unlink(fn)
            raise
        finally:
            f.close()


class FSDBMLight(object):
    '''
    Only byte string key and value. Max key length = 190 bytes. 
        >>> db = FSDBMLight('var/test.fdb')
        >>> db.clear()
        >>> db['a'] = 'bbb'
        >>> db['a'] == 'bbb'
        True
        >>> db['b'] = '1'
        >>> len(db)
        2
        >>> del db['a']
        >>> db.keys()
        ['b']
        >>> db.clear()
        >>> len(db)
        0
    '''
    def __init__(self, db_dir, depth=1):
        self.db_dir = db_dir
        self.depth = depth
        
    def fn(self, k):
        '''Full file path by key'''
        if isinstance(k, unicode):
            k = k.encode('utf-8')
        hash = md5(k).hexdigest()
        dirs = [self.db_dir]
        for i in xrange(-1 - self.depth * 2, -1, 2):
            dirs.append(hash[i:i+2])
        dir = os.path.join(*dirs)
        return os.path.join(dir, base64.urlsafe_b64encode(k))

    def __getitem__(self, k):
        try:
            return open(self.fn(k)).read()
        except IOError:
            raise KeyError

    def __setitem__(self, k, v):
        fn = self.fn(k)
        try:
            f = open(fn, 'w')
        except IOError:
            try:
                os.makedirs(os.path.dirname(fn))
            except OSError:
                pass
            f = open(fn, 'w')
        f.write(v)
        f.close()

    def __contains__(self, k):
        if os.path.exists(self.fn(k)):
            return True
        return False

    def __delitem__(self, k):
        try:
            os.unlink(self.fn(k))
        except OSError:
            raise KeyError
        
    def __iter__(self):
        return self.iterkeys()

    def get(self, k, default=None):
        try:
            return self[k]
        except KeyError:
            return default

    def __len__(self):
        cnt = 0
        for root, dirs, files in os.walk(self.db_dir):
            cnt += len(files)
        return cnt

    def iterkeys(self):
        for root, dirs, files in os.walk(self.db_dir):
            for fn in files:
                k = base64.urlsafe_b64decode(fn)
                yield k

    def iteritems(self):
        for k in self.iterkeys():
            yield (k, self[k])

    def clear(self):
        shutil.rmtree(self.db_dir, ignore_errors=True)

    def keys(self):
        return list(self.iterkeys())
        
    def values(self):
        return list(self.itervalues())

    def items(self):
        return list(self.iteritems())


class FSDBMLightUnicode(FSDBMLight):
    '''
    Only unicode key and value. Max key length = 190 bytes. 
        >>> db = FSDBMLightUnicode('var/test.fdb')
        >>> db.clear()
        >>> db[u'a'] = u'bbb'
        >>> db[u'a'] == u'bbb'
        True
        >>> db[u'b'] = u'1'
        >>> len(db)
        2
        >>> del db[u'a']
        >>> db.keys()
        [u'b']
        >>> db.clear()
        >>> len(db)
        0
    '''
    def fn(self, k):
        '''Full file path by key'''
        return super(self.__class__, self).fn(k.encode('utf-8'))
        
    def __getitem__(self, k):
        try:
            return open(self.fn(k)).read().decode('utf-8')
        except IOError:
            raise KeyError

    def __setitem__(self, k, v):
        super(self.__class__, self).__setitem__(k, v.decode('utf-8'))
        
    def iterkeys(self):
        for k in super(self.__class__, self).iterkeys():
            yield k.decode('utf-8')


def recomended_depth(row_cnt, max_in_dir=5000):
    '''
    Возвращает рекомендованную вложенность папок
        *row_cnt:       предполагаемое количество элементов
        **max_in_dir:   максимальное количество файлов в папке
    '''
    depth = 0
    in_dir = float(row_cnt)
    while 1:
        if in_dir <= max_in_dir:
            break
        depth += 1
        in_dir /= 256
    return depth


if __name__ == "__main__":
    import doctest
    doctest.testmod()


