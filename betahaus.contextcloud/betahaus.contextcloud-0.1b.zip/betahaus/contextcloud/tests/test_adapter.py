import unittest

from Products.PloneTestCase.ptc import PloneTestCase
from zope.component import queryAdapter

from betahaus.contextcloud.tests.layer import ContextCloudLayer
from betahaus.contextcloud.interfaces import IContextCloud


class TestAdapter(PloneTestCase):
 
    layer = ContextCloudLayer
    
    def afterSetUp(self):
        #Should be common for all tests
        self.loginAsPortalOwner()

    def _some_news(self):
        news = self.portal.news
        doActionFor = self.portal.portal_workflow.doActionFor
        
        #A gloomy cloud...
        items = {
        1:[u'Slander',u'Blasphemy'],
        2:[u'Slander',u'Loose talk',u'Blasphemy'],
        3:[u'Slander',u'Loose talk',],
        4:[u'Slander',],
        5:[u'Slander',],
        6:[u'Slander',u'Loose talk',u'Uncommon niceness'],
        }
        for (i, subjects) in items.items():
            id = news.invokeFactory('News Item', id="item-%s" % str(i))
            obj = news.get(id)
            obj.update(subject=subjects)
            doActionFor(obj, 'publish')
            obj.reindexObject()
        
    def test_adapter_retrieval(self):
        self.failUnless(queryAdapter(self.portal.news, IContextCloud))
        
    def test_subject_length(self):
        self._some_news()
        cloud = IContextCloud(self.portal.news)
        tags = cloud.getResults()
        
        #We should have 4 subjects here
        self.assertEqual(len(tags),4)
        
    def test_order(self):
        self._some_news()
        cloud = IContextCloud(self.portal.news)
        tags = cloud.getResults()

        self.assertEqual(tags[0].name, 'Blasphemy')
        self.assertEqual(tags[1].name, 'Loose talk')
        self.assertEqual(tags[2].name, 'Slander')
        self.assertEqual(tags[3].name, 'Uncommon niceness')
        
    def test_count(self):
        self._some_news()
        cloud = IContextCloud(self.portal.news)
        tags = cloud.getResults()
        
        self.assertEqual([x.count for x in tags], [2, 3, 6, 1])

    def test_weight(self):
        self._some_news()
        cloud = IContextCloud(self.portal.news)
        tags = cloud.getResults()
        tags = cloud.addCloud(tags)

        self.assertEqual([x.weight for x in tags], [3, 5, 5, 1])

    def test_result_limit_collection(self):
        """ Collections/Topics may have set limit results. The tagcloud should
            not honor that limit though, since it should display an
            overview of all content in a specific context.
        """
        #We can use the news aggregator
        self._some_news()
        topic = self.portal.news.aggregator
        topic.setLimitNumber(True)
        topic.setItemCount(1)
        
        #The topic should return only 1 news item now
        self.assertEqual(len(topic.queryCatalog()),1)
        
        #But the adapter should return all which means that the tag "Slander"
        #should have 6 occurences
        cloud = IContextCloud(self.portal.news)
        self.assertEqual(cloud.getResults()[2].count, 6)

    def test_regular_url(self):
        self._some_news()
        cloud = IContextCloud(self.portal.news)
        self.assertEqual(cloud.getResults()[0].url,'http://nohost/plone/news?Subject=Blasphemy')

    def test_selected_url(self):
        self._some_news()
        news = self.portal.news
        #This is the same as a get request like http://site?Subject=Blasphemy
        news.REQUEST.form['Subject'] = 'Blasphemy'
                
        cloud = IContextCloud(news)
        #The link for the selected tag should actually remove the keyword
        self.assertEqual(cloud.getResults()[0].url, 'http://nohost/plone/news')

    def test_fieldindex(self):
        self._some_news()
        news = self.portal.news
        cloud = IContextCloud(news)
        #portal_type will pick up the collection in this context too
        tags = cloud.getResults(index='portal_type')
        self.assertEqual(len(tags),2)
        self.assertEqual(tags[0].name, 'News Item')
        self.assertEqual(tags[1].name, 'Topic')
        self.assertEqual(tags[0].count, 6)
        self.assertEqual(tags[1].count, 1)

    def test_other_get_requests_kept(self):
        self._some_news()
        news = self.portal.news
        #This is the same as a get request like http://site?Subject=Blasphemy
        news.REQUEST.form['Subject'] = 'Blasphemy'
        news.REQUEST.form['dont_touch_me'] = 'Or else!'
                
        cloud = IContextCloud(news)
        #The link for the selected tag should actually remove the keyword
        #but not the link that this index doesn't handle
        self.assertEqual(cloud.getResults()[0].url, 'http://nohost/plone/news?dont_touch_me=Or%20else%21')

    def test_nonexistent_column(self):
        news = self.portal.news
        cloud = IContextCloud(news)
        try:
            cloud.getResults(index="I dont exist")
            self.fail("Adapter didn't raise KeyError for a query with an index that doesn't exist as a column.")
        except KeyError:
            pass

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)