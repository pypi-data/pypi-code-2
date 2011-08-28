#
# pyzmail/parse.py
# (c) Alain Spineux <alain.spineux@gmail.com>
# http://www.magiksys.net/pyzmail
# Released under LGPL

"""
Various function used by other modules
@var invalid_chars_in_filename: a mix of characters not permitted in most used filesystems
@var invalid_windows_name: a list of unauthorized filenames under Windows
"""

invalid_chars_in_filename='<>:"/\\|?*\%\''+reduce(lambda x,y:x+chr(y), range(32), '')

invalid_windows_name=['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 
                      'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 
                      'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7',
                      'LPT8', 'LPT9' ]

def sanitize_filename(filename, alt_name, alt_ext):
    """
    Convert the given filename into a name that should work on all 
    platform. Remove non us-ascii characters, and drop invalid filename.
    Use the I{alternative} filename if needed.
    
    @type filename: unicode or None
    @param filename: the originale filename or None. Can be unicode.
    @type alt_name: str
    @param alt_name: the alternative filename if filename is None or useless
    @type alt_ext: str
    @param alt_ext: the alternative filename extension (including the '.')

    @rtype: str
    @returns: a valid filename.
     
    >>> sanitize_filename('document.txt', 'file', '.txt')
    'document.txt'
    >>> sanitize_filename(None, 'file', '.txt')
    'file.txt'
    >>> sanitize_filename(u'R\\xe9pertoir.txt', 'file', '.txt')
    'Rpertoir.txt'
    >>> # the '\\xe9' has been removed
    >>> sanitize_filename(u'\\xe9\\xe6.html', 'file', '.txt')
    'file.html'
    >>> # all non us-ascii characters have been removed, the alternative name
    >>> # has been used the replace empty string. The originale extention
    >>> # is still valid  
    >>> sanitize_filename(u'COM1.txt', 'file', '.txt')
    'COM1A.txt'
    >>> # if name match an invalid name or assimilated then a A is added
    """
    
    if not filename:
        return alt_name+alt_ext

    if isinstance(filename, str):
        filename=filename.decode('ascii', 'ignore')
        
    # before: filename is unicode
    filename=filename.encode('ascii', 'ignore')
    # after: filename is ascii-7
    
    filename=filename.translate(None, invalid_chars_in_filename)
    filename=filename.strip()
        
    upper=filename.upper()
    for name in invalid_windows_name:
        if upper==name:
            return name+"A"
        if upper.startswith(name+'.'):
            return name+"A"+filename[len(name):]

    if filename.rfind('.')==0:
        filename=alt_name+filename

    return filename

def handle_filename_collision(filename, filenames):
    """
    Avoid filename collision, add a sequence number to the name when required.
    'file.txt' will be renamed into 'file-01.txt' then 'file-02.txt' ... 
    until their is no more collision. The file is not added to the list.
     
    Windows don't make the difference between lower and upper case. To avoid
    "case" collision, the function compare C{filename.lower()} to the list.
    If you provide a list in lower case only, then any collisions will be avoided.     
    
    @type filename: str
    @param filename: the filename
    @type filenames: list or set
    @param filenames: a list of filenames. 

    @rtype: str
    @returns: the I{filename} or the appropriately I{indexed} I{filename} 
     
    >>> handle_filename_collision('file.txt', [ ])
    'file.txt'
    >>> handle_filename_collision('file.txt', [ 'file.txt' ])
    'file-01.txt'
    >>> handle_filename_collision('file.txt', [ 'file.txt', 'file-01.txt',])
    'file-02.txt'
    >>> handle_filename_collision('foo', [ 'foo',])
    'foo-01'
    >>> handle_filename_collision('foo', [ 'foo', 'foo-01',])
    'foo-02'
    >>> handle_filename_collision('FOO', [ 'foo', 'foo-01',])
    'FOO-02'
    """
    if filename.lower() in filenames:
        try:
            basename, ext=filename.rsplit('.', 1)
            ext='.'+ext
        except ValueError:
            basename, ext=filename, '' 

        i=1
        while True:
            filename='%s-%02d%s' % (basename, i, ext)
            if filename.lower() not in filenames:
                break
            i+=1
        
    return filename
