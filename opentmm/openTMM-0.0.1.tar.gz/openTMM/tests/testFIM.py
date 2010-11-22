import scipy as sp
from openTMM import Layer
import openTMM.tests.utils as utils

#---------------------------------------------------------------------------------------------------
def test(logfile, layerDict, freq, phiDeg):
    numFailedTests = 0
    numTests = 0

    # freq in Hz (range), phiDeg in Deg (range)
    freqSample = 300
    phiSample = 100

    freqSet = sp.linspace(freq[0], freq[1], freqSample)
    phiDegSet = sp.linspace(phiDeg[0], phiDeg[1], phiSample)

    for patholMethod in 'keepReal', 'makeComplex':
        layerStack = Layer(layerDict, patholMethod)

        for pol in "parallel", "perp":
            for f in freqSet:
                for phi in phiDegSet:
                    numTests += 1
                    FIMbottom, FIMtop = layerStack.FIM(f, phi, pol)
                    testPassed = utils.assertApproxEqual(sp.absolute(FIMbottom), sp.absolute(FIMtop))
                    
                    if not testPassed:
                        data = {'freq':f, 'phi':phi} 
                        data['FIM'] = {}
                        data['FIM']['FIMbottom'] = FIMbottom
                        data['FIM']['FIMtop'] = FIMtop
                        dataSet = logfile.minDataSet(layerStack, layerDict, data, 'FIM')
                        logfile.write(dataSet)
                        numFailedTests += 1
    return numFailedTests, numTests
#---------------------------------------------------------------------------------------------------
def run(logfile):

    def printTestResult(sampleNum, numFailedTests, numTests):
        msg = 'FIM test results for sample ' + str(sampleNum) + ' : '
        if numFailedTests == 0:
            msg = msg + 'Passed ' + str(numTests) + ' Tests'
        elif numFailedTests != 0:
            msg = msg + 'Failed ' + str(numFailedTests) + ' of ' + str(numTests) + ' Tests' 
        print msg

    def printTestStatus(sampleNum):
        print 'FIM test on sample ' + str(sampleNum) + ' of 5.'
            

    mm = 1.0*10**-3
    GHz = 1.0*10**9

    freqRange = sp.array([50.0, 200.0], float) * GHz
    phiRange = sp.array([0, 89.0], float)

    # 1st Sample, RHM with and without absorption.
    #-----------------------------------------------------------------------------------------------
    sampleNum = 1
    printTestStatus(sampleNum)

    epsRangeIdeal = sp.array([0.01, 15.0], float)
    muRangeIdeal = sp.array([0.01, 15.0], float)
    hRangeIdeal = sp.array([1, 10], float) * mm
    layerDict1 = utils.randomIdealLayers(epsRangeIdeal, muRangeIdeal, hRangeIdeal, 25)

    epsRange = sp.array([0.01 + 0.001J, 15.0 + 1.0J], complex)
    muRange = sp.array([0.01 + 0.01J, 15.0 + 0.5J], complex)
    hRange = sp.array([1, 5], float) * mm
    layerDict2 = utils.randomLayers(epsRange, muRange, hRange, 25)

    layerDict = utils.shuffleLayers(layerDict1, layerDict2)
    layerDict['hostMedia'] = {}
    layerDict['hostMedia']['epsilonRelative'] = 2.0 * sp.ones(2, complex)
    layerDict['hostMedia']['muRelative'] = 3.0 * sp.ones(2, complex)    
    layerDict['hostMedia']['epsilonRelative'][0] = 2.5 + 0.05J
    layerDict['hostMedia']['muRelative'][0] = 1.5 + 0.01J

    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 2nd Sample, LHM with and without absorption.
    #-----------------------------------------------------------------------------------------------
    sampleNum = 2
    printTestStatus(sampleNum)

    epsRangeIdeal = sp.array([-0.01, -15.0], float)
    muRangeIdeal = sp.array([-0.01, -15.0], float)
    hRangeIdeal = sp.array([1, 10], float) * mm
    layerDict1 = utils.randomIdealLayers(epsRangeIdeal, muRangeIdeal, hRangeIdeal, 20)

    epsRange = sp.array([-0.01 + 0.001J, -15.0 + 1.0J], complex)
    muRange = sp.array([-0.01 + 0.01J, -15.0 + 0.5J], complex)
    hRange = sp.array([1, 5], float) * mm
    layerDict2 = utils.randomLayers(epsRange, muRange, hRange, 20)

    layerDict = utils.shuffleLayers(layerDict1, layerDict2)
    layerDict['hostMedia'] = {}
    layerDict['hostMedia']['epsilonRelative'] = -2.0 * sp.ones(2, complex)
    layerDict['hostMedia']['muRelative'] = -3.0 * sp.ones(2, complex)    
    layerDict['hostMedia']['epsilonRelative'][0] = -2.5 + 0.05J
    layerDict['hostMedia']['muRelative'][0] = -1.5 + 0.01J

    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 3rd Sample, LHM and RHM with absorption.
    #-----------------------------------------------------------------------------------------------
    sampleNum = 3
    printTestStatus(sampleNum)

    epsRangeLHM = sp.array([-0.01 + 0.01J, -10.0 + 0.09J], complex)
    muRangeLHM = sp.array([-0.1 + 0.001J, -11.0 + 0.05J ], complex)
    hRangeLHM = sp.array([1, 5], float) * mm
    layerDictLHM = utils.randomLayers(epsRangeLHM, muRangeLHM, hRangeLHM, 15)

    epsRangeRHM = sp.array([0.01 + 0.001J, 15.0 + 0.1J], complex)
    muRangeRHM = sp.array([0.01 + 0.01J, 5.0 + 0.05J], complex)
    hRangeRHM = sp.array([1, 10], float) * mm
    layerDictRHM = utils.randomLayers(epsRangeRHM, muRangeRHM, hRangeRHM, 15)

    layerDict = utils.shuffleLayers(layerDictLHM, layerDictRHM)
    layerDict['hostMedia'] = {}
    layerDict['hostMedia']['epsilonRelative'] = 2.0 * sp.ones(2, complex)
    layerDict['hostMedia']['muRelative'] = 3.0 * sp.ones(2, complex)    
    layerDict['hostMedia']['epsilonRelative'][0] = -2.5 + 0.05J
    layerDict['hostMedia']['muRelative'][0] = -1.5 + 0.01J

    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 4th Sample, LHM and RHM without absorption.
    #-----------------------------------------------------------------------------------------------
    sampleNum = 4
    printTestStatus(sampleNum)

    epsRangeLHM = sp.array([-0.01, -5.0], float)
    muRangeLHM = sp.array([-0.1, -11.0], float)
    hRangeLHM = sp.array([1, 20], float) * mm
    layerDictLHM = utils.randomIdealLayers(epsRangeLHM, muRangeLHM, hRangeLHM, 15)

    epsRangeRHM = sp.array([0.01, 15.0], float)
    muRangeRHM = sp.array([0.1, 10.0], float)
    hRangeRHM = sp.array([1, 10], float) * mm
    layerDictRHM = utils.randomIdealLayers(epsRangeRHM, muRangeRHM, hRangeRHM, 15)

    layerDict = utils.shuffleLayers(layerDictLHM, layerDictRHM)
    layerDict['hostMedia'] = {}
    layerDict['hostMedia']['epsilonRelative'] = -2.0 * sp.ones(2, float)
    layerDict['hostMedia']['muRelative'] = -3.0 * sp.ones(2, float)    
    layerDict['hostMedia']['epsilonRelative'][-1] = 2.5
    layerDict['hostMedia']['muRelative'][-1] = 1.5

    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 5th Sample, LHM and RHM with/without absorption.
    #-----------------------------------------------------------------------------------------------
    sampleNum = 5
    printTestStatus(sampleNum)

    epsRangeLHMideal = sp.array([-0.01, -10.0], float)
    muRangeLHMideal = sp.array([-0.1, -11.0], float)
    hRangeLHMideal = sp.array([1, 20], float) * mm
    layerDictLHMideal = utils.randomIdealLayers(epsRangeLHMideal, muRangeLHMideal, hRangeLHMideal, 5)

    epsRangeLHMabsorp = sp.array([-0.1 + 0.01J, -10.0 + 0.03J], complex)
    muRangeLHMabsorp = sp.array([-0.1, -11.0], float)
    hRangeLHMabsorp = sp.array([1, 8], float) * mm
    layerDictLHMabsorp = utils.randomLayers(epsRangeLHMabsorp, muRangeLHMabsorp, hRangeLHMabsorp, 5)

    layerDictLHM = utils.shuffleLayers(layerDictLHMideal, layerDictLHMabsorp)

    epsRangeRHMideal = sp.array([0.01, 15.0], float)
    muRangeRHMideal = sp.array([1.5, 5.0], float)
    hRangeRHMideal = sp.array([1, 10], float) * mm
    layerDictRHMideal = utils.randomIdealLayers(epsRangeRHMideal, muRangeRHMideal, hRangeRHMideal, 5)

    epsRangeRHMabsorp = sp.array([1.1, 10.0], float)
    muRangeRHMabsorp = sp.array([0.1 + 0.001J, -11.0 + 0.03J], complex)
    hRangeRHMabsorp = sp.array([1, 5], float) * mm
    layerDictRHMabsorp = utils.randomLayers(epsRangeRHMabsorp, muRangeRHMabsorp, hRangeRHMabsorp, 5)

    layerDictRHM = utils.shuffleLayers(layerDictRHMideal, layerDictRHMabsorp)

    layerDict = utils.shuffleLayers(layerDictLHM, layerDictRHM)

    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)
#---------------------------------------------------------------------------------------------------
