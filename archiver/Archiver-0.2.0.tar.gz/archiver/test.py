"""\
Defines some extra functions used in the tests.
"""

def extras_b(flow, path, file_record):
    if 'b' in file_record.path:
        print 'Printing from the extras function: ' + file_record.path + ", owner: b"
        return [('owner', 'b')]
    else:
        return []

def extras_d(flow, path, file_record):
    if 'd' in file_record.path:
        print 'Printing from the extras function: ' + file_record.path + ", owner: d"
        return [('owner', 'd', 'string')]
    else:
        return []

def extras_d_cap(flow, path, file_record):
    if 'd' in file_record.path:
        print 'Printing from the extras function: ' + file_record.path + ", owner: D"
        return [('owner', 'D', 'string')]
    else:
        return []

