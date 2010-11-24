import datetime

from django.contrib.auth.models import User

from crm import models as crm
from minibooks.ledger import models as ledger

def setup_demo():
    try:
        administrator = User.objects.get(username='demo')
    except User.DoesNotExist:
        administrator = User.objects.create_user(
            username='demo',
            email='demo@minibooksdemo.com',
            password='demo',
        )
        administrator.first_name = 'Demo'
        administrator.last_name = 'User'
        administrator.is_staff = True
        administrator.is_superuser = True
        administrator.save()
        crm.Profile.objects.create(user=administrator)
    
    people = (
        ('jdoe', 'John', 'Doe', 'johndoe@hometownanimals.com'),
        ('bjohnson', 'Bill', 'Johnson', 'bill@anicecreamshop.com'),
    )
    for username, first_name, last_name, email in people:
        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        user.set_unusable_password()
        user.save()
        profile = crm.Profile.objects.create(user=user)
    
    businesses = (
        ('Home Town Animal Shelter',
            'Small animal shelter in the area',
            'jdoe',
            'Client',
            '444444 Franklin St.',
            'Chapel Hill',
            'NC',
            '27510',
        ),
        ('An Ice Cream Shop',
            'Local ice cream store with homemade flavors!',
            'bjohnson',
            'Client',
            '222222 Rosemary St.',
            'Chapel Hill',
            'NC',
            '27510',
        ),
        ('Coffee Shop', 
            'Where we take clients for a chat',
            None,
            'Vendor',
            None,
            None,
            None,
            None,
        ),
    )
    for name, notes, contact, type, street, city, state, zipcode in businesses:
        if street:
            address = crm.Address.objects.create(
                street=street,
                city=city,
                state=state,
                zip=zipcode,
            )
        else:
            address = None
        business = crm.Business.objects.create(
            name=name,
            notes=notes,
        )
        business.business_types.add(crm.BusinessType.objects.get(name=type))
        if address:
            business.address = address
            business.save()
        if contact:
            business.contacts.add(User.objects.get(username=contact))
    
    jdoe = User.objects.get(username='jdoe')
    bjohnson = User.objects.get(username='bjohnson')
    ice_cream_shop = crm.Business.objects.get(name='An Ice Cream Shop')
    animal_shelter = crm.Business.objects.get(name='Home Town Animal Shelter')
    coffee_shop = crm.Business.objects.get(name='Coffee Shop')
    
    ice_cream_website = crm.Project.objects.create(
        name='Ice Cream Shop website',
        type='software',
        status='accepted',
        description='Simple CMS website',
        business=ice_cream_shop,
        point_person=administrator,
    )
    crm.ProjectRelationship.objects.create(
        user=bjohnson,
        project=ice_cream_website,
    )
    crm.ProjectRelationship.objects.create(
        user=administrator,
        project=ice_cream_website,
    )
    
    animal_shelter_website = crm.Project.objects.create(
        name='Animal Shelter website',
        type='software',
        status='finished',
        description='Custom database driven website with animal listings',
        business=animal_shelter,
        point_person=administrator,
    )
    crm.ProjectRelationship.objects.create(
        user=jdoe,
        project=animal_shelter_website,
    )
    crm.ProjectRelationship.objects.create(
        user=administrator,
        project=animal_shelter_website,
    )
    
    consulting = ledger.Account.objects.get(name='Consulting')
    ar = ledger.Account.objects.get(name='Accounts Receivable')
    checking = ledger.Account.objects.get(name='Checking')
    general_expenses = ledger.Account.objects.get(name='General Expenses')
    
    invoice = ledger.ExchangeType.objects.get(label='Invoice')
    receipt = ledger.ExchangeType.objects.get(label='Receipt')
    purchase = ledger.ExchangeType.objects.get(label='Purchase')
    
    exchange = ledger.Exchange.objects.create(
        memo='Invoice for redesign and implementation of website',
        date=datetime.date(2008, 1, 1),
        date_due=datetime.date(2008, 1, 15),
        type=invoice,
        business=ice_cream_shop,
    )
    exchange.transactions.create(
        date=datetime.date(2008, 1, 1),
        debit=ar,
        credit=consulting,
        project=ice_cream_website,
        memo='Implement simple Django CMS',
        amount='55.0',
        quantity='10',
    )
    exchange.transactions.create(
        date=datetime.date(2008, 1, 1),
        debit=ar,
        credit=consulting,
        project=ice_cream_website,
        memo='Design website',
        amount='75.0',
        quantity='7',
    )
    exchange = ledger.Exchange.objects.create(
        memo='partial payment for website',
        date=datetime.date(2008, 1, 14),
        type=receipt,
        business=ice_cream_shop,
    )
    exchange.transactions.create(
        date=datetime.date(2008, 1, 1),
        debit=checking,
        credit=ar,
        project=ice_cream_website,
        memo='partial payment for website',
        amount='600.0',
        quantity='1.0',
    )
    
    exchange = ledger.Exchange.objects.create(
        memo='Invoice for custom database solution',
        date=datetime.date(2008, 2, 20),
        date_due=datetime.date(2008, 3, 10),
        type=invoice,
        business=animal_shelter,
    )
    exchange.transactions.create(
        date=datetime.date(2008, 2, 5),
        debit=ar,
        credit=consulting,
        project=animal_shelter_website,
        memo='Implement simple Django CMS',
        amount='55.0',
        quantity='10',
    )
    exchange.transactions.create(
        date=datetime.date(2008, 2, 8),
        debit=ar,
        credit=consulting,
        project=animal_shelter_website,
        memo='Animal listing model and interface',
        amount='125.0',
        quantity='25',
    )
    exchange.transactions.create(
        date=datetime.date(2008, 2, 16),
        debit=ar,
        credit=consulting,
        project=animal_shelter_website,
        memo='Patient tracking and appointment calendar',
        amount='125.0',
        quantity='45',
    )
    exchange.transactions.create(
        date=datetime.date(2008, 2, 1),
        debit=ar,
        credit=consulting,
        project=animal_shelter_website,
        memo='Layout and design',
        amount='75.0',
        quantity='10',
    )
    exchange = ledger.Exchange.objects.create(
        memo='partial payment for website',
        date=datetime.date(2008, 2, 25),
        type=receipt,
        business=animal_shelter,
    )
    exchange.transactions.create(
        date=datetime.date(2008, 2, 25),
        debit=checking,
        credit=ar,
        project=animal_shelter_website,
        memo='partial payment for website',
        amount='3000.0',
        quantity='1.0',
    )
    exchange = ledger.Exchange.objects.create(
        memo='partial payment for website',
        date=datetime.date(2008, 3, 1),
        type=receipt,
        business=animal_shelter,
    )
    exchange.transactions.create(
        date=datetime.date(2008, 3, 1),
        debit=checking,
        credit=ar,
        project=animal_shelter_website,
        memo='partial payment for website',
        amount='3000.0',
        quantity='1.0',
    )
    exchange = ledger.Exchange.objects.create(
        memo='partial payment for website',
        date=datetime.date(2008, 3, 10),
        type=receipt,
        business=animal_shelter,
    )
    exchange.transactions.create(
        date=datetime.date(2008, 3, 10),
        debit=checking,
        credit=ar,
        project=animal_shelter_website,
        memo='partial payment for website',
        amount='3000.0',
        quantity='1.0',
    )
    
    
    exchange = ledger.Exchange.objects.create(
        memo='met with potential client',
        date=datetime.date(2008, 3, 10),
        type=purchase,
        business=coffee_shop,
    )
    exchange.transactions.create(
        date=datetime.date(2008, 4, 2),
        debit=general_expenses,
        credit=checking,
        memo='cofee and lunch',
        amount='23.50',
        quantity='1.0',
    )
    
    jdoe.interactions.create(
        date=datetime.date(2008, 2, 14),
        type='phone',
        completed=True,
        project=animal_shelter_website,
        memo='Phone discussion on interface elements',
    )
    
    