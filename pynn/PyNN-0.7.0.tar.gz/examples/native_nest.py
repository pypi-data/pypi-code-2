
from pyNN import nest
from pyNN.random import RandomDistribution

nest.setup()

class NativeNeuronModel(object):
    default_initial_values = {}
    default_parameters = {}
    injectable = True
    conductance_based = False

    def __init__(self, parameters):
        self.parameters = parameters

    @classmethod
    def has_parameter(cls, name):
        return name in cls.default_parameters

    @classmethod
    def get_parameter_names(cls):
        return cls.default_parameters.keys()

    @property
    def nest_name(self):
        return {
            "on_grid": self.nest_model,
            "off_grid": self.nest_model
        }

    @property
    def recordable(self):
        return nest.nest.GetDefaults(self.nest_model)['recordables'] + ['spikes']


class ht_neuron(NativeNeuronModel):
    default_initial_values = {
        'V_m': -65.0,
        'Theta': -51.0
    }
    default_parameters = {
        'Tau_m': 16.0,
        'Theta_eq': -51.0,
    }
    nest_model = 'ht_neuron'
    standard_receptor_type = False
    synapse_types = nest.nest.GetDefaults('ht_neuron')['receptor_types'].keys() + ['excitatory', 'inhibitory', None]
    conductance_based = True
    
    @classmethod
    def get_receptor_type(cls, name):
        return nest.nest.GetDefaults('ht_neuron')['receptor_types'][name]
    

class poisson_generator(NativeNeuronModel):
    injectable = False
    nest_model = "poisson_generator"
    default_parameters = {
        'rate': 0.0,
        'start': 0.0,
        'stop': 1e12
    }

parameters = {'Tau_m': 17.0}
p1 = nest.Population(10, ht_neuron, parameters)
print p1.get('Tau_m')
p1.rset('Tau_m', RandomDistribution('uniform', [15.0, 20.0]))
print p1.get('Tau_m')
p1.initialize('V_m', -64.0)
p1.initialize('Theta', -51.0)

current_source = nest.StepCurrentSource([50.0, 110.0, 150.0, 210.0],
                                        [0.4, 0.6, -0.2, 0.2])
p1.inject(current_source)

p2 = nest.Population(1, poisson_generator, {'rate': 100.0})

connector = nest.AllToAllConnector(weights=0.1)

prj_ampa = nest.Projection(p2, p1, connector, target='AMPA')

