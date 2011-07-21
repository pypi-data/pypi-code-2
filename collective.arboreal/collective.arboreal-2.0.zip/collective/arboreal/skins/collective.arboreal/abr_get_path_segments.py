##parameters=path
splitPath = path.split('/')
return ['/'.join(splitPath[:i + 1]) for i in range(1, len(splitPath))]

