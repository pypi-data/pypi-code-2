import urlparse
import py.test
from quantumcore.resources import CSSResourceManager, css_from_pkg_stream

from quantumcore.exceptions import NotFound


class TestInternals:
    """test the internal clustering API in order to make sure we can use it in 
    our tests."""
    resource1 = css_from_pkg_stream(__name__, 'data/style.css', merge=False)
    resource2 = css_from_pkg_stream(__name__, 'data/addons.css', merge=False)
    resources = CSSResourceManager([resource1, resource2], prefix_url='/static/css')
    resources.merge()
    
    # this is sort of internal API but it's easier to get hold of
    # hrefs this way instead of parsing the resulting links again
    # TODO: write a regexp parser for retrieving the links
    cluster_list = resources.clusters[''] # get the clusters with the default name
    
    assert len(cluster_list) == 2 # we have two clusters with the default name

    cluster1, cluster2 = cluster_list        
    assert len(cluster1) == 1 # cluster #0 has one resource
    assert len(cluster2) == 1 # cluster #1 has one resource

    foo,foo,path,foo,foo,foo = urlparse.urlparse(cluster1.href)
    
    assert path.startswith("/static/css/style")
    assert path.endswith(".css")
    

class TestRendering:
    """test if the resource sets are rendered correctly"""
    
    def test_nomerge(self):
        
        resource1 = css_from_pkg_stream(__name__, 'data/style.css', merge=False, prio=1)
        resource2 = css_from_pkg_stream(__name__, 'data/addons.css', merge=False, prio=2)
        resources = CSSResourceManager([resource1, resource2], prefix_url='/static/css')
        
        cluster1, cluster2 = resources.clusters['']
        
        # obtain the data of both resources
        data1 = resources.get_payload(cluster1.href)
        data2 = resources.get_payload(cluster2.href)
        data = [data1, data2]
        data.sort() # we do sorting just for testing because the sequence is arbitrary

        assert data[0] == u"\nbody {background: black;}"
        assert data[1] == u"\nh1 {font-size: 160%;}"

    def test_merge(self):
        resource1 = css_from_pkg_stream(__name__, 'data/style.css', merge=True, prio=1)
        resource2 = css_from_pkg_stream(__name__, 'data/addons.css', merge=True, prio=2)
        resources = CSSResourceManager([resource1, resource2], prefix_url='/static/css')
        
        href = resources.clusters[''][0].href
        data = resources.get_payload(href)

        assert data == u'\nbody {background: black;}\nh1 {font-size: 160%;}'

    def test_prefix_wrong(self):
        resources = CSSResourceManager([], prefix_url="/static/css")
        py.test.raises(NotFound, lambda : resources.get_payload("/noway/something"))
        
        