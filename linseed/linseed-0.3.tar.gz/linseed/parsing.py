def basic_parse(data):
    data = [d.split() for d in data]
    data = dict([(d[0], d[1:]) for d in data])
    return data

def paren_parse(data):
    data = [d.split(':') for d in data]
    data = [(k, v.split()) for (k,v) in data]
    return dict(data)
