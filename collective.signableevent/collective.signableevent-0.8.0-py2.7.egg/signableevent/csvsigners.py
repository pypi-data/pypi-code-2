import csv, cStringIO

    
def exportSignersToCsv(brains=None):
    attrs = ['gender','firstname','lastname','email','company',
            'function','address','zipcode','city','phone','fax',
            'bill_to', 'bill_address', 'bill_zipcode', 'bill_city', 'bill_province',
            'vatno', 'delegation_request', 'delegation',
            'penalty_clearance', 'credits_request', 'credits',
             'comment']
    attrsparent = ['event_url','title']
    rows = []
    for brain in brains:
        # o for object ;)
        o = brain.getObject()
        row = []
        for attr in attrs:
            itm = getattr(o,attr,'')
            try:
                itm = itm.encode('latin-1', 'ignore')
            except AttributeError:
                # Probably a Bool object
                itm = "True" if itm else "False"
            row.append(itm)
        # URL and title of the event
        op = o.getParentNode()
        row.append(brain.getURL().encode('latin-1', 'ignore'))
        row.append(op.title.encode('latin-1', 'ignore'))
        rows.append(row)

    csv_content = cStringIO.StringIO()
    writer = csv.writer(csv_content, quoting = csv.QUOTE_ALL)

    csvattrs = attrs + ['url','event_title']
    writer.writerow(csvattrs)
    writer.writerows(rows)
    
    csv_content = csv_content.getvalue()
    return csv_content
