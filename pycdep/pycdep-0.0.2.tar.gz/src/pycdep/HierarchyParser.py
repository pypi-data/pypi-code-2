# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Author: stefaan.himpe@gmail.com

from HierarchyViolation import HierarchyViolation

class HierarchyParser(object):
    """
    class to parse a hierarchy.txt file

    hierarchy.txt specifies a hierarchy of projects:
    project living higher are allowed to include from projects living lower,
    but not vice versa.  
    """
    def __init__(self):
        """
        initialize this class 
        """
        pass

    def parse(self, hierarchyfile):
        """
        reads hierarchy.txt and create a set
        of hierarchy violations (i.e. projects which
        cannot include from other projects)
        """
        already_found = set([])
        violations = set([])
        with open(hierarchyfile, "r") as f:
            contents = f.readlines()
            for depth, line in enumerate(contents):
                splitted = line.split(" ")
                for proj in splitted:
                    cleaned_proj = proj.strip()
                    if cleaned_proj:
                        for af in already_found:
                            violations.add(HierarchyViolation(cleaned_proj, af))
                        already_found.add(cleaned_proj)
        return violations

