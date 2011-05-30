# -*- coding: iso-8859-15 -*-

################################################################
# haufe.sharepoint
################################################################

import connector

if __name__ == '__main__':

    # initialization boilerplate
    url = 'http://myhmg/bereiche/Redaktionen/onlineschulungen/'
    username = 'GRP\\lex_hrs_pseudo'
    password = 'Salute2257'
    list_id = '60e3f442-6faa-4b49-814d-2ce2ec88b8d5'
    service = connector.Connector(url, username, password, list_id)

    # field descriptions
    fields = service.model

    # all items
    ref_items = service.getItems()

    # delete an item
    result = service.deleteItems('54', '55')
    print result
    print result.result
    print result.ok

    # update an item (existing ID)
    data = dict(ID='77', Title=u'Rübennase', FirstName=u'Heinz')
    result = service.updateItems(data)
    print result
    print result.result
    print result.ok

    # update an item (non-existing ID)
    data = dict(ID='77000', Title=u'Becker')
    result = service.updateItems(data)
    print result
    print result.result
    print result.ok

    # add an item 
    data = dict(Title=u'Rübennase', FirstName=u'Heinz')
    result = service.addItems(data)
    print result
    print result.result
    print result.ok
    print 'assigned ID:', result.result[0]['row']._ows_ID

    # query list item by id
    print service.getItem('77')
