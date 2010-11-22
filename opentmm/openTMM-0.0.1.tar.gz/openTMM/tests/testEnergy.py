import scipy as sp
from openTMM import Layer
import openTMM.tests.utils as utils

#---------------------------------------------------------------------------------------------------
def test(logfile, layerDict, freq, phiDeg):
    numFailedTests = 0
    numTests = 0

    # freq in Hz (range), phiDeg in Deg (range)
    freqSample = 50
    phiSample = 30
    xSample = 100
    numAvgLayersOutside = 0, 5

    freqSet = sp.linspace(freq[0], freq[1], freqSample)
    phiDegSet = sp.linspace(phiDeg[0], phiDeg[1], phiSample)

    for patholMethod in 'keepReal', 'makeComplex':
        layerStack = Layer(layerDict, patholMethod)

        for pol in "parallel", "perp":
            for f in freqSet:
                for phi in phiDegSet:
                    for num in numAvgLayersOutside:
                        numTests += 1
                        omega = 2.0 * sp.pi *f
                        x, u_e, u_m = layerStack.energy(f, phi, xSample, pol, num)
                        x, Q_e, Q_m = layerStack.loss(f, phi, xSample, pol, num)
                        x, divS = layerStack.divPoynting(f, phi, xSample, pol, num)

                        # avoid subtractive cancellation
                        divSscaled = divS / omega
                        LHSimag = divSscaled.imag + 2.0 * u_e
                        RHSimag = 2.0 * u_m
                        ix = divSscaled.imag < 0
                        LHSimag[ix] = divSscaled[ix].imag - 2.0 * u_m[ix]
                        RHSimag[ix] = -2.0 * u_e[ix]
                        
                        testRealPassed = utils.assertApproxEqual(divSscaled.real, -(Q_e+Q_m)/omega)
                        testImagPassed = utils.assertApproxEqual(LHSimag, RHSimag)
                        if not (testRealPassed and testImagPassed):
                            data = {'omega':omega, 'phi':phi} 
                            data['u'] = {}
                            data['u']['u_e'] = u_e
                            data['u']['u_m'] = u_m
                            data['Q'] = {}
                            data['Q']['Q_e'] = Q_e
                            data['Q']['Q_m'] = Q_m
                            data['divS'] = divS
                            
                            
                            msg = 'real part test ' + str(testRealPassed)
                            msg += '.  imag. part test ' + str(testImagPassed)
                            dataSet = logfile.minDataSet(layerStack, layerDict, data, 
                                                         'PoyntingThm', msg)
                            logfile.write(dataSet)
                            numFailedTests
    return numFailedTests, numTests
#---------------------------------------------------------------------------------------------------
def run(logfile):

    def printTestResult(sampleNum, numFailedTests, numTests):
        msg = 'Poynting Thm. test results for sample ' + str(sampleNum) + ' : '
        if numFailedTests == 0:
            msg = msg + 'Passed ' + str(numTests) + ' Tests'
        elif numFailedTests != 0:
            msg = msg + 'Failed ' + str(numFailedTests) + ' of ' + str(numTests) + ' Tests' 
        print msg

    def printTestStatus(sampleNum):
        print 'Performing Poynting Thm. test on sample ' + str(sampleNum) + ' of 5.'
            

    mm = 1.0*10**-3
    GHz = 1.0*10**9

    freqRange = sp.array([100.0, 200.0], float) * GHz
    phiRange = sp.array([0, 89.0], float)

    # 1st Sample, RHM without absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^+}$
    # $\epsilon''_{\ell} = 0, \mu''_{\ell} \} = 0$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 1
    printTestStatus(sampleNum)
    epsRange = sp.array([1.0, 9.0], float)
    muRange = sp.array([1.0, 9.0], float)
    hRange = sp.array([1, 10], float) * mm

    layerDict = utils.randomIdealLayers(epsRange, muRange, hRange, 25)
    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 2nd Sample, RHM with absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^+}$
    # $\epsilon''_{\ell} \in \mathbb{R^+} , \mu''_{\ell} \} = 0$
    #-----------------------------------------------------------------------------------------------
    sampleNum = 2
    printTestStatus(sampleNum)
    epsRange = sp.array([1.0+.001J, 9.0 + 1.0J], complex)
    muRange = sp.array([1.0, 9.0], float)
    hRange = sp.array([1, 10], float) * mm

    layerDict = utils.randomLayers(epsRange, muRange, hRange, 25)
    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 3rd Sample, RHM with absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^+}$
    # $\epsilon''_{\ell} = 0 , \mu''_{\ell} \} \in \mathbb{R^+} $
    #-----------------------------------------------------------------------------------------------
    sampleNum = 3
    printTestStatus(sampleNum)
    epsRange = sp.array([1.0, 15.0], float)
    muRange = sp.array([1.0 + .01J, 9.0 + 0.1J], complex)
    hRange = sp.array([1, 10], float) * mm

    layerDict = utils.randomLayers(epsRange, muRange, hRange, 50)
    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 4th Sample, RHM with absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^+}$
    # $\epsilon''_{\ell} \in \mathbb{R^+} , \mu''_{\ell} \} \in \mathbb{R^+} $
    #-----------------------------------------------------------------------------------------------
    sampleNum = 4
    printTestStatus(sampleNum)
    epsRange = sp.array([1.0 + .01J, 15.0 + 0.5J ], complex)
    muRange = sp.array([1.0 + .01J, 9.0 + 0.1J], complex)
    hRange = sp.array([1, 10], float) * mm

    layerDict = utils.randomLayers(epsRange, muRange, hRange, 50)
    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)


    # 5th Sample, RHM with absorption.
    # $\{ \epsilon'_{\ell}, \mu'_{\ell} \} \in \mathbb{R^+}$
    # $\epsilon''_{\ell} = \in \mathbb{R^+} , \mu''_{\ell} \} \in \mathbb{R^+} $
    # 0th layer is absorbant and pth layer is dielectric.
    #-----------------------------------------------------------------------------------------------
    sampleNum = 5
    printTestStatus(sampleNum)
    epsRangeIdeal = sp.array([1.0, 15.0], float)
    muRangeIdeal = sp.array([1.0, 9.0], float)
    hRangeIdeal = sp.array([1, 10], float) * mm

    epsRange = sp.array([0.1 + 0.001J, 4.0 + 0.1J], complex)
    muRange = sp.array([0.1 + 0.01, 8.0 + 0.05J], complex)
    hRange = sp.array([1, 5], float) * mm 

    layerDictIdeal = utils.randomIdealLayers(epsRangeIdeal, muRangeIdeal, hRangeIdeal, 25)
    layerDictAbsorp = utils.randomLayers(epsRange, muRange, hRange, 25)

    layerDict = utils.shuffleLayers(layerDictIdeal, layerDictAbsorp)
    layerDict['hostMedia'] = {}
    layerDict['hostMedia']['epsilonRelative'] = 2.0 * sp.ones(2, complex)
    layerDict['hostMedia']['muRelative'] = 3.0 * sp.ones(2, complex)    
    layerDict['hostMedia']['epsilonRelative'][0] = 2.5 + 0.5J
    layerDict['hostMedia']['muRelative'][0] = 1.5 + 0.1J

    fNum, total = test(logfile, layerDict, freqRange, phiRange)
    printTestResult(sampleNum, fNum, total)

#---------------------------------------------------------------------------------------------------
