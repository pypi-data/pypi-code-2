# -*- coding: utf-8 -*-

import codecs
import csv

def csv_export(rtm_client, csv_filename, filter = None):
    raise Exception("Sorry, this is not yet implemented")
    output = codecs.open(csv_filename, "w", encoding = "utf-8")  
    csv_output = csv.writer(output)
    csv_output.writerow([u'Task', u'List', u'Recurring'])
    output.close()
