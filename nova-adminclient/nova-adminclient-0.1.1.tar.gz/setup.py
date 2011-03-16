# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
from setuptools import setup, find_packages


setup(name = "nova-adminclient",
      version = "0.1.1",
      license = 'Apache 2.0',
      description = "client for administering OpenStack Nova",
      author = 'OpenStack',
      author_email = 'nova@lists.launchpad.net',
      url='http://www.openstack.org',
      packages = find_packages('nova_adminclient'),
      package_dir = {'': 'nova_adminclient'},
      install_requires = ['setuptools', 'boto==1.9b'],
      classifiers = [
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.6',
          'Topic :: Internet :: WWW/HTTP'])

