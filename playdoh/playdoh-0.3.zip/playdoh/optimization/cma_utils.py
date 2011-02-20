
# Copyright 2008, Nikolaus Hansen.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License, version 2,
#    as published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



import sys         # from sys import stdout
import string      # from string import join, split
import numpy as nu # arange, cos, size, eye, inf, dot, floor, outer, zeros, linalg.eig, sort, argsort, random, ones,... 
from numpy import array, log, sqrt, sum



# __all__ = ['fmin', 'CMAEvolutionStrategy', 'plotdata', ...] # TODO

class _Struct(dict):
# class Bunch(dict):   # struct and dictionary
    def __init__(self,**kw) :
        dict.__init__(self,kw)
        self.__dict__ = self    # this self reference relies on cycle detecting gc

#   
class _GenoPheno(object):
    """Genotype-phenotype transformation for convenient scaling.
    """
    def pheno(self, x):
        y = array(x)
        if self.scales != 1:  # just for efficiency
            y = self.scales * y
            # print 'transformed to phenotyp'
        if self.typical_x != 0:
            y = y + self.typical_x
        return y
    def geno(self, y):
        x = array(y)
        if self.typical_x != 0:
            x = x - self.typical_x
        if self.scales != 1:  # just for efficiency
            x = x / self.scales  # for each element in y
        return x

    def __init__(self, scaling=None, typical_x=None):
        if nu.size(scaling) > 1 or scaling:  # 
            self.scales = scaling  # CAVE: is not a copy
        else:
            self.scales = 1

        if nu.size(typical_x) > 1 or typical_x:
            self.typical_x = typical_x
        else:
            self.typical_x = 0


# 
def defaultOptions(tolfun = 1e-12  # prefered termination criterion
         , tolfunhist = 0 
         , tolx = 1e-11
         , tolfacupx = 1e3 # terminate on divergent behavior
         , ftarget = -nu.inf  # target function value
         , maxiter = 'long(1e3*N**2/sqrt(popsize))'
         , maxfevals = nu.inf
         , evalparallel = False  # not too useful so far
         , termination_callback = None  # a function returning True for termination
         , verb_disp = 100
         , verb_log = 1
         , verb_filenameprefix = 'outcmaes'
         , verb_append = 0 
         , popsize = '4+int(3*log(N))'
         , restarts = 0
         , incpopsize = 2
         , updatecovwait = None  # TODO: rename: updatedistribution?
         , seed = None 
         , CMAon = True
         , CMAdiagonal = '0*100*N/sqrt(popsize)' # TODO 4/ccov_separable? 
         , CMAmu = None    # default is lambda/2
         , CMArankmu = True 
         , CMArankmualpha = 0.3
         , CMAteststds = None   # for test purpose, non-isotropic initial distr.
         , CMAeigenmethod = 0   # 0=numpy, -1=pygsl, other=internal (slow)
         , noise_reevalfrac = 0.0  # 0.05, not yet working
         , noise_eps = 1e-7
         , scaling_of_variables = None
         , typical_x = None): 

    opts = locals()
    return opts # assembles the keyword-arguments in a dictionary    


def _evalOption(o, default, loc=None):
    """Evaluates input o as option in environment loc
    """
    if o == str(o):
        val = eval(o, globals(), loc)
    else:
        val = o
    if val in (None, (), [], ''):  # TODO: {} in the list gives an error
        val = eval(str(default), globals(), loc)
    return val
    
#____________________________________________________________
#____________________________________________________________
# 
class CMAEvolutionStrategy(object):
    """CMA-ES stochastic optimizer class with ask-and-tell interface
                
    """

    def __init__(self, x0, sigma0, inopts = {}):
        """
        :Parameters:
            x0 -- initial solution, starting point
            sigma0 -- initial standard deviation.  The problem
                variables should have been scaled, such that a single
                standard deviation on all variables is useful and the
                optimum is expected to lie within x0 +- 3*sigma0.
            inopts -- options, a dictionary according to the parameter list
              of function fmin(), see there and defaultOptions()
        """

        #____________________________________________________________
        self.inargs = locals().copy()
        del self.inargs['self'] # otherwise the instance self has a cyclic reference
        self.inopts = inopts
        defopts  = defaultOptions()
        opts = defopts.copy()
        if inopts: # filling of opts with inopts while checking for unknow keys in inopts
            if not isinstance(inopts, dict): 
                raise Exception('options argument must be a dict')
            for key in inopts.keys():
                if not defopts.has_key(key):
                    raise Exception(key + ' is invalid key entry for options argument, see defaultOptions()')
                opts[key] = inopts[key]

        if x0 == str(x0) :
            self.mean = array(eval(x0))
        else :
            self.mean = array(x0, copy=True) # does not have column or row, is just 1-D
        self.x0 = self.mean.copy()

        if self.mean.ndim != 1:
            raise Error('x0 must be 1-D array')
        
        self.N = self.mean.shape[0]
        N = self.N
        self.mean.resize(N) # 1-D array
        self.sigma = sigma0
        
        popsize = _evalOption(opts['popsize'], defopts['popsize'], locals())

        # extract/expand options 
        for key in opts.keys():
            if key.find('filename') < 0:
                opts[key] = _evalOption(opts[key], defopts[key], locals())
            elif not opts[key]:
                opts[key] = defopts[key]
        
        self.opts = opts

        self.gp = _GenoPheno(opts['scaling_of_variables'], opts['typical_x'])  # qqq
        self.mean = self.gp.geno(self.mean)
        self.fmean = 0.             # TODO name should change? 
        self.fmean_noise_free = 0.  # for output only
        
        self.sp = self._computeParameters(N, popsize, opts)
        self.sp0 = self.sp

        # initialization of state variables
        self.countiter = 0
        self.countevals = 0
        self.ps = nu.zeros(N)
        self.pc = nu.zeros(N)

        stds = nu.ones(N)
        if self.opts['CMAteststds'] not in (None, (), []):
            stds = self.opts['CMAteststds']
            if nu.size(stds) != N:
                raise Error('CMAteststds option must have dimension = ' + str(N)) 
        if self.opts['CMAdiagonal'] > 0 :  # linear time and space complexity ((True>0)==True)
            self.B = array(1) # works fine with nu.dot(self.B, anything) and self.B.T
            self.C = stds**2
        else :
            self.B = nu.eye(N) # identity(N), do not from matlib import *, as eye is a matrix there
            # prevent equal eigenvals, a hack for nu.linalg TODO:
            # self.C = nu.diag(1 + 0.01*nu.random.rand(N)) 
            self.C = nu.diag(stds**2)
        self.D = stds
        self.dC = nu.diag(self.C)

        self.flgtelldone = True
        self.itereigenupdated = self.countiter
        self.noiseS = 0  # noise "signal"
        self.hsiglist = [] 
        self.opts_in = inopts

        if opts['seed'] is None:
            nu.random.seed()
            opts['seed'] = 1e9 * nu.random.rand()
        opts['seed'] = int(opts['seed'])
        nu.random.seed(opts['seed'])
        
        out = {}
        # out.best = _Struct()
        out['best_f'] = nu.inf
        out['best_x'] = []
        out['best_evals'] = 0
        out['hsigcount'] = 0
        self.out = out
        
        self.const = _Struct()
        self.const.chiN = N**0.5*(1-1./(4.*N)+1./(21.*N**2)) # expectation of 
                      #   ||N(0,I)|| == norm(randn(N,1))
                                      # normalize recombination weights array

        # attribute for stopping criteria in function stop 
        self.stoplastiter = 0 
        self.manualstop = 0 
        self.fit = _Struct() 
        self.fit.fit = []   # not really necessary 
        self.fit.hist = [] 

#        if self.opts['verb_log'] > 0 and not self.opts['verb_append']:
#            self.writeHeaders()
#            self.writeOutput()
        if self.opts['verb_append'] > 0:
            self.countevals = self.opts['verb_append']

        # say hello
        if opts['verb_disp'] > 0:
            if self.sp.mu == 1:
                print '(%d,%d)-CMA-ES' % (self.sp.mu, self.sp.popsize),
            else:
                print '(%d_w,%d)-CMA-ES' % (self.sp.mu, self.sp.popsize), 
            print '(mu_w=%2.1f,w_1=%d%%)' % (self.sp.mueff, int(100*self.sp.weights[0])),
            print 'in dimension %d ' % N # + func.__name__ 
            if opts['CMAdiagonal'] and self.sp.CMAon:
                s = ''
                if opts['CMAdiagonal'] is not True:
                    s = ' for '
                    if opts['CMAdiagonal'] < nu.inf:
                        s += str(int(opts['CMAdiagonal']))
                    else:
                        s += str(nu.floor(opts['CMAdiagonal']))
                    s += ' iterations'
                    s += ' (1/ccov=' + str(round(1./(self.sp.c1+self.sp.cmu))) + ')'
                print '   Covariance matrix is diagonal' + s 

    #____________________________________________________________
    #____________________________________________________________

    def _getmean(self):
        """mean value of the sample distribution, this is not a copy.
        """
        return self.mean  

    def _setmean(self, m):
        """mean value setter, does not copy 
        """
        self.mean = m  
 

    #____________________________________________________________
    #____________________________________________________________
    def ask(self, number=None, xmean=None, sigma=1) :
        """Get new candidate solutions, sampled from a multi-variate
           normal distribution. 
        :Parameters:
            number -- number of returned solutions, by default the
                population size popsize (AKA lambda).
            xmean -- sequence of distribution means, if
               number > len(xmean) the last entry is used for the
               remaining samples. 
            sigma -- multiplier for internal sample width (standard
               deviation)
        :Returns:
            sequence of N-dimensional candidate solutions to be evaluated
        :Example:
            X = es.ask()  # get list of new solutions
            fit = []
            for x in X:
                fit.append(cma.fcts.rosen(x))  # call func rosen
            es.tell(X, fit)  
        """
        #________________________________________________________
        #
        def gauss(N):
            r = nu.random.randn(N)
            # r = r * sqrt(N / sum(r**2))
            return r

        #________________________________________________________
        #
        if number is None or number < 1:
            number = self.sp.popsize
        if xmean is None:
            xmean = self.mean
        sigma = sigma * self.sigma

        flgseparable = self.opts['CMAdiagonal'] is True \
                       or self.countiter <= self.opts['CMAdiagonal'] 


#        self._updateBD()

##        sample distribution
        self.pop = []
        if self.flgtelldone:  # could be done in tell()!? 
            self.flgtelldone = False
            self.ary = [] 
            
        for k in xrange(number):
            # use mirrors for mu=1 
            if self.sp.mu == 1 and nu.mod(len(self.ary),2) == 1:  # even individual
                 self.ary.append(-self.ary[-1])
            # regular sampling
            elif 1 < 2 or self.N > 40:
                self.ary.append(nu.dot(self.B, self.D*gauss(self.N)))
            # sobol numbers, quasi-random, derandomized, not in use
            else: 
                if self.countiter == 0 and k == 0:
                    print 'sobol numbers applied'
                # sobol sequence: does strongly bias sigma if mu > 1
                self.ary.append(nu.dot(self.B, self.D*sobolrandn(self.N))) 

            self.pop.append(self.gp.pheno(xmean + sigma * self.ary[-1]))

        # if k > 1:  # TODO: what was this for? Sample at most 1 (in fact 2)?
        #     1/0
        
        return self.pop  # this is just a reference and not so terribly useful to keep 

    #____________________________________________________________
    #____________________________________________________________
    # 
    def _updateBD(self): 
        # itereigenupdated is always up-to-date in the diagonal case 
        # just double check here
        if self.itereigenupdated == self.countiter:
            return

        self.C = 0.5 * (self.C + self.C.T)
        # self.C = nu.triu(self.C) + nu.triu(self.C,1).T  # should work as well
        # self.D, self.B = eigh(self.C) # hermitian, ie symmetric C is assumed
        if self.opts['CMAeigenmethod'] == -1:  
                   # pygsl
                   # easy to install (well, in Windows install gsl binaries first, 
                   # set system path to respective libgsl-0.dll (or cp the dll to
                   # python\DLLS ?), in unzipped pygsl edit
                   # gsl_dist/gsl_site_example.py into gsl_dist/gsl_site.py
                   # and run "python setup.py build" and "python setup.py install"
                   # in MINGW32)
            if 1 < 3:  # import pygsl on the fly
                try:
                    from pygsl.eigen import eigenvectors  # TODO efficient enough?
                except ImportError:
                    print 'WARNING: could not find pygsl.eigen module, either install pygsl \n' + \
                          '  or set option CMAeigenmethod=1 (is much slower), option set to 1'
                    self.opts['CMAeigenmethod'] = 0  # use 0 if 1 is too slow
                    
                if self.opts['CMAeigenmethod'] == -1:
                    self.D, self.B = eigenvectors(self.C)

            else:  # assumes pygsl.eigen was imported above 
                self.D, self.B = pygsl.eigen.eigenvectors(self.C)

            idx = nu.argsort(self.D)
            self.D = self.D[idx]
            self.B = self.B[:,idx] # self.B[i] is the i+1-th row and not an eigenvector
            
        elif self.opts['CMAeigenmethod'] == 0: 
            # TODO: thoroughly test nu.linalg.eigh 
            #       numpy.linalg.eig crashes in 200-D
            #       and EVecs with same EVals are not orthogonal 
            self.D, self.B = nu.linalg.eigh(self.C)  # self.B[i] is a row and not an eigenvector
            idx = nu.argsort(self.D)
            self.D = self.D[idx]
            self.B = self.B[:,idx]
        else:  # is overall two;ten times slower in 10;20-D
            self.D, self.B = eig(self.C)  # def eig, see below
            idx = nu.argsort(self.D)
            self.D = self.D[idx]
            self.B = self.B[:,idx]
            # assert(sum(self.D-DD) < 1e-6)
            # assert(sum(sum(nu.dot(BB, BB.T)-nu.eye(self.N))) < 1e-6)
            # assert(sum(sum(nu.dot(BB * DD, BB.T) - self.C)) < 1e-6)
        
        # assert(all(self.B[self.countiter % self.N] == self.B[self.countiter % self.N,:]))
            
        if 11 < 3 and any(abs(sum(self.B[:,0:self.N-1] * self.B[:,1:], 0)) > 1e-6): 
            print 'B is not orthogonal'
            #print self.D
            print sum(self.B[:,0:self.N-1] * self.B[:,1:], 0) 
        else:
            # TODO remove as it is O(N^3)
            # assert(sum(abs(self.C - nu.dot(self.D * self.B,  self.B.T))) < N**2*1e-11) 
            pass
        self.D **= 0.5
        self.itereigenupdated = self.countiter

    # 

    def readProperties(self):
        """reads dynamic parameters from property file
        """
        print 'not yet implemented'

    #____________________________________________________________
    #____________________________________________________________
    def _computeParameters(self, N, popsize, opts, ccovfac=1, verbose=True):
        """Compute strategy parameters mainly depending on
        population size """
        #____________________________________________________________
        # learning rates cone and cmu as a function
        # of the degrees of freedom df
        def cone(df, mu, N):
            return 1. / (df + 2.*sqrt(df) + float(mu)/N)

        def cmu(df, mu, alphamu):
            return (alphamu + mu - 2. + 1./mu) / (df + 4.*sqrt(df) + mu/2.)

        #____________________________________________________________
        sp = _Struct()  # just a hack 
        sp.popsize = int(popsize)
        sp.mu_f = sp.popsize / 2.0  # float value of mu
        

        if opts['CMAmu'] != None: 
            sp.mu_f = opts['CMAmu']

        sp.mu = int(sp.mu_f + 0.49999) # round down for x.5
        sp.weights = log(sp.mu_f+0.5) - log(1.+nu.arange(sp.mu))
        sp.weights /= sum(sp.weights)
        sp.mueff = 1./sum(sp.weights**2)
        sp.cs = (sp.mueff+2)/(N+sp.mueff+3)
        sp.cc = 4. / (N+4.)
        sp.cc_sep = sp.cc  # 1. / sqrt(N)  # TODO: should this stay? # 2. / (sqrt(N)+1.) 
        sp.rankmualpha = _evalOption(opts['CMArankmualpha'], 0.3)
        sp.c1 = ccovfac*min(1,sp.popsize/6)*cone((N**2+N)/2, sp.mueff, N) # 2. / ((N+1.3)**2 + sp.mucov)
        sp.c1_sep = ccovfac*cone(N, sp.mueff, N) # 2. / ((N+1.3)**2 + sp.mucov)
        if -1 > 0:
            sp.c1 = 0.
            print 'c1 is zero'
        if opts['CMArankmu'] != 0:  # also empty
            sp.cmu = min(1-sp.c1, ccovfac*cmu((N**2+N)/2, sp.mueff, sp.rankmualpha))
            sp.cmu_sep = min(1-sp.c1_sep, ccovfac*cmu(N, sp.mueff, sp.rankmualpha))
        else:
            sp.cmu = sp.cmu_sep = 0

        sp.CMAon = sp.c1 + sp.cmu > 0  
        # print sp.c1_sep / sp.cc_sep

        if not opts['CMAon'] and opts['CMAon'] not in (None,[],()): 
            sp.CMAon = False
            # sp.c1 = sp.cmu = sp.c1_sep = sp.cmu_sep = 0
        sp.damps = (1 + 2*max(0,sqrt((sp.mueff-1)/(N+1))-1)) + sp.cs 
        if 11 < 3:
            sp.damps = 30 * sp.damps  # 1e99 # (1 + 2*max(0,sqrt((sp.mueff-1)/(N+1))-1)) + sp.cs; 
            # sp.damps = 20 # 1. + 20 * sp.cs**-1  # 1e99 # (1 + 2*max(0,sqrt((sp.mueff-1)/(N+1))-1)) + sp.cs; 
            print 'damps is', sp.damps

        sp.kappa = 1  # 4-D, lam=16, rank1, kappa < 4 does not influence convergence rate
                      # in larger dim it does, 15-D with defaults, kappa=8 factor 2 
        if sp.kappa != 1:
            print '  kappa =', sp.kappa
        
        if verbose:
            if not sp.CMAon:
                print 'covariance matrix adaptation turned off'
            if opts['CMAmu'] != None: 
                pass
                #print 'mu =', sp.mu_f

        return sp  # the only existing reference to sp is passed here

    #____________________________________________________________
    #____________________________________________________________
    #____________________________________________________________
    #____________________________________________________________

    def tell(self, points, function_values, function_values_reevaluated=None):  
        """Pass objective function values to CMA-ES to prepare for next
        iteration

        :Arguments:
           points -- list or array of candidate solution points,
              most presumably before delivered by method ask().
           function_values -- list or array of objective function values 
              associated to the respective points. Beside termination 
              decisions, only the ranking of values in function_values
              is used.
        :Details: tell() updates the parameters of the multivariate
            normal search distribtion, namely covariance matrix and
            step-size and updates also the number of function evaluations
            countevals. 
        """
    #____________________________________________________________

        lam = len(points)
        pop = self.gp.geno(points)
#        print pop.shape
        if lam != array(function_values).shape[0] :
            raise Error('for each candidate solution '
                        + 'a function value must be provided')
        if lam < 3: 
            raise Exception('population is too small')
        N = self.N
        if lam != self.sp.popsize:  
            #print 'WARNING: population size has changed'
            # TODO: when the population size changes, sigma
            #    should have been updated before
            self.sp = self._computeParameters(N, lam, self.opts) 
        sp = self.sp

        self.countiter += 1  # >= 1 now
        self.countevals += sp.popsize
        flgseparable = self.opts['CMAdiagonal'] is True \
                       or self.countiter <= self.opts['CMAdiagonal'] 
        if not flgseparable and len(self.C.shape) == 1:  # C was diagonal ie 1-D
            self.B = nu.eye(N) # identity(N)
            self.C = nu.diag(self.C)
            idx = nu.argsort(self.D)
            self.D = self.D[idx]
            self.B = self.B[:,idx]

        fit = self.fit  # make short cut
        fit.idx = nu.argsort(function_values)
        fit.fit = array(function_values)[fit.idx]
        
        fit.hist.insert(0, fit.fit[0])
        if len(fit.hist) > 10 + 30*N/sp.popsize:
            fit.hist.pop()

        # compute new mean and sort pop
        mold = self.mean
        pop = array(pop)[fit.idx] # only arrays can be multiple indexed
        self.mean = mold + self.sp.kappa**-1 * \
                    (sum(sp.weights * array(pop[0:sp.mu]).T, 1) - mold)

        # evolution paths
        self.ps = (1-sp.cs) * self.ps + \
                  (sqrt(sp.cs*(2-sp.cs)*sp.mueff)  / self.sigma) \
                  * nu.dot(self.B, (1./self.D) * nu.dot(self.B.T,
                                                      self.sp.kappa*(self.mean - mold)))

        # "hsig"
        hsig = (sqrt(sum(self.ps**2)) / sqrt(1-(1-sp.cs)**(2*self.countiter)) 
                / self.const.chiN) < 1.4 + 2./(N+1)

        if 11 < 3:  # diagnostic data
            self.out['hsigcount'] += 1 - hsig
            if not hsig:
                self.hsiglist.append(self.countiter)
        if 11 < 3:  # diagnostic message
            if not hsig:  
                print self.countiter, ': hsig-stall'
        if 11 < 3:  # for testing purpose
            hsig = 1 # TODO: in 4-D and damps=1e99 hsig leads to premature convergence of C, put correction term
            if self.countiter == 1:
                print 'hsig=1'
        
        
        cc = sp.cc
        if flgseparable:
            cc = sp.cc_sep
        
        self.pc = (1-cc) * self.pc + \
                  hsig * sqrt(cc*(2-cc)*sp.mueff) \
                  * self.sp.kappa * (self.mean - mold) / self.sigma

        # covariance matrix adaptation
        
#        print self.sigma_iter
        #sp.CMAon=False

        if self.iteration > 60:
            if self.sigma_iter[self.iteration][0]-self.sigma_iter[self.iteration-60][0]<10e-12:
                sp.CMAon=False  
                
        if sp.CMAon:
            assert sp.c1 + sp.cmu < sp.mueff / N
            # default full matrix case 
            if not flgseparable:
                Z = (pop[0:sp.mu] - mold) / self.sigma
                if 11 < 3:
                    # TODO: here optional the Suttorp update
                    
                    # CAVE: how to integrate the weights
                    self.itereigenupdated = self.countiter
                else:
                    Z = nu.dot((sp.cmu * sp.weights) * Z.T, Z)  # learning rate integrated
                    if 11 > 3: # 3 to 5 times slower
                        Z = nu.zeros((N,N))
                        for k in xrange(sp.mu): 
                            z = (pop[k]-mold) 
                            Z += nu.outer((sp.cmu * sp.weights[k] / self.sigma**2) * z, z)
                    self.C = (1 - sp.c1 - sp.cmu) * self.C + \
                             nu.outer(sp.c1 * self.pc, self.pc) + Z
                    self.dC = nu.diag(self.C)  # for output and termination checking 

            else : # separable/diagonal linear case 
                c1, cmu = sp.c1_sep, sp.cmu_sep 
                assert(c1+cmu <= 1)
                Z = nu.zeros(N)
                for k in xrange(sp.mu):
                    z = (pop[k]-mold) / self.sigma  # TODO see above
                    Z += sp.weights[k] * z * z  # is 1-D
                self.C = (1-c1-cmu) * self.C + c1 * self.pc * self.pc + cmu * Z
                
                self.dC = self.C
                self.D = sqrt(self.C)  # C is a 1-D array
                self.itereigenupdated = self.countiter
                
        # step-size adaptation, adapt sigma
        self.sigma *= nu.exp(min(1, (sp.cs/sp.damps) *
                                (sqrt(sum(self.ps**2))/self.const.chiN - 1)))


            
        self.flgtelldone = True
        
        self._updateBD()

