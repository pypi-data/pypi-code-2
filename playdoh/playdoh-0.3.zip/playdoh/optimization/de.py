from ..synchandler import *
from ..debugtools import *
#from optimization import *
from algorithm import *
from numpy import zeros, ones, array, inf, tile, nonzero, isscalar, maximum, minimum
from numpy.random import rand

__all__ = ['PSO']

class PSO(OptimizationAlgorithm):
    @staticmethod
    def default_optparams():
        """
        Returns the default values for optparams
        """
        optparams = dict(omega = .8,
                         cl = .1,
                         cg = .1)
        return optparams
    
    @staticmethod
    def get_topology(node_count):
        topology = []
        # 0 is the master, 1..n are the workers
        if node_count>1:
            for i in xrange(1, node_count):
                topology.extend([('to_master_%d' % i, i, 0),
                                 ('to_worker_%d' % i, 0, i)])
        return topology
    
    def initialize(self):
        """
        Initializes the optimization algorithm. X is the matrix of initial particle positions.
        X.shape == (ndimensions, nparticles)
        """
        self.omega = self.optparams['omega']
        self.cl = self.optparams['cl']
        self.cg = self.optparams['cg']
        
        self.V = zeros((self.ndimensions, self.nparticles))
        
        if self.scaling == None:        
            self.Xmin = tile(self.boundaries[:, 0].reshape(self.ndimensions,1), (1, self.nparticles))
            self.Xmax = tile(self.boundaries[:, 1].reshape(self.ndimensions,1), (1, self.nparticles))
        else:
            self.Xmin = tile(self.parameters.scaling_func(self.boundaries[:, 0]).reshape(self.ndimensions,1), (1, self.nparticles))
            self.Xmax = tile(self.parameters.scaling_func(self.boundaries[:, 1]).reshape(self.ndimensions,1), (1, self.nparticles))

        # Preparation of the optimization algorithm
        self.fitness_lbest = inf*ones(self.nparticles)
        self.fitness_gbest = inf
        self.X_lbest = zeros((self.ndimensions, self.nparticles))
        self.X_gbest = zeros(self.ndimensions)
        self.best_fitness = zeros(self.niterations)
        self.best_particule = zeros((self.ndimensions,self.niterations))
    
    def get_global_best(self):
        """
        Returns the global best pos/fit on the current machine 
        """
        min_fitness = self.fitness.min()
        if min_fitness < self.fitness_gbest:
            index_gbest = nonzero(self.fitness == min_fitness)[0]
            if not(isscalar(index_gbest)): # if several best: take the first 
                index_gbest = index_gbest[0]
            self.X_gbest = self.X[:,index_gbest]
            self.fitness_gbest = min_fitness
        return self.fitness_gbest

    def get_local_best(self):
        indices_lbest = nonzero(self.fitness < self.fitness_lbest)[0]
        if (len(indices_lbest)>0):
            self.X_lbest[:,indices_lbest] = self.X[:,indices_lbest]
            self.fitness_lbest[indices_lbest] = self.fitness[indices_lbest]
    
    def communicate(self):
        # communicate with master to have the absolute global best
        if self.index > 0:
            # WORKERS
            log_info("I'm worker #%d" % self.index)
            
            # sends the temp global best to the master
            to_master = 'to_master_%d' % self.index
            self.tubes.push(to_master, (self.X_gbest, self.fitness_gbest))
            
            # receives the absolute global best from the master
            to_worker = 'to_worker_%d' % self.index
            (self.X_gbest, self.fitness_gbest) = self.tubes.pop(to_worker)
        else:
            # MASTER
            log_info("I'm the master (#%d)" % self.index)
            
            # best values for each node, including the master (current node)
            X_gbest = self.X_gbest
            fitness_gbest = self.fitness_gbest
            
            # receives the temp global best from the workers
            for node in self.nodes: # list of incoming tubes, ie from workers
                if node.index == 0:
                    continue
                tube = 'to_master_%d' % node.index
                log_info("Receiving best values from <%s>..." % tube)
                X_gbest_tmp, fitness_gbest_tmp = self.tubes.pop(tube)
                
                # this one is better
                if fitness_gbest_tmp < fitness_gbest:
#                    log_info("it's better! (%.6f < %.6f)" % (fitness_gbest_tmp, fitness_gbest))
                    X_gbest = X_gbest_tmp
                    fitness_gbest = fitness_gbest_tmp
#                else:
#                    log_info("it's not better... (%.6f >= %.6f)" % (fitness_gbest_tmp, fitness_gbest))
            
            # sends the absolute global best to the workers
            for node in self.nodes: # list of outcoming tubes, ie to workers
                if node.index == 0:
                    continue
                tube = 'to_worker_%d' % node.index
                self.tubes.push(tube, (X_gbest, fitness_gbest))
            
            self.X_gbest = X_gbest
            self.fitness_gbest = fitness_gbest
            
    
    def evolve(self):
        for ii in xrange(self.population_size):
            rnd = rand(self.population_size-1)
            permut = flex.sort_permutation(rnd)
            # make parent indices
            i1=permut[0]
            if (i1>=ii):
              i1+=1
            i2=permut[1]
            if (i2>=ii):
              i2+=1
            i3=permut[2]
            if (i3>=ii):
              i3+=1
            #
            x1 = self.population[ i1 ]
            x2 = self.population[ i2 ]
            x3 = self.population[ i3 ]
            vi = x1 + self.f*(x2-x3)
            # prepare the offspring vector please
            rnd = flex.random_double(self.vector_length)
            permut = flex.sort_permutation(rnd)
            test_vector = self.population[ii].deep_copy()
            # first the parameters that sure cross over
            for jj in xrange( self.vector_length  ):
              if (jj<self.n_cross):
                test_vector[ permut[jj] ] = vi[ permut[jj] ]
              else:
                if (rnd[jj]>self.cr):
                  test_vector[ permut[jj] ] = vi[ permut[jj] ]
            # get the score please
            test_score = self.evaluator.target( test_vector )
            # check if the score if lower
            if test_score < self.scores[ii] :
              self.scores[ii] = test_score
              self.population[ii] = test_vector
    
    def iterate(self, iteration, fitness):
        """
        Must return the new population
        """
#        log_debug("iteration %d/%d" % (iteration+1, self.iterations))
        self.iteration = iteration
        self.fitness = fitness
        
        # get local/global best on this machine
        self.get_local_best()
        self.get_global_best()
        
        # communicate with other nodes to have the absolute global best position
        self.communicate()
        
        # updates the particle positions
        self.evolve()
        self.get_info()
    
    def get_info(self):
#        print self.iteration
        self.best_fitness[self.iteration]= self.fitness_gbest 
        self.best_particule[:,self.iteration]=self.X_gbest
        
        return self.best_fitness,self.best_particule
    
    def get_result(self):
        """
        Returns (X_best, fitness_best)
        """
        return self.X_gbest, self.fitness_gbest