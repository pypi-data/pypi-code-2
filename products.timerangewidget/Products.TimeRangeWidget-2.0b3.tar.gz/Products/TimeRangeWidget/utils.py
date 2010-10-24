def getListFromTimeRange(value):
    """ converts Integers like 8300945 to ((8,30),(9,45))"""
    range = []
    try:
        value = '0'*(8-len(str(value))) + str(value)
        h = int(value[:2])
        m = int(value[2:4])
        range.append((h,m))
    except:
        range.append((0,0))
    try:
        value = '0'*(8-len(str(value))) + str(value)
        h = int(value[4:6])
        m = int(value[6:])
        range.append((h,m))
    except:
        range.append((0,0))
    return range
