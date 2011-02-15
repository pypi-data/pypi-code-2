import pkg_resources
import re
import fnmatch

EXT_RE = re.compile("(\.\w+)")

class GlobRegistry(object):
    """a registry for storing and detecting glob patterns"""
    
    def __init__(self):
        """initialize glob registry"""
        
        # this dict is used to map extensions to a list of mimetypes
        # e.g. ['.jpg'] = ("image/jpeg", )
        # mimetype results are sorted by their weight
        self.extensions = {} # extension => mimetype
        
        # same as above for those patterns which need to be matches
        # case sensitive. The above dict does not contain them
        # these should be checked first!
        self.cs_extensions = {} 
        
        # this list is used to map all non-extension patterns such as Makefile*
        # it's sorted be glob weight. It contains a tuple: (pattern, flags, mimetype)
        # e.g. ('Makefile*', "cs", 'text/Makefile')
        # again we have case sensitive and insensitive patterns
        self.cs_globs = []
        self.globs = []
        
        self.max_extension_length = 3 # maximum amount of dots in matching extensions        
        
    def read(self):
        """read the default glob file and create the mapping"""
        fp = pkg_resources.resource_stream(__name__,"data/sharedmime/globs2")
        
        max_extension_length = 0 # maximum length of extensions measured in dots
                
        while True:
            line = fp.readline()
            if not line:
                break
            if line.startswith("#"):
                continue
            line=line[:-1] 
            parts = line.split(":")
            prio, mimetype, pattern = parts[:3]
            flags = ""
            if len(parts)>3:
                flags=parts[3]
            
            # parts are known now, now process them
            if pattern.startswith("*."):
                # first those which map to an extension
                ext=pattern[1:] # remove the * but keep the dot
                # decide whether to put an extension into the case sensitive list
                if "cs" in flags: 
                    self.cs_extensions.setdefault(ext, []).append(mimetype)
                else:
                    self.extensions.setdefault(ext.lower(), []).append(mimetype)
                max_extension_length = max(max_extension_length, len(ext.split(".")))
            else:
                # now those which do more involved pattern matching
                e = fnmatch.translate(pattern)
                if "cs" in flags:
                    self.cs_globs.append((re.compile(e), mimetype))
                else:
                    self.globs.append((re.compile(e, re.I), mimetype))
        
        self.max_extension_length = max_extension_length
        
        
    def cut_extension(self, filename):
        """finds extensions of the filename and returns a list with found ones
        sorted by length, longest first. max_extension_length will define the 
        maximum length it searches for. This is computed on reading the glob file
        in read().
        
        Example::
            >>> gr.cut_extension("filename.tar.gz")
            ['.tar.gz', '.gz']        
        """
        exts = EXT_RE.findall(filename)
        result = []
        for i in range(min(len(exts),self.max_extension_length),0,-1):
            ext = "".join(exts[-i:])
            result.append(ext)
        return result
        
    def match(self, filename, default=None):
        """try to match a filename to a list of mimetypes. If this is your only
        method of matching you can give a ``default`` mimetype. Otherwise ``None``
        will be returned in case no match was found.
        
        Matching will be done from the longest to shortest pattern which"""
        
        # try case sensitive first
        cs_match_exts = self.cut_extension(filename)
        for m in cs_match_exts:
            if self.cs_extensions.has_key(m):
                return self.cs_extensions[m]
        
        # next up: case insensitive
        match_exts = self.cut_extension(filename.lower())
        for m in match_exts:
            if self.extensions.has_key(m):
                return self.extensions[m]
                
        # now do pattern patching, case sensitive first
        res = set()
        
        for regexp, mimetype in self.cs_globs:
            if regexp.match(filename) is not None: 
                res.add(mimetype)

        if len(res)>0: # check if we need to check case insensitive globs
            return list(res)
            
        for regexp, mimetype in self.globs:
            if regexp.match(filename) is not None: 
                res.add(mimetype)
                
        if len(res)>0:
            return list(res)

        # nothing found, return the default
        return default

