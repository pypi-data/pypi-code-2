import os.path

try:
    from Products.salesforcebaseconnector.tests import sfconfig
except ImportError:
    print ('These tests require API access to Salesforce. Please provide your credentials. '
           '(They will be saved to the sfconfig.py file for future use.)')
    username = raw_input('Username? ')
    password = raw_input('Password? ')
    token = raw_input('Token? ')
    
    config = open(os.path.join(os.path.dirname(__file__), 'sfconfig.py'), 'w')
    config.write("USERNAME='%s'\nPASSWORD='%s%s'" %
        tuple([s.replace("'", r"\'") for s in (username, password, token)]))
    config.close()
    from Products.salesforcebaseconnector.tests import sfconfig
