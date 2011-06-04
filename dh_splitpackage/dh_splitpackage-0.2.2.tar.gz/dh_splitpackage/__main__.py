# Copyright (C) 2011 Canonical
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# This file is part of dh_splitpackage.
#
# dh_splitpackage is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3
# as published by the Free Software Foundation
#
# dh_splitpackage is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dh_splitpackage.  If not, see <http://www.gnu.org/licenses/>.

from dh_splitpackage import SplitPackage 


def main():
    SplitPackage().run()


if __name__ == "__main__":
    main()
