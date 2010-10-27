import transaction
from raptus.torii import carrier

if not plone:
    conversation(carrier.PrintText('the global plone is not set.'))
    conversation(carrier.ExitTorii())


if len(arguments) > 3 and (arguments[3]== 'help' or arguments[3]=='-h'):
    mesg= """
            usage  run rebuild_catalogs [catalog1] [catalog2] ...
            
            rebuild all catalogs on the plone instance at %(plone_location)s
            You can specified the catalog you want rebuild with a given options.
            
            catalogs:   portal_catalog
                        reference_catalog
                        uid_catalog
            
            
          """ % dict(plone_location='/'.join(plone.getPhysicalPath()))
    conversation(carrier.PrintText(mesg))
    
else:
    transaction.begin()
    catalogs = dict(portal_catalog='clearFindAndRebuild',
                    reference_catalog='refreshCatalog',
                    uid_catalog='refreshCatalog')
    if len(arguments) > 3:
        temp = dict()
        for i in arguments[3:]:
            if catalogs.has_key(i):
                temp.update({i:catalogs.pop(i)})
            else:
                conversation(carrier.PrintText("can't rebuild %s" % i))
        catalogs = temp
    
    for cat, func in catalogs.iteritems():
        inst = getattr(plone, cat, None)
        if inst:
            getattr(inst, func)()
            conversation(carrier.PrintText('%s rebuilded' % cat))
        else:
            conversation(carrier.PrintText("%s dosen't exist" % cat))
    transaction.commit()
    conversation(carrier.PrintText('\ntransaction successfully committed'))


