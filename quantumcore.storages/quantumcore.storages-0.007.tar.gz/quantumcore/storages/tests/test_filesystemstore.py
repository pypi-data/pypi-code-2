import os
import py

class TestFilesystemStorage(object):
    
    def test_add_file(self, file, fs):
        filepath = fs.add(file)
        dirpath = os.path.split(filepath)[0] # split the filename from the dir path
        fullpath = os.path.join(fs.root_path, dirpath) # add the root path again
        assert len(os.listdir(fullpath)) == 1
        
    def test_file_retrieve(self, file, fs):
        filepath = fs.add(file)
        file2 = fs[filepath]
        file.seek(0)
        c1 = file.read()
        c2 = file2.read()
        assert c1==c2
        

    def test_add_multiple_files(self, file, fs):
        filepath1 = fs.add(file)
        file.seek(0)
        filepath2 = fs.add(file)
        
        dirpath1, filename1 = os.path.split(filepath1)
        dirpath2, filename2 = os.path.split(filepath2)
        
        assert dirpath1==dirpath2    
        assert filename1!=filename2
    
    def test_add_with_filename(self, file, fs):
        filepath1 = fs.add(file, u"foobar.png")

        dirpath1, filename1 = os.path.split(filepath1)

        assert filename1==u"foobar.png"

    def test_add_with_filename_collision(self, file, fs):
        filepath1 = fs.add(file, u"foobar.png")
        file.seek(0)
        filepath2 = fs.add(file, u"foobar.png")

        dirpath1, filename1 = os.path.split(filepath1)
        dirpath2, filename2 = os.path.split(filepath2)
        
        assert filename1==u"foobar.png"
        assert filename2==u"foobar-1.png"

    def test_add_and_retrieve(self, file, fs):
        filepath = fs.add(file, u"foobar.png")
        
        rfile = fs[filepath]
        file.seek(0)
        c1 = file.read()
        c2 = rfile.read()
        assert c1==c2
        
    def test_delete(self, file, fs):
        filepath = fs.add(file)
        fs.delete(filepath)
        
        py.test.raises(KeyError, lambda: fs[filepath])
        
    def test_update(self, file, file2, fs):
        filepath = fs.add(file)
        filepath2 = fs.update(file2,filepath)
        
        file.seek(0)
        file2.seek(0)
        
        rfile = fs[filepath]
        c1 = file.read()
        c2 = file2.read()
        c3 = rfile.read()
        
        assert c1!=c3
        assert c2==c3
        
    def test_export(self, file, file2, fs):
        f1 = fs.add(file)
        f2 = fs.add(file2)
        
        result = []
        for fp in fs:
            result.append(fp)

        mapping = dict(result) # convert tuple list into dict
        
        assert len(result)==2
        
        # also check contents
        file.seek(0)
        file2.seek(0)
        
        c1 = mapping[f1].read()
        c2 = mapping[f2].read()
        
        c1_o = file.read()
        c2_o = file2.read()
        
        assert c1==c1_o
        assert c2==c2_o
        
        
        
        
        
        
        