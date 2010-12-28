from quantumcore.storages import File
import py

class TestExtendedFileStore(object):
    
    def test_add_and_retrieve(self, file, efs):
        """add a file"""
        a=File(file)
        asset_id = efs.add(a)
        
        a2 = efs[asset_id]
        c1 = a2.fp.read()
        file.seek(0)
        c2 = file.read()
        assert c1 == c2
        
    def test_delete(self, file, efs):
        a=File(file)
        asset_id = efs.add(a)
        efs.delete(asset_id)
        
        py.test.raises(KeyError, lambda: efs[asset_id])
        
    
class TestFiles(object):
    """test the file implementation"""
    
    def test_create(self, file):
        a=File(file)
        assert len(a.id_)>0
        assert a.fp==file
        
    def test_create_with_name(self, file):
        a=File(file, u"superfile")
        assert a.id_==u"superfile"
        
    def test_create_with_metadata(self, file):
        a=File(file, gallery=1)
        assert a.gallery==1
        assert a['gallery']==1
        assert len(a.id_)==36 # not so black box but anyway

    def test_fp_not_in_metadata(self, file):
        a=File(file)
        assert a.keys()==['id_']

    def test_get_mapping(self, file):
        a = File(file, asset_id="foo", gallery=1, blogpost="foobar")
        assert a.items()==[('id_', 'foo'), ('blogpost', 'foobar'), ('gallery', 1)]
        
