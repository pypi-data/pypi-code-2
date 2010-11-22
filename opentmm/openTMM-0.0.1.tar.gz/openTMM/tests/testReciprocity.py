import scipy as sp
import scipy.constants as constants
import copy
from openTMM import Layer
import openTMM.tests.utils as utils

def test(logfile, layerDict1, layerDict2, freq, phiDeg, energyConserv=False):
    numFailedTests = 0
    numTests = 0

    # freq in Hz (range), phiDeg in Deg (range)
    freqSample = 300 
    phiSample = 100

    freqSet = sp.linspace(freq[0], freq[1], freqSample)
    phiDegSet = sp.linspace(phiDeg[0], phiDeg[1], phiSample)

    for patholMethod in 'keepReal', 'makeComplex':
        layerStack1 = Layer(layerDict1, patholMethod)
        layerStack2 = Layer(layerDict2, patholMethod)

        # Test setChi
        for pol in "parallel", "perp":
            for f in freqSet:
                for phi in sp.deg2rad(phiDegSet):
                    numTests += 1
                    layerStack1.setChi(f, phi, pol)
                    layerStack2.setChi(f, phi, pol)

                    testPassed = utils.assertApproxEqual(sp.absolute(layerStack1.chiPlus[0]), 
                                                         sp.absolute(layerStack2.chiPlus[0]))
                    if not testPassed:
                        data = {'freq': f, 'phi': phi}
                        data['chi'] = {}
                        data['chi']['chi1Plus'] = layerStack1.chiPlus[0]
                        data['chi']['chi2Plus'] = layerStack2.chiPlus[0]

                        dataSet = logfile.minDataSet(layerStack1, layerDict1, data, 'reciprocityChi')
                        logfile.write(dataSet)
                        numFailedTests += 1


        # Test getTRvsFrequencyAndAngle
        for pol in "parallel", "perp":
            numTests += 1
            f1, phi1, T1, R1 = layerStack1.TRvsFreqAndAngle(freq[0], freq[1], freqSample,
                                                            phiDeg[0], phiDeg[1], phiSample, pol)
            f2, phi2, T2, R2 = layerStack2.TRvsFreqAndAngle(freq[0], freq[1], freqSample,
                                                            phiDeg[0], phiDeg[1], phiSample, pol)

            testPassed = utils.assertApproxEqual(T1, T2)
            if not testPassed:
                data = {'freqData':(freq[0], freq[1], freqSample), 
                        'phiData':(phiDeg[0], phiDeg[1], phiSample)} 
                data['T'] = {}
                data['T']['T1'] = T1
                data['T']['T2'] = T2
            
                dataSet = logfile.minDataSet(layerStack1, layerDict1, data, 
                                             'reciprocityTRvsFreqAndAngle')
                logfile.write(dataSet)
                numFailedTests += 1

            if energyConserv:
                numTests += 1
                testPassed = utils.assertApproxEqual(R1, R2)
                if not testPassed:
                    data = {'freqData':(freq[0], freq[1], freqSample), 
                            'phiData':(phiDeg[0], phiDeg[1], phiSample)} 
                    data['R'] = {}
                    data['R']['R1'] = R1
                    data['R']['R2'] = R2
                
                    dataSet = logfile.minDataSet(layerStack1, layerDict1, data, 
                                                 'reciprocityTRvsFreqAndAngle')
                    logfile.write(dataSet)
                    numFailedTests += 1
            
    return numFailedTests, numTests
#---------------------------------------------------------------------------------------------------
def run(logfile):

    def printTestResult(sampleNum, numFailedTests, numTests):
        msg = 'Reciprocity test results for sample ' + str(sampleNum) + ' : '
        if numFailedTests == 0:
            msg = msg + 'Passed ' + str(numTests) + ' Tests'
        elif numFailedTests != 0:
            msg = msg + 'Failed ' + str(numFailedTests) + ' of ' + str(numTests) + ' Tests' 
        print msg

    def printTestStatus(sampleNum):
        print 'Performing reciprocity test on sample ' + str(sampleNum) + ' of 10.'
            

    mm = 1.0*10**-3
    GHz = 1.0*10**9

    freqRange = sp.array([100.0, 150.0], float) * GHz
    phiRange = sp.array([0, 89.0], float)


    # 1st Sample, RHM without absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in mathbb{R^+}$
    # $\epsilon''_{\ell} = 0, \mu''_{\ell} \} = 0$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 1
    printTestStatus(sampleNum)
    epsRange = sp.array([1.0, 9.0], float)
    muRange = sp.array([1.0, 9.0], float)
    hRange = sp.array([1, 3], float) * mm

    layerDict1 = utils.randomIdealLayers(epsRange, muRange, hRange, 10)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange, energyConserv=True)
    printTestResult(sampleNum, fNum, total)


    # 2nd Sample, LHM without absorption.
    # \{ $\epsilon'_{\ell}, \mu'_{\ell} \} \in mathbb{R^-}$
    # $\epsilon''_{\ell} = 0, \mu''_{\ell} \} = 0$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 2
    printTestStatus(sampleNum)
    layerDict1['epsilonRelative'] *= -1.0
    layerDict1['muRelative'] *= -1.0
    layerDict2['epsilonRelative'] *= -1.0
    layerDict2['muRelative'] *= -1.0

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange, energyConserv=True)
    printTestResult(sampleNum, fNum, total)


    # 3rd Sample, RHM with absorption.
    # \{ $\epsilon'_{\ell}, \mu'_{\ell} \} \in mathbb{R^+}$
    # $\epsilon''_{\ell} = \in \mathbb{R^+}, \mu''_{\ell} = 0$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 3
    printTestStatus(sampleNum)
    epsRange = sp.array([1.0 + .01J, 9.0 + .1J], complex)
    muRange = sp.array([1.0, 9.0], float)
    hRange = sp.array([1, 3], float) * mm

    layerDict1 = utils.randomLayers(epsRange, muRange, hRange, 10)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 4th Sample, LHM with absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^-}$
    # $\epsilon''_{\ell} = \in \mathbb{R^+}, \mu''_{\ell} = 0$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 4
    printTestStatus(sampleNum)
    epsRange = sp.array([-1.0 + .01J, -9.0 + .1J], complex)
    muRange = sp.array([-1.0, -9.0], float)
    hRange = sp.array([1, 3], float) * mm

    layerDict1 = utils.randomLayers(epsRange, muRange, hRange, 10)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 5th Sample, RHM with absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^+}$
    # $\{ \epsilon''_{\ell}, \mu''_{\ell} \} \in \mathbb{R^+}$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 5
    printTestStatus(sampleNum)
    epsRange = sp.array([1.0 + .01J, 9.0 + .1J], complex)
    muRange = sp.array([1.0 + .01J, 9.0 + .1J], complex)
    hRange = sp.array([1, 3], float)*mm

    layerDict1 = utils.randomLayers(epsRange, muRange, hRange, 10)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 6th Sample, LHM with absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^-}$
    # $\{ \epsilon''_{\ell}, \mu''_{\ell} \} \in \mathbb{R^+}$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 6
    printTestStatus(sampleNum)
    epsRange = sp.array([-1.0 + .01J, -9.0 + .1J], complex)
    muRange = sp.array([-1.0 + .01J, -9.0 + .1J], complex)
    hRange = sp.array([1, 3], float)*mm

    layerDict1 = utils.randomLayers(epsRange, muRange, hRange, 10)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 7th Sample, RHM and LHM with absorption
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^{\pm}}$
    # $\{ \epsilon''_{\ell}, \mu''_{\ell} \} \in \mathbb{R^+}$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 7
    printTestStatus(sampleNum)
    epsRangeRHM = sp.array([.1 + .01J, 10.0 + 1.0J], complex)
    muRangeRHM = sp.array([.1 + .01J, 10.0 + 1J], complex)
    hRangeRHM = sp.array([.1, 10], float) * mm
    layerDictRHM = utils.randomLayers(epsRangeRHM, muRangeRHM, hRangeRHM, 25)

    epsRangeLHM = sp.array([-.1 + .01J, -10.0 + 1.0J], complex)
    muRangeLHM = sp.array([-.1 + .01J, -10.0 + 1J], complex)
    hRangeLHM = sp.array([.1, 10], float) * mm
    layerDictLHM = utils.randomLayers(epsRangeLHM, muRangeLHM, hRangeLHM, 25)

    layerDict1 = utils.shuffleLayers(layerDictRHM, layerDictLHM)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 8th Sample, RHM and LHM with/without absorption and RHM hostMedia
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^{\pm}}$
    # $\{ \epsilon''_{\ell}, \mu''_{\ell} \} \in \mathbb{R^+} or 0$
    # $\epsilon'_0 = \epsilon_p > 1, \mu'_0 = \mu'_p > 1$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 8
    printTestStatus(sampleNum)
    epsRangeRHM = sp.array([.1 + .01J, 10.0 + 1.0J], complex)
    muRangeRHM = sp.array([.1 + .01J, 10.0 + 1J], complex)
    hRangeRHM = sp.array([.1, 1.0], float) * mm
    layerDictRHM = utils.randomLayers(epsRangeRHM, muRangeRHM, hRangeRHM, 25)

    epsRangeRHMideal = sp.array([.1, 10.0], float)
    muRangeRHMideal = sp.array([.1, 10.0], float)
    hRangeRHMideal = sp.array([.1, 10.0], float) * mm
    layerDictRHMideal = utils.randomIdealLayers(epsRangeRHMideal, muRangeRHMideal, 
                                                hRangeRHMideal, 25)

    epsRangeLHM = sp.array([-.1 + .01J, -10.0 + 1.0J], complex)
    muRangeLHM = sp.array([-.1 + .01J, -10.0 + 1J], complex)
    hRangeLHM = sp.array([.1, 1.0], float) * mm
    layerDictLHM = utils.randomLayers(epsRangeLHM, muRangeLHM, hRangeLHM, 25)

    epsRangeLHMideal = sp.array([-.1, -5.0], float)
    muRangeLHMideal = sp.array([-.1, -3.0], float)
    hRangeLHMideal = sp.array([.1, 2.0], float) * mm
    layerDictLHMideal = utils.randomIdealLayers(epsRangeLHMideal, muRangeLHMideal, 
                                                 hRangeLHMideal, 25)

    layerDictWithAbsorption = utils.shuffleLayers(layerDictRHM, layerDictLHM)
    layerDictWithoutAbsorption = utils.shuffleLayers(layerDictRHMideal, layerDictLHMideal)
    layerDict1 = utils.shuffleLayers(layerDictWithAbsorption, layerDictWithoutAbsorption)
    layerDict1['hostMedia'] = {}
    layerDict1['hostMedia']['epsilonRelative'] = 2.0 * sp.ones(2, float)
    layerDict1['hostMedia']['muRelative'] = 3.0 * sp.ones(2, float)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 9th Sample, RHM and LHM without absorption and LHM hostMedia.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^{\pm}}$
    # $\epsilon''_{\ell} = 0, \mu''_{\ell} \} = 0$
    # $\epsilon'_0 = \epsilon_p < -1, \mu'_0 = \mu'_p < -1$
    # -----------------------------------------------------------------------------------------------
    sampleNum = 9
    printTestStatus(sampleNum)
    MHz = 1.0*10**6
    freqRange = sp.array([100.0, 150.0], float) * MHz
    period = constants.c/freqRange[0]

    epsRangeRHM = sp.array([1.0, 5.0], float)
    muRangeRHM = sp.array([1.0, 5.0], float)
    hRangeRHM = sp.array([.1, 1.0], float) * period
    layerDictRHM = utils.randomIdealLayers(epsRangeRHM, muRangeRHM, hRangeRHM, 25)

    epsRangeLHM = sp.array([-1, -5], float)
    muRangeLHM = sp.array([-1, -5], float)
    hRangeLHM = sp.array([.1, 1.0], float) * period
    layerDictLHM = utils.randomIdealLayers(epsRangeLHM, muRangeLHM, hRangeLHM, 25)

    layerDict1 = utils.shuffleLayers(layerDictRHM, layerDictLHM)
    layerDict1['hostMedia'] = {}
    layerDict1['hostMedia']['epsilonRelative'] = -3.0 * sp.ones(2, float)
    layerDict1['hostMedia']['muRelative'] = -1.5 * sp.ones(2, float)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange, energyConserv=True)
    printTestResult(sampleNum, fNum, total)


    # 10th Sample, RHM and LHM with absorption and LHM hostMedia.
    # $ 0 < \{ \epsilon'_{\ell}, \mu'_{\ell} \} < 1$ or 
    # $ -1 < \{ \epsilon'_{\ell}, \mu'_{\ell} \} < 0$
    # $\{ \epsilon''_{\ell} = 0, \mu''_{\ell} \} \in \mathbb{R^+}$
    # $\epsilon'_0 = \epsilon_p < -1, \mu'_0 = \mu'_p < -1$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 10
    printTestStatus(sampleNum)
    MHz = 1.0*10**6
    freqRange = sp.array([100.0, 150.0], float) * MHz
    period = constants.c/freqRange[0]

    epsRangeRHM = sp.array([.01 + .1J, .9 + 1.0J], complex)
    muRangeRHM = sp.array([.01 + .01J, .9 + .1J], complex)
    hRangeRHM = sp.array([.1, 1], float) * period
    layerDictRHM = utils.randomLayers(epsRangeRHM, muRangeRHM, hRangeRHM, 25)

    epsRangeLHM = sp.array([-.9 + .1J, -.01 + 1.0J], complex)
    muRangeLHM = sp.array([-.9 + .01J, -.1 + .1J], complex)
    hRangeLHM = sp.array([.1, 1], float) * period
    layerDictLHM = utils.randomLayers(epsRangeLHM, muRangeLHM, hRangeLHM, 25)

    layerDict1 = utils.shuffleLayers(layerDictRHM, layerDictLHM)
    layerDict1['hostMedia'] = {}
    layerDict1['hostMedia']['epsilonRelative'] = -1.1 * sp.ones(2, float)
    layerDict1['hostMedia']['muRelative'] = -1.3 * sp.ones(2, float)

    layerDict2 = copy.deepcopy(layerDict1)
    layerDict2['epsilonRelative'] = layerDict2['epsilonRelative'][::-1]
    layerDict2['muRelative'] = layerDict2['muRelative'][::-1]
    layerDict2['height'] = layerDict2['height'][::-1]

    fNum, total = test(logfile, layerDict1, layerDict2, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)
#---------------------------------------------------------------------------------------------------
