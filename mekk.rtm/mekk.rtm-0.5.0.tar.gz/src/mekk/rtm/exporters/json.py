# -*- coding: utf-8 -*-

import codecs
import simplejson

def json_export(rtm_client, json_filename, filter = None):
    """
    Exports all task or task satisfying the filter.
    """
    raise Exception("Sorry, this is not yet implemented")

    lists = []
    tasks = []

    output = codecs.open(json_filename, "w", encoding = "utf-8")   
    simplejson.dump(
        dict(lists = lists, tasks = tasks),
        output,
        sort_keys = True,
        indent = 4,
        )
    output.close()
    
