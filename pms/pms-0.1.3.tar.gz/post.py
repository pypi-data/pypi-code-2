from jsonrequester import JsonRequester

requester = JsonRequester('http://localhost:5000')

for i in range(1):
    doc = {
        'a': 'a',
        'b': 'b',
        'level': 'error',
        'host': str(i),
    }
    for j in range(i + 1):
        print requester.post('/record', doc)

