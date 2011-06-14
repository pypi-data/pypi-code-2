# import the Citadel class according to your PYTHONPATH
from citadel.citadel import Citadel

# get the "config" oject (anyway you want)
import config

# instantiate the Citadel class passing it the "config" object
# connecting to the server
citadel = Citadel(config)

# print server infos, showing everything is okay
print citadel.server()

# create a new user
# implicity log in as "admin"
# ! admin login and password will be seen in the log file !
citadel.create_user('john', 'password', 'john', 'wayne')

# list users
for usr in citadel.users: print usr

# log in as john
#  ! "password" will appear in the log file !
citadel.login('john', 'password')

# send a mail to zorro (which must exist)
citadel.mail('zorro', 'subject', 'message')

# log out
citadel.logout()

# delete user
citadel.deluser('john')

# close the connection
citadel.close()
