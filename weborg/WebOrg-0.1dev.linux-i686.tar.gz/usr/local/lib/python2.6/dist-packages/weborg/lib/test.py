import client
import json
print client.entry_index()
print client.entry_update('88bf8c57-5bd6-4d45-b2a2-44c3fa4d3b6c',
                          json.dumps({u'category': u'play.org', u'scheduled': None, u'parent': u'root', u'state': u'TODO', u'deadline': None, u'heading': u'\u4e09\u56fd\u6740\uff08\u4fee\u6539\uff09'}))
print client.entry_new('88bf8c57-5bd6-4d45-b2a2-44c3fa4d3b6c')
print client.entry_create('88bf8c57-5bd6-4d45-b2a2-44c3fa4d3b6c',
                          json.dumps({"heading":u'\u4e09\u56fd\u6740\u6740\u6740', "state":None, "parent":"88bf8c57-5bd6-4d45-b2a2-44c3fa4d3b6c", "category":"play.org", "scheduled":None, "deadline":None}))
print client.entry_delete('c859cf52-1029-463b-a01a-903045c15491')
print client.entry_show('88bf8c57-5bd6-4d45-b2a2-44c3fa4d3b6c')
