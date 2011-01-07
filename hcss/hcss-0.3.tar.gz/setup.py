"""
hcss is a CSS compiler that that allows you to use HTML element hierarchy to
define CSS rules. Requires Python 2.2+. BSD-licensed.

Input
`````

::

    <div id="parent">
      margin: 10px;
      <div class="child">
        margin: 5px;
        border: 1px solid #000;
      </div>
    </div>
    
Output
``````

::

    div#parent {
      margin: 10px;
    }
    div#parent > div.child {
      margin: 5px;
      border: 1px solid #000;
    }

Setup
`````

::

    $ pip install hcss # or
    $ easy_install hcss

Links
`````

* `Full documentation <http://jonasgalvez.com.br/Software/HCSS.html>`_
* `Development repository <http://github.com/galvez/hcss/>`_
* `Author's website <http://jonasgalvez.com.br/>`_

"""

from setuptools import setup

setup(
    name = 'hcss',
    version = '0.3',
    url = 'http://jonasgalvez.com.br/Software/HCSS.html',
    license = 'BSD',
    author = "Jonas Galvez",
    author_email = "jonasgalvez@gmail.com",
    description = "hcss is a CSS compiler that that allows you to use HTML element hierarchy to define CSS rules",
    long_description = __doc__,
    py_modules = ['hcss'],
    platforms = 'Python 2.5 and later',
    entry_points = {
        'console_scripts': [
            'hcss = hcss:main',
        ]
    },
    classifiers = [
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Text Processing :: Markup :: HTML'
    ]
)
