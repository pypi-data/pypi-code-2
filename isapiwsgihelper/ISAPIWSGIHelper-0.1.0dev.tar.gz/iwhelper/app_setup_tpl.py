from os import path
import logging
from utils import prependsitedir

#logging.basicConfig(level=logging.INFO,
#                    format='%(asctime)s %(levelname)s %(message)s',
#                    filename=path.dirname(__file__) + '\info.log',
#                    filemode='a')

# setup the virtual environment so that we can import specific versions
# of system libraries and can also import from our local libs directory
spdir = path.join(path.dirname(__file__), '..', 'Lib', 'site-packages')
prependsitedir(spdir)


from sellersburg.applications import make_wsgi
__wsgiapp__ = make_wsgi('Prod')


