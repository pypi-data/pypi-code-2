# 
# Copyright (C) 2009  Camptocamp
#  
# This file is part of MapFish Client Plugin.
#  
# MapFish Client Plugin is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# MapFish Client Plugin is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with MapFish Client Plugin.  If not, see <http://www.gnu.org/licenses/>.
#

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

version = '0.2'

setup(name                  = 'mapfish.plugin.client',
      version               = version,
      license               = 'GPLv3',
      install_requires      = ["PasteScript>=1.7.2,<=1.7.99",
                               "Tempita>=0.4,<=0.4.99",
                               "JSTools>=0.1.5,<=0.1.99"],
      zip_safe              = False,
      include_package_data  = True,
      packages              = find_packages(),
      keywords              = 'MapFish JavaScript GeoExt OpenLayers ExtJS',
      author                = 'Camptocamp',
      url                   = 'http://www.mapfish.org',
      description           = "Client plugin of the MapFish Framework.",
      author_email          = 'info@camptocamp.com',
      classifiers           = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Framework :: Paste',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      entry_points          = """
        [paste.paster_create_template]
        mapfish_client = mapfishpluginclient.util:MapFishClientTemplate
        """,
      long_description      = """
      MapFish Client Plugin
      =====================

      The client plugin of the MapFish framework. This plugin provides a Paster
      template for installing the MapFish JavaScript toolbox and a default
      JavaScript web-mapping user interface within MapFish applications.

      Current status
      --------------

      MapFish Client Plugin 0.2 described in this page is the current stable
      version.

      Download and Installation
      -------------------------

      The plugin can be installed with `Easy Install
      <http://peak.telecommunity.com/DevCenter/EasyInstall>`_ by typing::

          > easy_install mapfish.plugin.client
      """
)
