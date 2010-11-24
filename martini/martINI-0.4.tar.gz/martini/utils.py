def getlist(string, separator=','):
    if not string:
        return []
    _list = [ i.strip() for i in string.split(',') ]
    if not _list:
        return _list
    if not _list[-1]:
        return _list[:-1]
    return _list

def getbool(string):
    return string.strip().lower() == 'true'

