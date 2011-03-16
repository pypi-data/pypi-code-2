from StringIO import StringIO

from django.conf import settings
from django.test import TestCase

from django_dbstorage.models import File
from django_dbstorage.storage import DatabaseStorage


class FileTestCase(TestCase):
    def setUp(self):
        File.objects.all().delete()

    def test_init(self):
        f = File(name='hello.txt')
        self.assertEqual(f.name, 'hello.txt')
        self.assertEqual(f.data, '')
        self.assertEqual(f.closed, False)
        self.assertEqual(f.encoding, None)
        self.assertEqual(f.errors, None)
        self.assertEqual(f.mode, 'r+b')
        self.assertEqual(f.newlines, None)
        self.assertEqual(f.softspace, 0)

    def test_create(self):
        f = File.objects.create(name='hello.txt')
        self.assertEqual(f.name, 'hello.txt')
        self.assertEqual(f.data, '')
        self.assertEqual(f.closed, False)
        self.assertEqual(f.encoding, None)
        self.assertEqual(f.errors, None)
        self.assertEqual(f.mode, 'r+b')
        self.assertEqual(f.newlines, None)
        self.assertEqual(f.softspace, 0)

    def test_get(self):
        File.objects.create(name='hello.txt', data='Hello world!')
        f = File.objects.get(name='hello.txt')
        self.assertEqual(f.data, 'Hello world!')

    def test_unicode(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(repr(f), "<File: 'hello.txt', mode 'r+b'>")
        f.close()
        self.assertEqual(repr(f), "<File: closed 'hello.txt', mode 'r+b'>")

    def test_iter_next(self):
        data = ['Hello world!\n', 'Salut monde!\n']
        f = File.objects.create(name='hello.txt', data=''.join(data))
        for line, expected in zip(f, data):
            self.assertEqual(line, expected)

    def test_close(self):
        f = File.objects.create(name='hello.txt')
        self.assertFalse(f.closed)
        f.close()
        self.assertTrue(f.closed)
        self.assertRaises(ValueError, f.isatty)
        self.assertRaises(ValueError, f.seek, 0)
        self.assertRaises(ValueError, f.tell)
        self.assertRaises(ValueError, f.read)
        self.assertRaises(ValueError, f.readline)
        self.assertRaises(ValueError, f.readlines)
        self.assertRaises(ValueError, f.truncate)
        self.assertRaises(ValueError, f.write, '')
        self.assertRaises(ValueError, f.writelines, [''])
        self.assertRaises(ValueError, f.flush)

    def test_isatty(self):
        f = File.objects.create(name='hello.txt')
        self.assertFalse(f.isatty())

    def test_seek_tell(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f.tell(), 0)
        f.seek(5)
        self.assertEqual(f.tell(), 5)
        f.seek(3, 1)
        self.assertEqual(f.tell(), 8)
        f.seek(0, 2)
        self.assertEqual(f.tell(), 12)
        f.seek(-2, 2)
        self.assertEqual(f.tell(), 10)

    def test_read(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f.read(1), 'H')
        self.assertEqual(f.read(), 'ello world!')

    def test_readline(self):
        f = File.objects.create(name='hello.txt',
                                data='Hello world!\nSalut monde!\n')
        self.assertEqual(f.readline(), 'Hello world!\n')
        self.assertEqual(f.readline(), 'Salut monde!\n')

    def test_readlines(self):
        f = File.objects.create(name='hello.txt',
                                data='Hello world!\nSalut monde!\n')
        self.assertEqual(f.readlines(), ['Hello world!\n',
                                         'Salut monde!\n'])

    def test_truncate(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f.read(5), 'Hello')
        f.truncate()
        self.assertEqual(f.read(), '')
        f.seek(0)
        self.assertEqual(f.read(), 'Hello')
        f.seek(10)
        f.truncate(1)
        self.assertEqual(f.tell(), 10)
        f.seek(0)
        self.assertEqual(f.read(), 'H')

    def test_write(self):
        f = File.objects.create(name='hello.txt')
        f.write('Hello ')
        f.write('world!\n')
        print >>f, 'Salut monde!'
        f.flush()
        self.assertEqual(f.data, 'Hello world!\nSalut monde!\n')

    def test_flush(self):
        f = File.objects.create(name='hello.txt',
                                data='Hello world!\n')
        f.seek(0, 2)
        print >>f, 'Salut monde!'
        f.flush()
        f = File.objects.get(name='hello.txt')
        self.assertEqual(f.read(), 'Hello world!\nSalut monde!\n')

    def test_size(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        self.assertEqual(f._size(), 12)
        f.seek(5)
        f.truncate()
        self.assertEqual(f._size(), 5)

    def test_readonly(self):
        f = File.objects.create(name='hello.txt', data='Hello world!')
        f.mode = 'rb'
        self.assertFalse(f.isatty())
        self.assertEqual(f.tell(), 0)
        self.assertEqual(f.read(), 'Hello world!')
        f.seek(0)
        self.assertEqual(f.readline(), 'Hello world!')
        f.seek(0)
        self.assertEqual(f.readlines(), ['Hello world!'])
        self.assertRaises(IOError, f.truncate)
        self.assertRaises(IOError, f.write, '')
        self.assertRaises(IOError, f.writelines, [''])
        self.assertRaises(IOError, f.flush)


class DatabaseStorageTestCase(TestCase):
    def setUp(self):
        File.objects.all().delete()

    def test_init(self):
        s = DatabaseStorage()
        self.assertEqual(s.base_url, settings.MEDIA_URL)
        s = DatabaseStorage(base_url='/media/')
        self.assertEqual(s.base_url, '/media/')

    def test_open(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertRaises(IOError, s.open, name='hello.txt')
        s.save(name='hello.txt', content=content)
        f = s.open(name='hello.txt')
        self.assertEqual(f.read(), content.getvalue())
        self.assertRaises(IOError, f.truncate)
        f = s.open(name='hello.txt', mode='r+b')
        self.assertEqual(f.read(), content.getvalue())
        f.truncate()

    def test_save(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertRaises(IOError, s.save, name='', content=content)
        self.assertRaises(IOError, s.save, name='/', content=content)
        self.assertRaises(IOError, s.save, name='hello/', content=content)
        self.assertEqual(s.save(name='hello.txt', content=content),
                         'hello.txt')
        self.assertEqual(s.save(name='hello.txt', content=content),
                         'hello_.txt')
        self.assertEqual(s.save(name='/hello.txt', content=content),
                         'hello__.txt')
        self.assertEqual(s.save(name='/hello/goodbye.txt', content=content),
                         'hello/goodbye.txt')

    def test_get_available_name(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertEqual(s.get_available_name('hello.txt'), 'hello.txt')
        s.save(name='hello.txt', content=content)
        self.assertEqual(s.get_available_name('hello.txt'), 'hello_.txt')

    def test_delete(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        s.delete('hello.txt')
        s.save(name='hello.txt', content=content)
        s.delete('hello.txt')
        self.assertFalse(s.exists('hello.txt'))

    def test_exists(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertFalse(s.exists('hello.txt'))
        s.save(name='hello.txt', content=content)
        self.assertTrue(s.exists('hello.txt'))

    def test_listdir(self):
        content = StringIO('')
        english = StringIO('Hello world!')
        french = StringIO('Salut monde!')
        s = DatabaseStorage()
        self.assertEqual(s.listdir(''), ([], []))
        self.assertEqual(s.listdir('/'), ([], []))
        s.save(name='hello.txt', content=english)
        s.save(name='salut.txt', content=french)
        self.assertEqual(s.listdir(''), ([], ['hello.txt', 'salut.txt']))
        self.assertEqual(s.listdir('/'), ([], ['hello.txt', 'salut.txt']))
        s.save(name='hello/en.txt', content=english)
        s.save(name='hello/fr.txt', content=french)
        s.save(name='hello/docs/README', content=content)
        self.assertEqual(s.listdir(''), (['hello'],
                                         ['hello.txt', 'salut.txt']))
        self.assertEqual(s.listdir('/'), (['hello'],
                                          ['hello.txt', 'salut.txt']))
        self.assertEqual(s.listdir('hello'), (['docs'], ['en.txt', 'fr.txt']))
        self.assertEqual(s.listdir('/hello'), (['docs'], ['en.txt', 'fr.txt']))
        self.assertEqual(s.listdir('hello/docs'), ([], ['README']))
        self.assertEqual(s.listdir('/hello/docs'), ([], ['README']))
        self.assertRaises(OSError, s.listdir, 'goodbye')
        self.assertRaises(OSError, s.listdir, '/goodbye')

    def test_name(self):
        s = DatabaseStorage()
        self.assertEqual(s._name(''), '')
        self.assertEqual(s._name('/'), '')
        self.assertEqual(s._name('//'), '')
        self.assertEqual(s._name('hello'), 'hello')
        self.assertEqual(s._name('/hello'), 'hello')
        self.assertEqual(s._name('//hello'), 'hello')
        self.assertEqual(s._name('hello/'), 'hello/')
        self.assertEqual(s._name('hello//'), 'hello/')
        self.assertEqual(s._name('hello/goodbye'), 'hello/goodbye')
        self.assertEqual(s._name('hello//goodbye'), 'hello/goodbye')

    def test_size(self):
        content = StringIO('Hello world!')
        s = DatabaseStorage()
        self.assertRaises(IOError, s.size, name='hello.txt')
        s.save(name='hello.txt', content=content)
        self.assertEqual(s.size(name='hello.txt'), len(content.getvalue()))

    def test_url(self):
        s = DatabaseStorage()
        s.base_url = None
        self.assertRaises(ValueError, s.url, name='hello.txt')
        s = DatabaseStorage(base_url='/media/')
        self.assertEqual(s.url(name='hello.txt'), '/media/hello.txt')
        self.assertEqual(s.url(name='/hello.txt'), '/hello.txt')
