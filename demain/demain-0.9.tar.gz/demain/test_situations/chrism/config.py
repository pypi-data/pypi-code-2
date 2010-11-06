L = []

def decorator(func):
    L.append(func)
    return func
