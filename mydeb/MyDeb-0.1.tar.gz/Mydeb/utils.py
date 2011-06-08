# -----------------------------------------------------------------------------
#    Myconf - Personal configuration and installed software backup
#    Copyright (C) 2011 Some Hackers In Town

#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# -----------------------------------------------------------------------------


def parse_config_file(file_):
    """
    Parse the config file and return the list of backup targets
    and a set of packages.
    """

    data = file(file_).readlines()
    targets = list()
    packages = list()

    for line in data:
        parsed_data = line.split(":")
        targets.append(parsed_data[0])
        if len(parsed_data) == 2:
            packages.append(parsed_data[1])
    return (targets, list(set(packages)))
