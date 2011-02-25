# -*- coding: utf-8 -*-
import core
import numpy as np
import tool


class TrainGD(core.TrainInt):
    """
    Gradient descent backpropagation

    """
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
        adapt: bool (detault false)
            type of learning
    :Support networks:
        newff (multy-layers perceptron)

    """
    
    def __init__(self, **kwargs):
        super(TrainGD, self).__init__(**kwargs)
        self.defaults['adapt'] = False

    def _step(self, net, input, target):
        
        if self.param['adapt']:
            for inp, tar in zip(input, target):
                grad = tool.ff_grad_step(net, inp, tar, self.param['errorf'].deriv)
                self._learn(net, grad)
        else:
            grad = tool.ff_grad(net, input, target, self.param['errorf'].deriv)
            self._learn(net, grad)  
        return None
    
    def _learn(self, net, grad):
        #print grad
        for ln, layer in enumerate(net.layers):
            layer.np['w'] -= self.param['lr'] * grad[ln]['w']
            layer.np['b'] -= self.param['lr'] * grad[ln]['b']
        return None

class TrainGDM(TrainGD):
    """
    Gradient descent with momentum backpropagation
    """
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
        adapt: bool (detault false)
            type of learning
    :Support networks:
        newff (multy-layers perceptron)
    """
    def _step(self, net, input, target):
        if len(self.error) < 2 or self.error[-2] / self.error[-1] < 1.04:
            TrainGD._step(self, net, input, target)
        else:
            self._learn(net, self.grad_prev)
        return None
    
    def _learn(self, net, grad):
        self.grad_prev = grad
        TrainGD._learn(self, net, grad)
        return None
        

class TrainRprop(TrainGD):
    """Resilient Backpropagation"""
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
        adapt: bool (detault false)
            type of learning
        rate_dec: float (default 0.5)
            Decrement to weight change
        rate_inc: float (defaunt 1.2)
            Increment to weight change
        rate_min: float (defaunt 1e-9)
            Minimum performance gradient
        rate_max: float (defaunt 50)
            Maximum weight change
    :Support networks:
        newff (multy-layers perceptron)
    """
    def __init__(self, **kwargs):
        super(TrainRprop, self).__init__(**kwargs)
        self.defaults['rate_dec'] = 0.5
        self.defaults['rate_inc'] = 1.2
        self.defaults['rate_min'] = 1e-9
        self.defaults['rate_max'] = 50
        # init rate
        self.defaults['lr'] = 0.07

    def _init(self, net, input, target):
        self.grad_prev = [np.zeros([l.cn, l.ci+1]) for l in net.layers]
        self.rate = [np.zeros([l.cn, l.ci+1]) + self.param['lr'] for l in net.layers]
        
    def _learn(self, net, grad):
    
        for ln, layer in enumerate(net.layers):
            grad[ln]['b'].shape = grad[ln]['b'].size, 1
            gr = np.concatenate((grad[ln]['w'], grad[ln]['b']), axis=1)
            
            prod = gr * self.grad_prev[ln]
            # Знак изменен
            ind = prod > 0 
            self.rate[ln][ind] *= self.param['rate_inc']
            # Знак не менялся
            ind = prod < 0 
            self.rate[ln][ind] *= self.param['rate_dec']

            self.rate[ln][self.rate[ln] > self.param['rate_max']] = self.param['rate_max']
            self.rate[ln][self.rate[ln] < self.param['rate_min']] = self.param['rate_min']

            delta = - self.rate[ln] * np.sign(gr)

            layer.np['w'] += delta[:, 0:-1]
            layer.np['b'] += delta[:, -1]
            
            self.grad_prev[ln] = gr
        return None


class TrainRpropM(TrainRprop):
    """Resilient Backpropagation Modified"""
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
        adapt: bool (detault false)
            type of learning
        rate_dec: float (default 0.5)
            Decrement to weight change
        rate_inc: float (defaunt 1.2)
            Increment to weight change
        rate_min: float (defaunt 1e-9)
            Minimum performance gradient
        rate_max: float (defaunt 50)
            Maximum weight change
    :Support networks:
        newff (multy-layers perceptron)
    
    """
    def _init(self, net, input, target):
        self.grad_prev = [np.zeros([l.cn, l.ci+1]) for l in net.layers]
        self.deltaWB = [np.zeros([l.cn, l.ci+1]) for l in net.layers]
        self.rate = [np.zeros([l.cn, l.ci+1]) + self.param['lr'] for l in net.layers]
        
    def _learn(self, net, grad):
    
        for ln, layer in enumerate(net.layers):
            grad[ln]['b'].shape = grad[ln]['b'].size, 1
            gr = np.concatenate((grad[ln]['w'], grad[ln]['b']), axis=1)
            
            sign = gr * self.grad_prev[ln]
            # Знак изменен
            ind = sign > 0 
            self.rate[ln][ind] *= self.param['rate_inc']
            # Знак не менялся
            ind = sign < 0 
            self.rate[ln][ind] *= self.param['rate_dec']

            self.rate[ln][self.rate[ln] > self.param['rate_max']] = self.param['rate_max']
            self.rate[ln][self.rate[ln] < self.param['rate_min']] = self.param['rate_min']
            # Если знак менялся, то анлогичный шаг в обратном направлении
            self.deltaWB[ln][ind] *= -1
            gr[ind] = [0.0]

            ind = sign >= 0
            sign_gr = (gr[ind] >= 0) * 2.0 - 1.0
            self.deltaWB[ln][ind] = - self.rate[ln][ind] * sign_gr

            layer.np['w'] += self.deltaWB[ln][:, 0:-1]
            layer.np['b'] += self.deltaWB[ln][:, -1]
            
            self.grad_prev[ln] = gr
        return None

        
#--------------------------------------------------------------------------
        
        
class TrainBFGS(core.TrainExt):
    """Broyden–Fletcher–Goldfarb–Shanno (BFGS) method"""
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
    :Support networks:
        newff (multy-layers perceptron)
    
    """
    def _optimize(self, net, input, target, fcn, x0, step):
        size = x0.size
        
        def grad(*args):
            gr = tool.ff_grad(net, input, target, self.param['errorf'].deriv)
            out = np.empty(size)
            st = 0
            for l in gr:
                for v in l.values():
                    out[st: st + v.size] = v.flat[:]
                    st = st + v.size
            return out
    
        from scipy.optimize import fmin_bfgs
        if 'disp' not in self.kwargs:
            self.kwargs['disp'] = 0
        fmin_bfgs(fcn, x0, fprime=grad, maxiter=self.param['epochs'], callback=step, **self.kwargs)
        return None


class TrainCG(core.TrainExt):
    """Conjugate gradient algorithm"""
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
    :Support networks:
        newff (multy-layers perceptron)
    
    """
    def _optimize(self, net, input, target, fcn, x0, step):
        size = x0.size
        
        def grad(*args):
            gr = tool.ff_grad(net, input, target, self.param['errorf'].deriv)
            out = np.empty(size)
            st = 0
            for l in gr:
                for v in l.values():
                    out[st: st + v.size] = v.flat[:]
                    st = st + v.size
            return out
    
        from scipy.optimize import fmin_cg 
        if 'disp' not in self.kwargs:
            self.kwargs['disp'] = 0
        fmin_cg(fcn, x0, fprime=grad, maxiter=self.param['epochs'], callback=step, **self.kwargs)
        return None


#-----------------------------------------------------------------------


class TrainWTA(core.TrainInt):
    """ Winner Take All algoritm """
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
    :Support networks:
        newc
    """
       
    def _init(self, net, input):
        self.winner_output = np.zeros_like(input)
    
    def _error(self, net, input):
        return self.param['errorf'](self.winner_output - input)
    
    def _step(self, net, input):
        layer = net.layers[0]
        # Init network!
        for w in layer.np['w']:
            w[:] = input[np.random.randint(0, len(input))]

        for inp in input:
            out = net.step(inp)
            winner = np.argmax(out)
            e = layer.last_dist
            layer.np['w'][winner] += self.param['lr'] * e[winner] * (inp - layer.np['w'][winner])

        for i,inp in enumerate(input):
            net.step(inp)
            winner = np.argmax(out)
            self.winner_output[i,:] = layer.np['w'][winner]
        return None


class TrainCWTA(TrainWTA):
    """ Conscience Winner Take All algoritm"""
    __doc__ =  __doc__ + core.Train.__call__.__doc__ + """
    :Support networks:
        newc
    
    """
    def _init(self, net, input):
        self.winner_output = np.zeros_like(input)

    def _step(self, net, input):
        layer = net.layers[0]

        for inp in input:
            out = net.step(inp)
            winner = np.argmax(out)
            e = layer.last_dist
            layer.np['conscience'][winner] += 1
            layer.np['w'][winner] += self.param['lr'] * e[winner] * (inp - layer.np['w'][winner])

        layer.np['conscience'] = np.ones_like(layer.np['conscience'])

        for i,inp in enumerate(input):
            net.step(inp)
            winner = np.argmax(out)
            self.winner_output[i,:] = layer.np['w'][winner]
        return None


#--------------------------------------------------------------------------------------
        

class TrainDelta(core.TrainInt):
    """ Train with Delta rule """
    __doc__ =  __doc__ + core.Train.__call__.__doc__ +"""
    :Support networks:
        newp (one-layers perceptron)
    
    """
    def _step(self, net, input, target):
        layer = net.layers[0]
        for inp, tar in zip(input, target):
            out = net.step(inp)
            err = tar - out
            err.shape =  err.size, 1
            inp.shape = 1, inp.size
            #print layer.np['w'], err * inp,self.lr
            layer.np['w'] += self.param['lr'] * err * inp
            #print layer.np['b'].shape, err.shape
            err.shape =  err.size
            layer.np['b'] += self.param['lr'] * err
            #print layer.np['w']

        return None
