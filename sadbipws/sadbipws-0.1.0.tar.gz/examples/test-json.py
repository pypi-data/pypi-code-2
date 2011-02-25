#!/usr/bin/env python3

import sadbipws

data = '''
{
  "name": "RE-44M3Q",
  "age":  78.23,
  "info": [
    23, true, null, false
          ]
}
'''

bzd_jsn = sadbipws.serialize(data, json_in=True, gzip_out=True)
unbzd_dat = sadbipws.deserialize(bzd_jsn, json_out=True, gzip_in=True)
print(data)
print(bzd_jsn)
print(unbzd_dat)
