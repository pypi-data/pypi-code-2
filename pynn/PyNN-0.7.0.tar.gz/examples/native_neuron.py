from nrnutils import Mechanism, Section
from pyNN import neuron as nrn
from pyNN.random import RandomDistribution
from pyNN.neuron.cells import _new_property
import copy

nrn.setup()


class NativeNeuronModel(object):
    default_initial_values = {}
    default_parameters = {}
    injectable = True
    conductance_based = False

    def __init__(self, parameters):
        self.parameters = self.__class__.checkParameters(parameters, with_defaults=True)

    @classmethod
    def has_parameter(cls, name):
        return name in cls.default_parameters

    @classmethod
    def get_parameter_names(cls):
        return cls.default_parameters.keys()

    @classmethod
    def checkParameters(cls, supplied_parameters, with_defaults=False):
        """
        Returns a parameter dictionary, checking that each
        supplied_parameter is in the default_parameters and
        converts to the type of the latter.

        If with_defaults==True, parameters not in
        supplied_parameters are in the returned dictionary
        as in default_parameters.

        """
        default_parameters = cls.default_parameters
        if with_defaults:
            parameters = copy.copy(default_parameters)
        else:
            parameters = {}
        if supplied_parameters:
            for k in supplied_parameters.keys():
                if default_parameters.has_key(k):
                    err_msg = "For %s in %s, expected %s, got %s (%s)" % \
                              (k, cls.__name__, type(default_parameters[k]),
                               type(supplied_parameters[k]), supplied_parameters[k])
                    # same type
                    if type(supplied_parameters[k]) == type(default_parameters[k]): 
                        parameters[k] = supplied_parameters[k]
                    # float and something that can be converted to a float
                    elif isinstance(default_parameters[k], float): 
                        try:
                            parameters[k] = float(supplied_parameters[k]) 
                        except (ValueError, TypeError):
                            raise errors.InvalidParameterValueError(err_msg)
                    # list and something that can be transformed to a list
                    elif isinstance(default_parameters[k], list):
                        try:
                            parameters[k] = list(supplied_parameters[k])
                        except TypeError:
                            raise errors.InvalidParameterValueError(err_msg)
                    else:
                        raise errors.InvalidParameterValueError(err_msg)
                else:
                    raise errors.NonExistentParameterError(k, cls, cls.default_parameters.keys())
        return parameters


class SimpleNeuron(object):
    
    def __init__(self, **parameters):
        # define ion channel parameters
        leak = Mechanism('pas', e=-65, g=parameters['g_leak'])
        hh = Mechanism('hh', gl=parameters['g_leak'], el=-65,
                       gnabar=parameters['gnabar'], gkbar=parameters['gkbar'])
        # create cable sections
        self.soma = Section(L=30, diam=30, mechanisms=[hh])
        self.apical = Section(L=600, diam=2, nseg=5, mechanisms=[leak], parent=self.soma,
                              connect_to=1)
        self.basilar = Section(L=600, diam=2, nseg=5, mechanisms=[leak], parent=self.soma)
        self.axon = Section(L=1000, diam=1, nseg=37, mechanisms=[hh])
        # synaptic input
        self.apical.add_synapse('ampa', 'Exp2Syn', e=0.0, tau1=0.1, tau2=5.0)

        # needed for PyNN
        self.source_section = self.soma
        self.source = self.soma(0.5)._ref_v
        self.parameter_names = ('g_leak', 'gnabar', 'gkbar')
        
    def _set_g_leak(self, value):
        for sec in (self.apical, self.basilar):
            for seg in sec:
               seg.pas.g = value
        for sec in (self.soma, self.axon):
            for seg in sec:
                seg.hh.gl = value
    def _get_g_leak(self):
        return self.apical(0.5).pas.g
    g_leak = property(fget=_get_g_leak, fset=_set_g_leak)

    def _set_gnabar(self, value):
        for sec in (self.soma, self.axon):
            for seg in sec:
                seg.hh.gnabar = value
    def _get_gnabar(self):
        return self.soma(0.5).hh.gnabar
    gnabar = property(fget=_get_gnabar, fset=_set_gnabar)

    def _set_gkbar(self, value):
        for sec in (self.soma, self.axon):
            for seg in sec:
                seg.hh.gkbar = value
    def _get_gkbar(self):
        return self.soma(0.5).hh.gkbar
    gkbar = property(fget=_get_gkbar, fset=_set_gkbar)


class SimpleNeuronType(NativeNeuronModel):
    default_parameters = {'g_leak': 0.0002, 'gkbar': 0.036, 'gnabar': 0.12}
    default_initial_values = {'v': -65.0}
    recordable = ['v']
    model = SimpleNeuron
    

parameters = {'g_leak': 0.0003}
p1 = nrn.Population(10, SimpleNeuronType, parameters)
print p1.get('g_leak')
p1.rset('gnabar', RandomDistribution('uniform', [0.10, 0.14]))
print p1.get('gnabar')
p1.initialize('v', -63.0)

current_source = nrn.StepCurrentSource([50.0, 110.0, 150.0, 210.0],
                                       [0.4, 0.6, -0.2, 0.2])
p1.inject(current_source)

p2 = nrn.Population(1, nrn.SpikeSourcePoisson, {'rate': 100.0})

connector = nrn.AllToAllConnector(weights=0.1)

prj_alpha = nrn.Projection(p2, p1, connector, target='apical.ampa')

