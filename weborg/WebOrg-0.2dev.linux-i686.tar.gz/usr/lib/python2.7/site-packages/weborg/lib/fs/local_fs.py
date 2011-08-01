import tempfile
import os.path

class FileSystem():
    def __init__(self, root):
        self.root = root

    def listdir(self):
        "Return a list of file paths"
        file_list = os.listdir(self.root)
        file_list = filter(lambda s: s.endswith('.org'), file_list)
        return file_list

    def get(self, path):
        "Returns a temp file path"
        fd = open(os.path.join(self.root, path), 'r')
        content = fd.read()
        fd.close()
        temppath = tempfile.mkstemp(suffix='.org')[1]
        fd = open(temppath, 'w')
        fd.write(content)
        fd.close()
        return temppath

    def put(self, path, temppath):
        fd = open(temppath, 'r')
        content = fd.read()
        fd.close()
        fd = open(os.path.join(self.root, path), 'w')
        fd.write(content)
        fd.close()

    def rm(self, path):
        os.remove(path)
    
