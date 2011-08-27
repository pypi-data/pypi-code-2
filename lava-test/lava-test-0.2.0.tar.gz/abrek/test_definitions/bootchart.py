# Copyright (c) 2011 Linaro
#
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

import abrek.testdef

INSTALLSTEPS = ['bzr branch lp:~linaro-foundations/lava-test/bootchartscript']
DEPS = ['bootchart', 'pybootchartgui', 'bzr']
RUNSTEPS = ['./bootchartscript/bootchartscript.sh']
PATTERN = "^(?P<test_case_id>\w+):\W+(?P<measurement>\d+\.\d+)"

bootchartinst = abrek.testdef.AbrekTestInstaller(INSTALLSTEPS, deps=DEPS)
bootchartrun = abrek.testdef.AbrekTestRunner(RUNSTEPS)
bootchartparser = abrek.testdef.AbrekTestParser(PATTERN,
                   appendall={'units':'sec', 'result':'pass'})
testobj = abrek.testdef.AbrekTest(testname="bootchart", installer=bootchartinst,
                                  runner=bootchartrun, parser=bootchartparser)
