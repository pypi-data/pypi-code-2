# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os

from paste.fileapp import _FileIter
from benri.service import InitFailure
from tempfile import mkstemp

class Spool(object):
    """Spool class which retrieves the input-data via wsgi.input and dumps it in
       a temporary file in a spool-directory. Can be used as both middleware or
       direct via a method call.
    """
    
    def __init__(self, config, app=None):
        """
        Takes a config-instance and optionally a WSGI-app if this will be used as a 
        middleware. Raises `InitFailure` if the spool_path does not exist in the 
        config or cannot be created.
        
        - `config`: a `benri.config.Config` instance.
        - `app`: a WSGI application, if None this cannot be used as a WSGI-
                 middleware.
                 
        Usage:
        
        >>> spool = Spool({'service': {'spool_path': '/tmp/'}})
        >>> f_name = '/etc/hosts'
        >>> f = open(f_name, 'r')
        >>> tmp = spool.dump(f, os.path.getsize(f_name))
        >>> #''.join([l for l in open(tmp)])
        >>> os.unlink(tmp)
        """
        try:
            spool_path = config['service']['spool_path']
        except KeyError, e:
            raise InitFailure("spool_path could not be found in the [service] section in the config file")
                        
        if not os.path.exists(spool_path):
            try:
                os.mkdir(spool_path)
            except Exception, e:
                raise InitFailure("Could not create spool_path: %s" %(spool_path))

        self.__spool_path = spool_path
        self.__app = app        

    def __call__(self, env, resp):
        """
        When used as a WSGI-middleware, the input-data is read into a spool-file.
        The absolute-path to the file is passed to the application in the 
        environment-variable `benri.spool_file`.
        """
        
        in_file = env.get('wsgi.input', None)
        size = int(env.get('CONTENT_LENGTH', '-1'))
        
        env['benri.spool_file'] = self.dump(in_file, size)
        
        return self.__app(env, resp)
        

    def dump(self, file_obj, size=-1):
        """
        Dumps the contents of `file_obj` to a file in the spool-directory. Returns
        the absolute path to the new file.
        
        - `file_obj`: a file-like object with a `read`-method
        - `size`: number of bytes to be read from the file. If this is -1, we read
                  data until an EOF is found or StopIteration is raised.
        """        
        (fd, tmp_name) = mkstemp(dir=self.__spool_path)

        f = os.fdopen(fd, 'w+')
        for chunk in _FileIter(file_obj, size=size, block_size=2**14):
            f.write(chunk)
        
        f.close()
        
        return tmp_name
                
if __name__ == '__main__':
    import doctest
    doctest.testmod()    
