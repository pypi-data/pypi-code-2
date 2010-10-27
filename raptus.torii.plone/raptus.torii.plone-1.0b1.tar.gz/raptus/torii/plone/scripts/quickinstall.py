import transaction
from raptus.torii import carrier

if not plone:
    conversation(carrier.PrintText('the global plone is not set.'))
    conversation(carrier.ExitTorii())
    
if len(arguments) <= 3 or arguments[3]== 'help' or arguments[3]=='-h':
    mesg= """
            usage  run quickinstall product1 [product2] ...
            
            help        this help message
            
            list        print a list with all products installable 
                        on the plone instance at %(plone_location)s
            
          """ % dict(plone_location='/'.join(plone.getPhysicalPath()))
    
    conversation(carrier.PrintText(mesg))
    
installer = plone.portal_quickinstaller
    
if arguments[3] == 'list':
    products = installer.listInstalledProducts() + installer.listInstallableProducts()
    
    longest_title = 0
    longest_value = 0
    for pro in products:
        for key, value in pro.iteritems():
            key = str(key)
            value = str(value)
            if longest_title < len(key):
                longest_title = len(key)
            if longest_value < len(value):
                longest_value = len(value)
                
    longest_title += 5
    longest_value += 5
                
    conversation(carrier.PrintText('\n\nPlone QuickInstaller at %s\n%s'%('/'.join(plone.getPhysicalPath()),'='*(longest_title+longest_value))))
    for pro in products:
        out = []
        for key, value in pro.iteritems():
            out.append(key + ' '*(longest_title-len(str(key)))+str(value))
        out.reverse()
        for i in out:
            conversation(carrier.PrintText(i))
        conversation(carrier.PrintText('='*(longest_title+longest_value)))
else:
    transaction.begin()

    products = arguments[3:]
    for pro in products:
        if not installer.isProductAvailable(pro):
            conversation(carrier.PrintText('Product: %s was not found' % pro))
        elif not installer.isProductInstallable(pro):
            conversation(carrier.PrintText('Product: %s is not installable' % pro))
        elif installer.isProductInstalled(pro):
            installer.reinstallProducts(pro)
            conversation(carrier.PrintText('Product: %s was reinstalled' % pro))
        else:
            installer.installProduct(pro)
            conversation(carrier.PrintText('Product: %s was installed' % pro))
    transaction.commit()
    conversation(carrier.PrintText('\ntransaction successfully committed'))
