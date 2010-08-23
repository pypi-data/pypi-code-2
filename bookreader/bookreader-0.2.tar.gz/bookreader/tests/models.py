from os.path import dirname, join
import unittest

from django.utils.datastructures import MultiValueDict
from django.core.exceptions import ValidationError

from bookreader.models import *
from bookreader.signals import collection
from bookreader.signals import repository

from bookreader.tests import fakes



class BaseTest(unittest.TestCase):
    save_repository = False
    save_collection = False
    book_identifier = None
    
    def setUp(self):
        self.repository = Repository(url='http://dspace.institution.edu/dspace-oai/request')
        fakes.fake_repository_connection(self.repository, join(dirname(__file__),'oai'))
        if not self.save_repository:
            return
        self.repository.save()
        self.collection = Collection(repository=self.repository,
                                     handle='1969.1/6069')
        if not self.save_collection:
            return
        self.collection.save()
        if not self.book_identifier:
            return
        self.book = self.collection.books.get(identifier=self.book_identifier)
    
    def tearDown(self):
        Link.objects.all().delete()
        Page.objects.all().delete()
        Book.objects.all().delete()
        Collection.objects.all().delete()
        Repository.objects.all().delete()

class RepositoryTests(BaseTest):
    def testRepositoryName(self):
        """ Signal for setting repository name from OAI-PMH Identity """
        self.assertEqual(self.repository.name, '')
        self.repository.save()
        self.assertEqual(self.repository.name, u'The DSpace Repository')
    
    def testCollectionValidation(self):
        """ Collection handle validation """
        self.assert_(self.repository.validate_collection_handle('1969.1/6069'))
        self.assertFalse(self.repository.validate_collection_handle('1969.1/2500'))
        self.assertRaises(ValueError,
                          self.repository.validate_collection_handle,
                          12345)
    
    def testCollectionHarvesting(self):
        """ Collection handle harvesting """
        handles = self.repository.collection_handles
        self.assertEqual(len(handles), 3)
        self.assert_('hdl_1969.1_6069' in handles)
        self.assert_('hdl_1969.1_6459' in handles)
        self.assert_('hdl_1969.1_86400' in handles)

class CollectionTests(BaseTest):
    save_repository = True
    
    def testCollectionNameSignal(self):
        """ Signal for setting collection name from OAI-PMH ListSets """
        self.assertEqual(self.collection.name, '')
        self.collection.save()
        self.assertEqual(self.collection.name, 'Accomplishment Reports')
    
    def testBooksHarvestingSignal(self):
        """ Signal for harvesting books from OAI-PMH """
        self.assertEqual(self.collection.books.count(), 0)
        self.collection.save()
        self.assertEqual(self.collection.books.count(), 2)
        
        for book in self.collection.books.all():
            self.assert_(book.identifier in ('oai:dspace.institution.edu:1969.1/91216',
                                             'oai:dspace.institution.edu:1969.1/91217',))
    
    def testFieldCleaning(self):
        """ Collection handle validation on collection creation """
        self.collection.handle = 'invalid'
        self.assertRaises(ValidationError,
                          self.collection.clean_fields)

class BookTests(BaseTest):
    save_repository = True
    save_collection = True
    book_identifier = 'oai:dspace.institution.edu:1969.1/91216'
    
    def testPages(self):
        """ Signal for/harvesting of pages """
        self.assertEqual(self.book.pages.count(), 3)
        pages = self.book.pages.order_by('sequence').all()
        
        self.assertEqual(pages[0].title, 'pl_tamu_001_00712')
        self.assertEqual(pages[0].sequence, 1)
        self.assertEqual(pages[0].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/91216/pl_tamu_001_00712.jpf?sequence=2141')
        self.assertEqual(pages[0].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/91216/thumbs/pl_tamu_001_00712.jpg?sequence=2141')
        
        self.assertEqual(pages[1].title, 'pl_tamu_001_00713')
        self.assertEqual(pages[1].sequence, 2)
        self.assertEqual(pages[1].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/91216/pl_tamu_001_00713.jpf?sequence=2141')
        self.assertEqual(pages[1].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/91216/thumbs/pl_tamu_001_00713.jpg?sequence=2141')
        
        self.assertEqual(pages[2].title, 'pl_tamu_001_00714')
        self.assertEqual(pages[2].sequence, 3)
        self.assertEqual(pages[2].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/91216/pl_tamu_001_00714.jpf?sequence=2141')
        self.assertEqual(pages[2].thumbnail, None)
    
    def testLinks(self):
        """ Signal for/harvesting of links """
        self.assertEqual(self.book.links.count(), 1)
        link = self.book.links.all()[0]
        self.assertEqual(link.title, 'pl_tamu_001_Speculum')
        self.assertEqual(link.mimetype, 'application/pdf')
        self.assertEqual(link.size, 687936288)
        self.assertEqual(link.bundle, 'ORIGINAL')
        self.assertEqual(link.url, 'http://dspace.institution.edu/bitstream/handle/1969.1/91216/pl_tamu_001_Speculum.pdf?sequence=2142')
    
    def testHandle(self):
        """ Book handle extraction """
        self.assertEqual(self.book.handle, '1969.1/91216')
    
    def testRepositoryUrl(self):
        """ Book repository url extraction """
        self.assertEqual(self.book.repository_url,
                         'http://dspace.institution.edu/handle/1969.1/91216')

class BookMetadataTest(BaseTest):
    save_repository = True
    save_collection = True
    book_identifier = 'oai:dspace.institution.edu:1969.1/91216'
    metadata = {'title': 'Speculum 1',
                'creator': 'Pablos',
                'created': '1556',
                'issued': '2010-07-12 17:04:42',
                'thumbnail': 'http://dspace.institution.edu/bitstream/handle/1969.1/91216/thumbs/pl_tamu_001_00712.jpg?sequence=2141',
                'contributor': ['Cushing Memorial Library'],
                'publisher': ['Ocharte, Melchior, 1571-1616?'],
                'subject': ['Casuistry -- Early works to 1800',
                            'Confession -- Catholic Church -- Early works to 1800',
                            'Confession -- Catholic Church -- Handbooks, manuals, etc.'],
                'other subject': ['Evangelization of Mexican Indians',
                                  'Franciscan missionaries in Mexico',
                                  'Catholic Church'],
                'alternate title': ['Confessionario en lengua mexicana y castellana',
                                    'Confessionario en leng. mex. ycas.'],
                'description': ['49-112, [2] leaves : ill. ; 15 cm.(16mo)',
                                'Original imperfect: Initial unfoliated 16 leaves (including t.p.), everything prior to fol. 49, andd fols. 50, 55, 73, 105 (index) and the final three leaves (index and colophon) wanting'],
                'offset': ['4'],
                'offset_reading': False}
    
    def testTitleHarvesting(self):
        """ Book title harvested """
        self.assertEqual(self.book.title, self.metadata['title'])
    
    def testCreatorHarvesting(self):
        """ Book creator harvested """
        self.assertEqual(self.book.creator, self.metadata['creator'])
    
    def testCreatedHarvesting(self):
        """ Book created harvesting """
        self.assertEqual(self.book.created, self.metadata['created'])
    
    def testIssuedHarvesting(self):
        """ Book issued harvesting """
        self.assertEqual(str(self.book.issued), self.metadata['issued'])
    
    def testThumbnailHarvesting(self):
        """ Book thumbnail harvesting """
        self.assertEqual(self.book.thumbnail, self.metadata['thumbnail'])
    
    def testContributorHarvesting(self):
        """ Book contributor harvesting """
        if 'contributor' in self.metadata:
            for value in self.book.additional_metadata.getlist('contributor'):
                self.assert_(value in self.metadata['contributor'],
                             '%s not in %s' % (value, str(self.metadata['contributor']),))
            
            self.assertEqual(len(self.book.additional_metadata.getlist('contributor')),
                             len(self.metadata['contributor']))
    
    def testPublisherHarvesting(self):
        """ Book publisher harvesting """
        if 'publisher' in self.metadata:
            for value in self.book.additional_metadata.getlist('publisher'):
                self.assert_(value in self.metadata['publisher'],
                             '%s not in %s' % (value, str(self.metadata['publisher']),))
            
            self.assertEqual(len(self.book.additional_metadata.getlist('publisher')),
                             len(self.metadata['publisher']))
    
    def testSubjectHarvesting(self):
        """ Book subject harvesting """
        if 'subject' in self.metadata:
            for value in self.book.additional_metadata.getlist('subject'):
                self.assert_(value in self.metadata['subject'],
                             '%s not in %s' % (value, str(self.metadata['subject']),))
            
            self.assertEqual(len(self.book.additional_metadata.getlist('subject')),
                             len(self.metadata['subject']))
        
    def testSubjectOtherHarvesting(self):
        """ Book other subject harvesting """
        if 'other subject' in self.metadata:
            for value in self.book.additional_metadata.getlist('other subject'):
                self.assert_(value in self.metadata['other subject'],
                             '%s not in %s' % (value, str(self.metadata['other subject']),))
            
            self.assertEqual(len(self.book.additional_metadata.getlist('other subject')),
                             len(self.metadata['other subject']))
    
    def testAlternateTitleHarvesting(self):
        """ Book alternate title harvesting """
        if 'alternate title' in self.metadata:
            for value in self.book.additional_metadata.getlist('alternate title'):
                self.assert_(value in self.metadata['alternate title'],
                             '%s not in %s' % (value, str(self.metadata['alternate title']),))
            
            self.assertEqual(len(self.book.additional_metadata.getlist('alternate title')),
                             len(self.metadata['alternate title']))
        
    def testDescriptionHarvesting(self):
        """ Book description harvesting """
        if 'description' in self.metadata:
            for value in self.book.additional_metadata.getlist('description'):
                self.assert_(value in self.metadata['description'],
                             '%s not in %s' % (value, str(self.metadata['description']),))
            self.assertEqual(len(self.book.additional_metadata.getlist('description')),
                             len(self.metadata['description']))
    
    def testOffsetHarvesting(self):
        """ Book offset harvesting """
        if 'offset' in self.metadata:
            for value in self.book.additional_metadata.getlist('offset'):
                self.assert_(value in self.metadata['offset'],
                             '%s not in %s' % (value, str(self.metadata['offset']),))
            self.assertEqual(len(self.book.additional_metadata.getlist('offset')),
                             len(self.metadata['offset']))
    
    def testAddtionalMetadata(self):
        """ Book additional metadata is a valid container """
        self.assert_(isinstance(self.book.additional_metadata, MultiValueDict))
    
    def testOffsetReadingView(self):
        """ Book offset reading view """
        self.assertEqual(self.book.offset_reading_view,
                         self.metadata['offset_reading'])
    
class Book2MetadataTest(BookMetadataTest):
    book_identifier = 'oai:dspace.institution.edu:1969.1/91217'
    metadata = {'title': 'Speculum 1',
                'creator': 'Pablos, Other',
                'created': '1556',
                'issued': '2010-07-12 17:04:42',
                'thumbnail': None,
                'contributor': [],
                'publisher': [],
                'subject': [],
                'other subject': [],
                'alternate title': [],
                'description': [],
                'offset': [],
                'offset_reading': True}

class BookPageTest(BaseTest):
    save_repository = True
    save_collection = True
    book_identifier = 'oai:dspace.institution.edu:1969.1/91216'
    
    def testReadingPage(self):
        """ Reading view page of a page in a book """
        pages = self.book.pages.all()
        
        self.assertEquals(pages[0].reading_page, 1)
        self.assertEquals(pages[1].reading_page, 1)
        self.assertEquals(pages[2].reading_page, 2)
        
        for page in pages:
            page.book.additional_metadata['offset'] = '5'
        
        self.assertEquals(pages[0].reading_page, 1)
        self.assertEquals(pages[1].reading_page, 2)
        self.assertEquals(pages[2].reading_page, 2)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(RepositoryTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CollectionTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BookTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BookMetadataTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Book2MetadataTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BookPageTest))
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
