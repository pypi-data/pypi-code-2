# -*- coding: utf-8 -*-
"""
Base classes

"""
import numpy as np
import tool

class NeuroLabError(Exception):
    pass
    
class TrainStop(NeuroLabError):
    pass


class Net(object):
    """ 
    Neural Network class 
    
    :Parameters:
        inp_minmax: minmax: list ci x 2
            Range of input value
        co: int
            Number of output
        layers: list of Layer
            Network layers
        connect: list of list
            Connection scheme of layers*
        trainf: callable
            Train function
    
    :Connect format:
        Example 1: for two-layers feed forwad network
            >>> connect = [[-1], #- layer 0 reseives the input network signal;
            ...            [0],  #- layer 1 reseives the output signal from the layer 0;
            ...            [1]]  #- the network exit reseives the output signal from the layer 1.
        
        Example 2: for two-layers Elman network with derivatives:
            >>> connect = [[-1, 0], #- layer 0 reseives the input network signal and output signal from layer 0;
            ...            [0],     #- layer 1 reseives the output signal from the layer 0;
            ...            [1]]     #- the network exit reseives the output signal from the layer 1.
                
        """

    def __init__(self, inp_minmax, co, layers, connect, trainf):
        self.inp_minmax = np.asfarray(inp_minmax)
        self.ci = self.inp_minmax.shape[0]
        self.co = co
        self.layers = layers
        self.trainf = trainf
        self.inp = np.zeros(self.ci)
        self.out = np.zeros(self.co)
        # Check connect format
        if len(connect) != len(layers) + 1:
            raise ValueError(u"Connect error: неверный размер")
        tmp = [0] * (len(connect))
        for con in connect:
            for s in con:
                tmp[s]+=1
        for l,c in enumerate(tmp):
            if c == 0:
                raise ValueError(u"Connect error: Lost the signal from the layer " + (l-1))
        
        self.connect = connect

        # Set inp_minmax for all layers
        for nl, nums_signal in enumerate(self.connect):
            if nl == len(self.layers):
                self.out_minmax = np.zeros([self.co, 2])
                minmax = self.out_minmax
            else:
                self.layers[nl].inp_minmax = np.zeros([self.layers[nl].ci, 2])
                minmax = self.layers[nl].inp_minmax
            ni = 0
            for ns in nums_signal:
                t = self.layers[ns].out_minmax if ns != -1 else self.inp_minmax
                minmax[ni : ni + len(t)] = t
                ni += len(t)
        self.init()

    def step(self, inp):
        """ 
        Simulated step
        
        :Parameters:
            inp: array like
                Input vector
        :Returns:
            out: array
                Output vector
            
        """
        self.inp = inp
        for nl, nums_signal in enumerate(self.connect):
            if nl == len(self.layers):
                signal = np.empty(self.co)
            else:
                signal = np.empty(self.layers[nl].ci)
            ni = 0
            for ns in nums_signal:
                s = self.layers[ns].out if ns != -1 else inp
                l = len(s)
                signal[ni : ni + l] = s
                ni += l
            # Если не выход сети
            if nl != len(self.layers):
                self.layers[nl].step(signal)
        self.out[:] = signal
        return self.out

    def sim(self, input):
        """
        Simulate a neural network
        
        :Parameters:
            input: array like
                array input vectors
        :Returns:
            outputs: array like
                array output vectors
        """
        input = np.asfarray(input)
        assert input.ndim == 2
        assert input.shape[1] == self.ci
        
        output = np.zeros([len(input), self.co])
        
        for inp_num,inp in enumerate(input):
            output[inp_num,:] = self.step(inp)

        return output

    def init(self):
        """
        Iinitialization weights and bias
        
        :Returns: None
        
        """
        for layer in self.layers:
            layer.init()

    def train(self, *args, **kwargs):
        """ Train network """
        return self.trainf(self, *args, **kwargs)

    def clear_signals(self):
        """
        Clear of deley
        
        """
        self.inp.fill(0)
        self.out.fill(0)
        for layer in self.layers:
            layer.inp.fill(0)
            layer.out.fill(0)

    def save(self, fname):
        """
        Save network on file
        
        :Parameters:
            fname: file name
        
        """
        tool.save(self, fname)

    def copy(self):
        """
        Copy network
        
        """
        import copy
        cnet = copy.deepcopy(self)

        return cnet
        

class Layer(object):
    """
    Abstract Neural Layer class 
    
    :Parameters:
        ci: int
            Number of inputs
        cn: int
            Number of neurons
        co: int
            Number of outputs
        property: list (default ['w', 'b'])
            names of properties of neurons
    
    """
    def __init__(self, ci, cn, co ,property=['w','b']):
        
        self.ci = ci
        self.cn = cn
        self.co = co
        self.np = {}
        for p in property:
            self.np[p] = None
        self.inp = np.zeros(ci)
        self.out = np.zeros(co)
        # Abstract property must be change when init Layer
        self.out_minmax = np.zeros([self.co,2])
        # This property must be change when init Net
        self.inp_minmax = np.zeros([self.ci,2])
        self.initf=None

    def step(self, inp):
        """ Layer simulation step """
        assert len(inp) == self.ci
        out = self._step(inp)
        self.inp = inp
        self.out = out

    def init(self):
        """ Init Layer random values """
        if type(self.initf) is list:
            for initf in self.initf: initf(self)
        elif self.initf is not None:
            self.initf(self)

    def _step(self, inp):
        raise NotImplementedError("Call abstract metod Layer._step")


class Train(object):
    """Main train abstract class"""
    def __init__(self, **kwargs):
        # Sets defaults train params
        from error import SSE
        self.defaults = {'epochs': 1000,
                         'goal': 0.01, 
                         'lr':0.01, 
                         'show': 100,
                         'errorf': SSE()}
        
        for k in kwargs:
            self.defaults[k] = kwargs[k]
        
    def __call__(self, net, input, target=None, *args, **kwargs):
        """
    :Returns:
        error: error process
    :Parameters:
        input: array like (l x ci)
            train input patterns
        target: array like (l x co)
            train target patterns
        epochs: int (default 1000)
            Number of train epochs
        show: int
            Print periud
        goal: float (default 0.01)
            The goal of train
        lr: float (default 0.01)
            learning rate
        """
        self.param = {}
        for k in self.defaults:
            if k in kwargs:
                self.param[k] = kwargs[k]
                del kwargs[k]
            else:
                self.param[k] = self.defaults[k]
        
        input = np.asfarray(input)
        assert input.ndim == 2
        if target is not None:
            target = np.asfarray(target)
            assert target.ndim == 2
            args = [target] + list(args)
        
        self.error = []
        try:
            self._init(net, input, *args, **kwargs)
        except NeuroLabError as e:
            print "Train algoritm unsupport this type of neural network", e
        
        try:
            self._cycle(net, input, *args)
        except TrainStop as msg:
            if self.param['show']: print msg
        else:
            if self.param['show']: print "Stop by epochs"
            
        return np.array(self.error)
        
    def _cycle(self, net, input, *args):
        pass
        
    def _init(self, *args, **kwargs):
        pass
    
    def _error(self, net, input, target):
        output = net.sim(input)
        error = target - output
        err = self.param['errorf'](error)
        return err
        
    def _step_check(self, net, input, *args):
        epoch = len(self.error)
        show = self.param['show']
        err = self.error[-1]
        if show and (epoch % show) == 0:
            print "Epoch: {0}; Error: {1};".format(epoch, err)
        if err < self.param['goal']:
            # Цель обучения достигнута
            raise TrainStop('Stop by goal')
    

class TrainInt(Train):
    """ Abstract train class """
    def _cycle(self, net, input, *args):
        for epoch in range(self.param['epochs']):
            self._step(net, input, *args)
            err = self._error(net, input, *args)
            self.error.append(err)
            self._step_check(net, input, *args)
        return None    
    
    def _step(self, net, input, *args):
        pass


class TrainExt(Train):
    """ Abstract train class to use external libraries """
    def _init(self, net, input, target, *args, **kwargs):
        self.kwargs = kwargs
        self._last_err = None
    
    def _cycle(self, net, input, target, *args):
        
        def fcn(x, *args):
            tool.np_set(net, x)
            self._last_err = self._error(net, input, target)
            return self._last_err
        
        def step(*args):
            err = self._last_err
            self.error.append(err)
            self._step_check(net, input, target)

        size = tool.np_size(net)
        x0 = tool.np_get(net, size)
        self._optimize(net, input, target, fcn, x0, step, *args)
        return None
        
    def _optimize(net, input, target, fcn, x0, step, *args):
        pass