import scipy as sp
import openTMM.tests.logFile as LF

#---------------------------------------------------------------------------------------------------
def randomIdealLayers(epsRelRange, muRelRange, hRange, numLayers):
    sp.random.seed()

    epsRel = sp.random.uniform(epsRelRange[0], epsRelRange[1], numLayers)
    muRel = sp.random.uniform(muRelRange[0], muRelRange[1], numLayers)
    h = sp.random.uniform(hRange[0], hRange[1], numLayers)
    
    layersDict = {'height':h, 'epsilonRelative':epsRel, 'muRelative':muRel}
    return layersDict
#---------------------------------------------------------------------------------------------------
def randomLayers(epsRelRange, muRelRange, hRange, numLayers):
    layersDictRe = randomIdealLayers(epsRelRange.real, muRelRange.real, hRange, numLayers)
    layersDictIm = randomIdealLayers(epsRelRange.imag, muRelRange.imag, hRange, numLayers)

    epsRel = layersDictRe['epsilonRelative'] + 1.0J*layersDictIm['epsilonRelative']
    muRel = layersDictRe['muRelative'] + 1.0J*layersDictIm['muRelative']
    h = layersDictRe['height']
    
    layersDict = {'height':h, 'epsilonRelative':epsRel, 'muRelative':muRel}
    return layersDict
#--------------------------------------------------------------------------------------------------- 
def shuffleLayers(layersDict1, layersDict2):
    epsRel = sp.concatenate((layersDict1['epsilonRelative'], layersDict2['epsilonRelative']))
    muRel = sp.concatenate((layersDict1['muRelative'], layersDict2['muRelative']))
    h = sp.concatenate((layersDict1['height'], layersDict2['height']))

    # Shuffle the layers
    ix = range(epsRel.size)
    sp.random.shuffle(ix)
    epsRel = epsRel[ix]
    muRel = muRel[ix]
    h = h[ix]

    layersDict = {'height':h, 'epsilonRelative':epsRel, 'muRelative':muRel}
    return layersDict
#---------------------------------------------------------------------------------------------------
def assertApproxEqual(a, b):
    a = sp.asarray(a)
    b = sp.asarray(b)

    # D. E. Knuth, The Art of Computer Programming, Addison-Wesley, 2nd edition, 1981
    # page. 219, eqn. (34), says
    # $|u - v| \leq \epsilon |u|$ and $|u - v| \leq \epsilon |v|$ implies $ u \approx v $
    # Single precision, http://en.wikipedia.org/wiki/IEEE_754-2008
    rtol = 1.0*10**-7
    atol = 1.0*10**-38
    abSame = sp.allclose(a, b, rtol, atol) and sp.allclose(b, a, rtol, atol)
    return abSame
#---------------------------------------------------------------------------------------------------
