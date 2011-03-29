from os.path import dirname, join
import unittest

from lxml import etree

from django.utils.datastructures import MultiValueDict
from django.core.exceptions import ValidationError
from django.test import TestCase

from bookreader.models import Repository, Collection, Book
from bookreader.signals import collection
from bookreader.signals import repository

from bookreader.tests import fakes



class BaseRepositoryTest(TestCase):
    save_repository = False
    collection_handle = '1969.1/6069'
    save_collection = False
    book_identifier = None
    
    def setUp(self):
        self.repository = Repository(url='http://dspace.institution.edu/dspace-oai/request')
        fakes.fake_repository_connection(self.repository, join(dirname(__file__),'oai'))
        
        if self.save_repository:
            self.repository.save()
        
        if self.collection_handle:
            self.collection = Collection(repository=self.repository,
                                         handle=self.collection_handle)
            if self.save_collection:
                self.collection.save()
        
        if self.book_identifier:
            self.book = Book.objects.get(identifier=self.book_identifier)
            
            if self.collection_handle:
                self.book.collection = self.collection
            

class RepositoryTests(BaseRepositoryTest):
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

class CollectionTests(BaseRepositoryTest):
    save_repository = True
    
    def testCollectionNameSignal(self):
        """ Signal for setting collection name from OAI-PMH ListSets """
        self.assertEqual(self.collection.name, '')
        self.collection.save()
        self.assertEqual(self.collection.name, 'Test Collection 1')
    
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

class BookTests(BaseRepositoryTest):
    save_repository = True
    save_collection = True
    book_identifier = 'oai:dspace.institution.edu:1969.1/91216'
    
    def testPages(self):
        """ Signal for/harvesting of pages (ORE based pages) """
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

class BitstreamBaseTest(BaseRepositoryTest):
    def setUp(self):
        super(BitstreamBaseTest, self).setUp()
        from bookreader.harvesting import book
        fakes.fake_repository_connection(self.book.collection.repository,
                                         join(dirname(__file__),'oai'))
        book.load_pages(self.book, parser=lambda v: etree.parse(join(dirname(__file__),v)))

class BookBitstreamMetadataTest(BitstreamBaseTest):
    save_repository = True
    save_collection = True
    book_identifier = 'oai:dspace.institution.edu:1969.1/91216'
    
    def testIsCanonical(self):
        """ Bitstream metadata sets is_canonical flag """
        self.assertEqual(self.book.is_canonical, False)
    
    def testPageCount(self):
        """ Bitstream metadata number of pages harvested """
        self.assertEqual(self.book.pages.count(), 17)
    
    def testInternalPageCount(self):
        """ Bitstream metadata number of internal pages harvested """
        self.assertEqual(self.book.pages.filter(internal=True).count(), 11)
    
    def testExternalPageCount(self):
        """ Bitstream metadata number of external pages harvested """
        self.assertEqual(self.book.pages.filter(internal=False).count(), 6)
    
    def testExternalPages(self):
        """ Bitstream metadata external pages """
        pages = self.book.pages.filter(internal=False).order_by('title').all()
        
        self.assertEqual(pages[0].title, 'back')
        self.assertEqual(pages[0].sequence, 0)
        self.assertEqual(pages[0].jp2, None)
        self.assertEqual(pages[0].thumbnail, None)
        
        self.assertEqual(pages[1].title, 'bottom')
        self.assertEqual(pages[1].sequence, 0)
        self.assertEqual(pages[1].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00002.jpf')
        self.assertEqual(pages[1].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00002.jpg')
        
        self.assertEqual(pages[2].title, 'front')
        self.assertEqual(pages[2].sequence, 0)
        self.assertEqual(pages[2].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00003.jpf')
        self.assertEqual(pages[2].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00003.jpg')
        
        self.assertEqual(pages[3].title, 'side')
        self.assertEqual(pages[3].sequence, 0)
        self.assertEqual(pages[3].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00004.jpf')
        self.assertEqual(pages[3].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00004.jpg')
        
        self.assertEqual(pages[4].title, 'spine')
        self.assertEqual(pages[4].sequence, 0)
        self.assertEqual(pages[4].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00005.jpf')
        self.assertEqual(pages[4].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00005.jpg')
        
        self.assertEqual(pages[5].title, 'top')
        self.assertEqual(pages[5].sequence, 0)
        self.assertEqual(pages[5].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00001.jpf')
        self.assertEqual(pages[5].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00001.jpg')
    
    def testInternalPages(self):
        """ Bitstream metadata internal pages """
        pages = self.book.pages.filter(internal=True).order_by('sequence').all()
        
        for i in range(0,len(pages)):
            self.assertEqual(pages[i].sequence, i+1)
        
        self.assertEqual(pages[0].title, 'test title')
        self.assertEqual(pages[0].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00006.jpf')
        self.assertEqual(pages[0].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00006.jpg')
        
        self.assertEqual(pages[1].title, 'pl_tamu_013_00007')
        self.assertEqual(pages[1].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00007.jpf')
        self.assertEqual(pages[1].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00007.jpg')
        
        for i in range(3, 8):
            self.assertEqual(pages[i].title, None)
            self.assertEqual(pages[i].jp2, None)
            self.assertEqual(pages[i].thumbnail, None)
        
        self.assertEqual(pages[10].title, 'pl_tamu_013_00011')
        self.assertEqual(pages[10].jp2,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/pl_tamu_013_00011.jpf')
        self.assertEqual(pages[10].thumbnail,
                         'http://dspace.institution.edu/bitstream/handle/1969.1/92214/thumbs/pl_tamu_013_00011.jpg')
    
    def testAnnotationCount(self):
        """ Bitstream metadata number of annotations """
        self.assertEqual(self.book.annotations.count(), 12)
    
    def testAnnotations(self):
        """ Bitstream metadata annotations """
        annotations = self.book.annotations.order_by('offset','-length','text').all()
        values = [
            {'offset': 1, 'length': 2, 'end': 2, 'structural': True, 'text': 'Chapter 1'},
            {'offset': 1, 'length': 1, 'end': 1, 'structural': True, 'text': 'Chapter 1.1'},
            {'offset': 1, 'length': 1, 'end': 1, 'structural': False, 'text': 'Title Page'},
            {'offset': 2, 'length': 1, 'end': 2, 'structural': True, 'text': 'Chapter 1.2'},
            {'offset': 3, 'length': 3, 'end': 5, 'structural': True, 'text': 'Chapter 2'},
            {'offset': 3, 'length': 2, 'end': 4, 'structural': True, 'text': 'Chapter 2.1'},
            {'offset': 3, 'length': 1, 'end': 3, 'structural': True, 'text': 'Chapter 2.1.1'},
            {'offset': 4, 'length': 1, 'end': 4, 'structural': True, 'text': 'Chapter 2.1.2'},
            {'offset': 5, 'length': 3, 'end': 7, 'structural': True, 'text': 'Chapter 3'},
            {'offset': 5, 'length': 2, 'end': 6, 'structural': True, 'text': 'Chapter 3.1'},
            {'offset': 5, 'length': 1, 'end': 5, 'structural': True, 'text': 'Chapter 2.2'},
            {'offset': 6, 'length': 2, 'end': 7, 'structural': True, 'text': 'Chapter 3.2'},
        ]
        
        for i in range(0,9):
            self.assertEqual(annotations[i].offset, values[i]['offset'], 'Invalid offset on page: %s' % (str(annotations[i],)))
            self.assertEqual(annotations[i].length, values[i]['length'], 'Invalid length on page: %s' % (str(annotations[i],)))
            self.assertEqual(annotations[i].structural, values[i]['structural'], 'Invalid structural on page: %s' % (str(annotations[i],)))
            self.assertEqual(annotations[i].text, values[i]['text'], 'Invalid text on page: %s' % (str(annotations[i],)))
            self.assertEqual(annotations[i].end, values[i]['end'], 'Invalid end on page: %s' % (str(annotations[i],)))
    
    def testAnnotationStructure(self):
        """ Bitstream metadata structured annotations """
        top_level = self.book.top_level_structure
        
        self.assertEqual(len(top_level), 3)
        
        chapter = top_level[0]
        
        self.assertEqual(chapter.text, 'Chapter 1')
        subchapters = chapter.children
        self.assertEqual(len(subchapters), 2)
        self.assertEqual(subchapters[0].text, 'Chapter 1.1')
        self.assertEqual(subchapters[1].text, 'Chapter 1.2')
        self.assertEqual(len(subchapters[0].children),0)
        self.assertEqual(len(subchapters[1].children),0)
        
        
        chapter = top_level[1]
        
        self.assertEqual(chapter.text, 'Chapter 2')
        subchapters = chapter.children
        self.assertEqual(len(subchapters), 2,
                         'Chapter 2: Invalid number of subchapters: %d' % (len(subchapters),))
        self.assertEqual(subchapters[0].text, 'Chapter 2.1',
                         'Chapter 2: Invalid first subchapter: %s' % (subchapters[0].text,))
        self.assertEqual(subchapters[1].text, 'Chapter 2.2',
                         'Chapter 2: Invalid second subchapter: %s' % (subchapters[1].text,))
        
        subsubchapters = subchapters[0].children
        
        self.assertEqual(len(subsubchapters),2)
        self.assertEqual(len(subsubchapters[0].children),0)
        self.assertEqual(subsubchapters[0].text,'Chapter 2.1.1')
        self.assertEqual(len(subsubchapters[1].children),0)
        self.assertEqual(subsubchapters[1].text,'Chapter 2.1.2')
        
        chapter = top_level[2]
        
        self.assertEqual(chapter.text, 'Chapter 3')
        subchapters = chapter.children
        self.assertEqual(len(subchapters), 2,
                         'Chapter 3: Invalid number of subchapters: %d' % (len(subchapters),))
        self.assertEqual(subchapters[0].text, 'Chapter 3.1',
                         'Chapter 3: Invalid first subchapter: %s' % (subchapters[0].text,))
        self.assertEqual(subchapters[1].text, 'Chapter 3.2',
                         'Chapter 3: Invalid second subchapter: %s' % (subchapters[1].text,))
        
    
    def testPageOneAnnotations(self):
        """ Bitstream metadata page annotations (page 1) """
        page = self.book.pages.get(sequence=1)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 3)
        
        for i in range(0,3):
            self.assertTrue(annotations[i].text in ('Chapter 1','Chapter 1.1','Title Page',))
    
    def testPageTwoAnnotations(self):
        """ Bitstream metadata page annotations (page 2) """
        page = self.book.pages.get(sequence=2)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 2)
        
        for i in range(0,2):
            self.assertTrue(annotations[i].text in ('Chapter 1','Chapter 1.2',))
    
    def testPageThreeAnnotations(self):
        """ Bitstream metadata page annotations (page 3) """
        page = self.book.pages.get(sequence=3)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 3)
        
        for i in range(0,3):
            self.assertTrue(annotations[i].text in ('Chapter 2','Chapter 2.1','Chapter 2.1.1',))
    
    def testPageFourAnnotations(self):
        """ Bitstream metadata page annotations (page 4) """
        page = self.book.pages.get(sequence=4)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 3)
        
        for i in range(0,3):
            self.assertTrue(annotations[i].text in ('Chapter 2','Chapter 2.1','Chapter 2.1.2',))
    
    def testPageFiveAnnotations(self):
        """ Bitstream metadata page annotations (page 5) """
        page = self.book.pages.get(sequence=5)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 4)
        
        for i in range(0,4):
            self.assertTrue(annotations[i].text in ('Chapter 2','Chapter 2.2','Chapter 3','Chapter 3.1',))
    
    def testPageSixAnnotations(self):
        """ Bitstream metadata page annotations (page 6) """
        page = self.book.pages.get(sequence=6)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 3)
        
        for i in range(0,3):
            self.assertTrue(annotations[i].text in ('Chapter 3','Chapter 3.1','Chapter 3.2',))
        
    def testPageSevenAnnotations(self):
        """ Bitstream metadata page annotations (page 7) """
        page = self.book.pages.get(sequence=7)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 2)
        
        for i in range(0,2):
            self.assertTrue(annotations[i].text in ('Chapter 3', 'Chapter 3.2'))
        
    def testPageNineAnnotations(self):
        """ Bitstream metadata page annotations (page 8) """
        page = self.book.pages.get(sequence=8)
        annotations = page.annotations
        
        self.assertEqual(len(annotations), 0)
    
    def testExternalPageAnnotations(self):
        """ Bitstream metadata page annotations (external) """
        for page in self.book.pages.filter(internal=False):
            self.assertEqual(len(page.annotations), 0)

class CanonicalBookBitstreamMetadataTest(BitstreamBaseTest):
    save_repository = True
    save_collection = True
    book_identifier = 'oai:dspace.institution.edu:1969.1/91217'
    
    def testIsCanonical(self):
        """ Canonical bitstream metadata sets is_canonical flag """
        self.assertEqual(self.book.is_canonical, True)

class BookMetadataTest(BaseRepositoryTest):
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

class BookPageTest(BaseRepositoryTest):
    save_repository = True
    save_collection = True
    book_identifier = 'oai:dspace.institution.edu:1969.1/91216'
    
    def testReadingPage(self):
        """ Book page reading view page number """
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
    """
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(RepositoryTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CollectionTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BookTests))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BookMetadataTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(Book2MetadataTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BookPageTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BookBitstreamMetadataTest))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CanonicalBookBitstreamMetadataTest))
    """
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(test_suite())
