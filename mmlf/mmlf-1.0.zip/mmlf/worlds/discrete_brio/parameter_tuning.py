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

import sys
import subprocess
from resources.optimization.cma_es import CMA_ES

def adapt(arg,value):
    if sys.argv[1] == "sarsa_lambda_agent":
        if arg==0:
            if value==1:
                return "epsilon"
            if value==2:
                return "lambda"
            if value==3:
                return "minTraceValue"
        if arg==1:
            epsilon=(value+2)/4.0-0.49
            if epsilon>1.0:
                epsilon=1.0
            if epsilon<0.0:
                epsilon=0.0
            return epsilon
        if arg==2:
            lambd=(value+2)/4.0
            if lambd>1.0:
                lambd=1.0
            if lambd<0.0:
                lambd=0.0
            return lambd
        if arg==3:
            minTraceValue=(value+2)/4.0
            if minTraceValue>1.0:
                minTraceValue=1.0
            if minTraceValue<0.0:
                minTraceValue=0.0
            return minTraceValue
    if sys.argv[1] == "q_lambda_agent":
        if arg==0:
            if value==1:
                return "epsilon"
            if value==2:
                return "lambda"
            if value==3:
                return "minTraceValue"
        if arg==1:
            epsilon=(value+2)/4.0-0.4
            if epsilon>1.0:
                epsilon=1.0
            if epsilon<0.0:
                epsilon=0.0
            return epsilon
        if arg==2:
            lambd=(value+2)/4.0
            if lambd>1.0:
                lambd=1.0
            if lambd<0.0:
                lambd=0.0
            return lambd
        if arg==3:
            minTraceValue=(value+2)/4.0
            if minTraceValue>1.0:
                minTraceValue=1.0
            if minTraceValue<0.0:
                minTraceValue=0.0
            return minTraceValue
    if sys.argv[1] == "dyna_td_agent":
        if arg==0:
            if value==1:
                return "epsilon"
            if value==2:
                return "updatesPerStep"
            if value==3:
                return "minSweepDelta"
        if arg==1:
            epsilon=(value+2)/4.0-0.4
            if epsilon>1.0:
                epsilon=1.0
            if epsilon<0.0:
                epsilon=0.0
            return epsilon
        if arg==2:
            updatesPerStep=int((value+2)*12.5)
            if updatesPerStep>100:
                updatesPerStep=100
            if updatesPerStep<0:
                updatesPerStep=0
            return updatesPerStep
        if arg==3:
            minSweepDelta=(value+2)/4.0
            if minSweepDelta>1.0:
                minSweepDelta=1.0
            if minSweepDelta<0.0:
                minSweepDelta=0.0
            return minSweepDelta
if __name__ == '__main__':
    # set options

    # pt dyna_td_agent parameters: epsilon, updatesPerStep, gamma
    cma_es = CMA_ES(dims=3, episodesPerPolicy=2, initialMean=(0.0, 0.0, 0.0) )

    # main loop, loops as many individuals are gathered
    for i in range(1000):
        currentIndividual = cma_es.getActiveIndividual()

        arg1 = adapt(1,currentIndividual[0])
        arg2 = adapt(2,currentIndividual[1])
        arg3 = adapt(3,currentIndividual[2])

        gamma = 0.9
        # start the mmlf process
        output = subprocess.Popen([
                sys.path[0]+"/execTrial.sh",
                sys.argv[1],
                "100000",
                str(arg1),
                str(arg2),
                str(gamma),
                str(arg3)
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        # parse the return from the outpu
        ret = output.split('\n')[-2].split(' ')[-1]
        # print some feedback
        print "currentIndividual:",adapt(0,1),arg1,adapt(0,2),arg2,adapt(0,3),arg3," ret:",int(ret)
        # hand the value over to cma_es
        cma_es.tellFitness(int(ret))
        # get the best individual
        bestIndividual = cma_es.getBestIndividual()
        if len(bestIndividual) > 0:
            arg1 = adapt(1, bestIndividual[0])
            arg2 = adapt(2, bestIndividual[1])
            arg3 = adapt(3, bestIndividual[2])
            print "best:",adapt(0,1),arg1,adapt(0,2),arg2,adapt(0,3),arg3
    # get the best individual
    bestIndividual = cma_es.getBestIndividual()
    arg1 = adapt(1, bestIndividual[0])
    arg2 = adapt(2, bestIndividual[1])
    arg3 = adapt(3, bestIndividual[2])
    print "best:",adapt(0,1),arg1,adapt(0,2),arg2,adapt(0,3),arg3
