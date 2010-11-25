import os
import sys
from fnmatch import fnmatch
from mimetypes import guess_type
from paste.fileapp import FileApp
from pkg_resources import iter_entry_points
from transformers import ContentTypeChanger

class FileTypeTransformer(object):

    def __init__(self, *types, **kwargs):
        """types is a list of two-tuples: glob pattern (string), transformer name (string, name of entry point)"""
        self.types = types

        # arguments to the xformers
        self.kwargs = kwargs
        
        self.transformers = transformers()
        for pattern, transformer_name in self.types:
            if '/' in transformer_name:
                continue
            assert transformer_name in self.transformers, '%s not in transformers' % transformer_name

    def __call__(self, path): 
        """this should return something that is callable with (environ, start_response) to return a response; the transformer thing"""
        filename = os.path.basename(path)
        for pattern, transformer_name in self.types:
            if fnmatch(filename, pattern):
                content_type, _ = guess_type(filename)
                content = file(path).read()

                # transform content type
                # XXX hack: -> refactor
                if '/' in transformer_name:
                    return ContentTypeChanger(content, content_type, transformer_name)
                return self.transformers[transformer_name](content, content_type, **self.kwargs.get(transformer_name, {})) 
        return FileApp(path)


def transformers():
    transformers = {} # XXX could cache
    for entry_point in iter_entry_points('content_transformers'):
        try:
            transformers[entry_point.name] = entry_point.load()
        except:
            raise # XXX
    return transformers
        
