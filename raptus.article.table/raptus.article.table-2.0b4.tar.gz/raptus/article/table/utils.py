
def parseColumn(string):
    """ Parses a column definition
    """
    col = string.split(':')
    flags = {}
    for flag in col[3:]:
        flags[flag.strip()] = True
    column = {'name': col[0].strip(),
              'title': col[1].strip(),
              'type': col[2].strip(),
              'flags': flags}
    return column
