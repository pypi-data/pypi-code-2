try:
  import json as json
except ImportError:
  import simplejson as json

def format_json(data):

  # fix datetime
  for f in data['files']:
    f['modified'] = f['modified'].ctime()

  return 'application/json', json.dumps(data['files'])
  
