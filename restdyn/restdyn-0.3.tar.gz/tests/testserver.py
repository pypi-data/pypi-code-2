from bottle import route, run, request
import json

@route('/tests/jsonquery')
def index():
    return json.dumps(json.loads(request.GET.get('q')))

run(host='localhost', port=8080)

