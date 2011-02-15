

def test_globs(gr):
    
    files = {
	    'core' : ['application/x-core'],
	    'word.doc' : ['application/msword', 'text/plain'],
	    'Makefile.PL' : ['application/x-perl'],
	    'Makefile.in' : ['text/x-makefile'],
	    'data,v' : ['text/plain'],
	    'filename.tar.gz' : ['application/x-compressed-tar'],
	    'filename.tar.bz2' : ['application/x-bzip-compressed-tar'],
	    'Makefile' : ['text/x-makefile'],
	    'file.C' : ['text/x-c++src'],
	    'filename.tgz' : ['application/x-compressed-tar'],
	    'file.c' : ['text/x-csrc'],
	    'filename.gz' : ['application/x-gzip'],
	    'README' : ['text/x-readme'],
	    'README.doc' : ['application/msword', 'text/plain'],
	    'README.txt' : ['text/plain']
	}

    for filename, mimetypes in files.items():
	assert gr.match(filename) == mimetypes
