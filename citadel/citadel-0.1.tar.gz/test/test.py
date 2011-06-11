from citadel import Citadel

import config

citadel = Citadel(config)
print citadel.INFO()
print '\n'.join(citadel.listu())
citadel.close()
