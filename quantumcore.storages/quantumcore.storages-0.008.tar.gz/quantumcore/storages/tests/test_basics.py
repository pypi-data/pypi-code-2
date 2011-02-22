

class NoTestBasics(object):
    
    def test_add_without_filename(self, file, am):
        asset_id = am.add(file)
        assert asset_id is not None
        
    def test_retrieve_asset(self, asset_id, am):
        asset = am[asset_id]
