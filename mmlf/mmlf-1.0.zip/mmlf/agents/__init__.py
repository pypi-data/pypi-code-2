# Maja Machine Learning Framework
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.


import os
import re

try:
    # The pattern which python modules have to match
    module_pattern = re.compile("[a-zA-Z0-9][a-zA-Z0-9_]*.py$")
    
    # The root of the search (should be the agents directory)
    root = os.sep.join(__file__.split(os.sep)[:-1])
    
    # The global dict of MMLF Agents
    MMLF_AGENTS = {}
    
    # search all modules in the directory
    for file_name in os.listdir(root):
        # Compute the package path for the current directory
        dir_path = root.split(os.sep)
        # Find the last occurrence of "MMLF" in the path
        mmlf_index = None
        for index, token in enumerate(dir_path):
            if token == "mmlf": mmlf_index = index
        dir_path = dir_path[mmlf_index:]
        package_path = ".".join(dir_path)
        # Check all files if they are python modules
        if module_pattern.match(file_name):
            # Import the module
            module_name = file_name.split(".")[0]
            module_path = package_path + '.' + module_name
            module = __import__(module_path, {}, {}, ["dummy"])
            # If this module exports MDP nodes
            if hasattr(module, "AgentClass"):
                MMLF_AGENTS[module.AgentName] = {"module_name": module_name,
                                                 "agent_class": module.AgentClass}
    
    # Clean up...
    del(os, re, module_pattern, root, dir_path, mmlf_index, index, token,
        package_path, module_name, module_path, module, file_name)
except Exception, e:
    print e
    pass