

class TestJSLinking:
    
    def test_nomerge_links(self, jsfix1):
        
        links = jsfix1.unmerged_resources() # this contains two scripts
        lines = links.split("\n")
        assert len(lines) == 2

    def test_merge_links(self, jsfix1):
        """here we merge two stylesheets together"""
        
        links = jsfix1.merged_resources()
        assert len(links.split("\n")) == 1
        
        assert 'src="/static/js/script' in links
        assert 'type="text/javascript"' in links
    
    def test_multiple_named_scripts(self, jsfix1):
        """test it with one merged cluster and a special named `ie` one"""
        resources = jsfix1.named_resources
        
        links = resources() 
        assert len(links.split("\n")) == 1
        
        # check the ie thing
        links = resources('ie')
        assert len(links.split("\n")) == 1

