import sys; sys.path.append('..')
SERVICES_DIR = '.'

# Test executing local core services
from wille.services import LocalService
from upload_test.upload_test import checksum_simple
import sys

# Local service, only string parameters
tidy = LocalService(SERVICES_DIR, 'timeout_test', '../../libs')
result1 = tidy.execute({'timeout':'1'})
assert( result1.success() )

# Local service, (PDF) file as a parameter
upload_test = LocalService(SERVICES_DIR, 'upload_test', '../../libs')
raw_data = open('data/illformed.html','rb').read()
calc_checksum = checksum_simple(raw_data)
result2 = upload_test.execute({'raw_data':raw_data, 'checksum': str(calc_checksum)})
assert( result2.success() )
