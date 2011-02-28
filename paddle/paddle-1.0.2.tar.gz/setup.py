
from setuptools import setup
import paddle

long_description = """
**PADDLE** is a Python package for learning dictionaries with frame-like 
properties, as well as achieving sparse coding of the training data.
In particular, it provides algorithms for

- learning a dictionary together with a dual of itself, and

- learning a dictionary close to a tigth-frame.

PADDLE's license is free for both commercial and non-commercial use, under the `BSD terms <http://www.opensource.org/licenses/bsd-license.php>`_.
"""

setup(name = 'paddle',
      version = paddle.__version__,
      description = 'A package for dictionary learning',
      long_description = long_description,
      author = 'Curzio Basso',
      author_email = 'curzio.basso@gmail.com',
      url = 'http://slipguru.disi.unige.it/Research/PADDLE',
      download_url = 'http://slipguru.disi.unige.it/Research/PADDLE/PADDLE-latest.tar.gz',
      license = 'BSD',
      #classifiers = [],
      #py_modules = ['paddleDual', 'paddleTF']
      packages = ['paddle', 'paddle/examples']
      )
