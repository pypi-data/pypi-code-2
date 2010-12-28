from quantumcore.resources import CSSResourceManager, css_from_pkg_stream
from urlparse import urlparse

class TestLinking:
    
    def test_nomerge_links(self, cssfix1):
        
        resources = cssfix1.unmerged_resources
        links = resources()
        lines = links.split("\n")
        print links
        assert len(lines) == 2
        assert len(resources.filenames.keys())==2
        
    def test_cluster_filename(self, cssfix1):
        cluster = cssfix1.merged_resources._get_clusters_for_name('')[0]
        filename = cluster.filename
        
        scheme, hostport, path, foo, params, foo = urlparse(filename)
        print filename
        assert path.endswith(".css")
        assert params.startswith("h=")
        assert path.startswith("/static/css")

    def test_numbered_clusters(self, cssfix1):
        """test if clusters with different profiles but same name are numbered in filenames"""
        clusters = cssfix1.unmerged_resources._get_clusters_for_name(u'')
        cluster1, cluster2 = clusters
        
        foo, foo, path1, foo, foo, foo = urlparse(cluster1.filename)
        foo, foo, path2, foo, foo, foo = urlparse(cluster2.filename)

        assert path1!=path2
        # TODO: Test for explicit format
        
    def test_merge_links(self, cssfix1):
        """here we merge two stylesheets together"""
        
        cssfix1.merged_resources.merge()
        links = cssfix1.merged_resources()
        print links
        assert len(links.split("\n")) == 1
        print links

        # the name in this example is 
        
        assert 'href="/static/css/style' in links
        assert 'media="projection, screen"' in links
        assert 'rel="stylesheet"' in links
        assert 'type="text/css"' in links
    
    def test_multiple_named_links(self, cssfix1):
        """test it with one merged cluster and a special named `ie` one"""
        resources = cssfix1.ie_resources # 2 normal and one ie named resource
        
        links = resources() 
        assert len(links.split("\n")) == 1 # 1 merged resource out of 2 basic resources
        
        # check the ie thing
        links = resources('ie')
        assert len(links.split("\n")) == 1

    def test_media_cluster_links(self, cssfix1):
        """test if different media types result in different clusters"""
        resources = cssfix1.print_resources
        
        links = resources() 
        assert len(links.split("\n")) == 2
        
    def test_sorting(self):
        r1 = css_from_pkg_stream(__name__, 'data/style.css', merge=True, prio=2)
        r2 = css_from_pkg_stream(__name__, 'data/addons.css', merge=True, prio=1)
        rs = CSSResourceManager([r1, r2], prefix_url='/static/css')
        rs.merge()
        
        cluster = rs._get_clusters_for_name(u'')[0]
        assert cluster.resource_string == u"""\nh1 {font-size: 160%;}\nbody {background: black;}"""
        
        
        
        
        
        