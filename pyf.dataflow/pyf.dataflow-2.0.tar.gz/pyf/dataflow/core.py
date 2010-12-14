"""
@author: Jonathan Schemoul <jonathan.schemoul@gmail.com
@license: LGPL

Lazy flow lib based on ZFlow that was created by Jeremy Lowery and
released as LGPL, more info at http://www.thensys.com/. 
@author: Jeremy Lowery
"""
import inspect, sys, itertools
from pprint import pprint

__all__ = ['component', 'runner', 'pprint_component']

BYPASS_VALS = [Ellipsis]

def component(*port_specs, **xtra_args):
    def decor(fun):
        arg_specs = inspect.getargspec(fun)[0]
        if arg_specs[0] == 'self':
            arg_specs = arg_specs[1:]
        match = zip(port_specs, arg_specs)
        name = xtra_args.get('name', fun.__name__)
        in_ports = [m[1] for m in match if m[0] == 'IN']
        out_ports = [m[1] for m in match if m[0] == 'OUT']
        in_array_ports = [m[1] for m in match if m[0] == 'INA']
        out_array_ports = [m[1] for m in match if m[0] == 'OUTA']
        controls = arg_specs[len(port_specs):]

        if 'generator_port' in xtra_args:
            generator_port = xtra_args['generator_port']
            if generator_port not in out_ports:
                raise ValueError, ("The given generator port %r does not match "
                    "a port with an OUT port specification" % generator_port)
        elif len(out_ports) == 1:
            generator_port = out_ports[0]
        else:
            generator_port = None

        fun.zf_component = True
        fun.zf_name = name
        fun.zf_generator_port = generator_port
        fun.zf_in_ports = in_ports
        fun.zf_out_ports = out_ports
        fun.zf_in_array_ports = in_array_ports
        fun.zf_out_array_ports = out_array_ports
        fun.zf_port_order = arg_specs[:len(port_specs)]
        fun.zf_controls = controls
        return fun
    return decor

def pprint_component(comp, stream=sys.stdout):
    print >>stream, comp.zf_name
    if comp.__doc__:
        print >>stream, comp.__doc__
        print >>stream, ''

    print >>stream, "PORTS"
    print >>stream, "-"*80
    pmap = [
        ("IN", comp.zf_in_ports),
        ("OUT", comp.zf_out_ports),
        ("IN ARRAY", comp.zf_in_array_ports),
        ("OUT ARRAY", comp.zf_out_array_ports)
    ]
    for port in comp.zf_port_order:
        for s, v in pmap:
            if port in v:
                print >>stream, s.ljust(10),
                break
        else:
            print >>stream, "UNKNOWN".ljust(10),
        print >>stream, port
    if comp.zf_generator_port:
        print >>stream, ''
        print >>stream, "GENERATOR PORT: %s" % comp.zf_generator_port
    if comp.zf_controls:
        print >>stream, '\nCONTROLS'
        print >>stream, "-"*80
        for c in comp.zf_controls:
            print c

FNAME, FTYPE, FPORT, TNAME, TTYPE, TPORT = range(6)
EFPORT, EFPROTOCOL, EFPRIORITY, ETPORT, ETPROTOCOL, ETPRIORITY = range(6)

def build_nodes(mesh, G, A):
    # Build Nodes
    for m in mesh:
        if not isinstance(m, (list, tuple)):
            raise ValueError, "Found invalid edge line %r, excepted list or tuple." % m
        if m[FNAME] in G:
            node = A[m[FNAME]]
            if node['component'] != m[FTYPE]:
                raise ValueError, ("Multiple component labels for %r point to "
                    "different component types. Found %r, excepted %r" %
                    (m[FNAME], m[FTYPE], node['component']))
        else:
            G.add_node(m[FNAME])
            A[m[FNAME]] = {'component' : m[FTYPE]}
        if m[TNAME] in G:
            node = A[m[TNAME]]
            if node['component'] != m[TTYPE]:
                raise ValueError, ("Multiple component labels for %r point to "
                    "different component types. Found %r, excepted %r" %
                    (m[TNAME], m[TTYPE], node['component']))
        else:
            G.add_node(m[TNAME])
            A[m[TNAME]] = {'component' : m[TTYPE]}

def build_edges(mesh, G, A):
    # Build Edges
    for m in mesh:
        fpriority = -1
        tpriority = -1
        # Ensure the port connection is valid
        fcomp = A[m[FNAME]]['component']
        tcomp = A[m[TNAME]]['component']

        from_port = m[FPORT]
        if m[FPORT] in fcomp.zf_out_ports:
            fprotocol = 'STANDARD'
        elif m[FPORT] in fcomp.zf_out_array_ports:
            fprotocol = 'ARRAY'
        # Specification used to connect an out array line to another component.
        elif isinstance(m[FPORT], tuple) and len(m[FPORT]) == 2 and m[FPORT][0] in fcomp.zf_out_array_ports:
            fprotocol = 'ARRAY'
            fpriority = m[FPORT][1]
            from_port = m[FPORT][0]
        else:
            raise ValueError, "Out port %s:%s does not exist." % (m[FNAME], m[FPORT])

        to_port = m[TPORT]
        if m[TPORT] in tcomp.zf_in_ports:
            tprotocol = 'STANDARD'
        elif m[TPORT] in tcomp.zf_in_array_ports:
            tprotocol = 'ARRAY'
        elif isinstance(m[TPORT], tuple) and len(m[TPORT]) == 2 and m[TPORT][0] in tcomp.zf_in_array_ports:
            tprotocol = 'ARRAY'
            tpriority = m[TPORT][1]
            to_port = m[TPORT][0]
        else:
            raise ValueError, "In port %s:%s does not exist." % (m[TNAME], m[TPORT])
        
        # We have to put a priority on the edge so that array ports get their ports
        # processed in the correct order.
        existing_edges = G.edges()

        # Loop through all of the edges and find names and OUT ports that match this
        # new edge.
        from_side = [f[:1] + f[2][:3] for f in existing_edges]
        if fpriority == -1:
            while (m[FNAME], from_port, fprotocol, fpriority) in from_side:
                fpriority = fpriority + 5

        # Do the same for the IN edges
        to_side = [f[1:2] + f[2][3:6] for f in existing_edges]
        if tpriority == -1:
            while (m[TNAME], to_port, tprotocol, tpriority) in to_side:
                tpriority = tpriority + 5
        G.add_edge(m[FNAME], m[TNAME], (from_port, fprotocol, fpriority, to_port, tprotocol, tpriority))

def control_match(map, this, values, defaults):
    """
    """
    ctrls = {}
    for label, cdef in map.items():
        for ddef, dvalue in defaults.items():
            if ddef[0] == this:
                ctrls[ddef[1]] = dvalue
        if cdef[0] == this and label in values:
            ctrls[cdef[1]] = values[label]
    return ctrls


## The port number classes are used to provide a communication protocol
## for components to yield back values that are send to out ports
p_counter = itertools.count(1)
class PortNumber(int):
   def __new__(self):
        global p_counter
        n = p_counter.next()
        if n >= 1048576:
            p_counter = itertools.count(1)
            n = p_counter.next()
        return int.__new__(self, n)

class ArrayPortNumber(int):
    def __new__(self):
        global p_counter
        n = p_counter.next()
        if n >= 1048576:
            p_counter = itertools.count(1)
            n = p_counter.next()
        return int.__new__(self, n)

    def size(self):
        return ArrayPortSizeSpec(self)

    def __call__(self, idx):
        return ArrayPortSpec(self, idx)

class ArrayPortSpec(object):
    def __init__(self, num, idx):
        self.port = num
        self.idx = idx

class ArrayPortSizeSpec(object):
    def __init__(self, port):
        self.port = port

class runner(object):
    """Provides a run harness for a component."""
    def __init__(self, comp, commands={}, handle_bypass=True):
        self.comp = comp
        self.out_buffer = dict([(n, []) for n in comp.zf_out_ports])
        self.out_lookup = {}
        self.out_array_lookup = {}
        self.in_gens = {}
        self.in_gen_arrays = {}
        self.arg_list = []
        self.build_arg_list()
        self.generator = self.comp(*self.arg_list, **commands)

        self.handle_bypass = handle_bypass

    def input_stream(self, name):
        # We have to do this lazy-style so we can have loops in the graph
        #XXX: After doing the code, the loops don't work anyway, but we're keeping this
        # construct.

        def closure():
            if name in self.in_gens:
                if self.handle_bypass:
                    for value in self.in_gens[name]:
                        if value in BYPASS_VALS:
                            self.pass_value(value)
                        else:
                            yield value
                else:
                    for value in self.in_gens[name]:
                        yield value

            elif name in self.in_gen_arrays:
                for value in self.in_gen_arrays[name]:
                    yield value
            else:
                raise ValueError, ("Invalid IN port %r on component %r. "
                    "Valid Ports: %s" %
                    (name, self.comp.zf_name, self.in_gens.keys() + self.in_gen_arrays.keys()))

        return closure()

    def connect_in(self, name, value):
        if name in self.comp.zf_in_ports:
            self.in_gens[name] = value
        elif name in self.comp.zf_in_array_ports:
            # We are directly assigning an array to the port. the zs_is_array
            # flag tells us so
            if getattr(value, 'zf_is_array', False):
                self.in_gen_arrays[name] = value
                return
            # We are appending connections to the array port in sequence as they come in
            if name not in self.in_gen_arrays:
                self.in_gen_arrays[name] = []
            self.in_gen_arrays[name].append(value)
        else:
            raise ValueError, "No port %r on component %r" % (name, self.comp.zf_name)

    def build_arg_list(self):
        args = []
        comp = self.comp
        for port in comp.zf_port_order:
            if port in comp.zf_in_ports or port in comp.zf_in_array_ports:
                args.append(self.input_stream(port))
            elif port in comp.zf_out_ports:
                num = PortNumber()
                self.out_lookup[num] = port
                args.append(num)
            elif port in comp.zf_out_array_ports:
                num = ArrayPortNumber()
                self.out_lookup[num] = port
                args.append(num)
            else:
                raise ValueError, ("Component %r include a port order for port %r, "
                    "but the port is not registered as an IN port or OUT port" % (comp.zf_name, port))
        self.arg_list = args

    def buffer_empty(self, out_port, idx):
        """Are there any results for us to yield?"""
        is_out_array_port = out_port in self.comp.zf_out_array_ports
        if is_out_array_port:
            # We are scanning a specific out array port index
            if idx != -1:
                if out_port not in self.out_array_lookup:
                    return True
                elif not self.out_array_lookup[out_port][idx]:
                    return True
                else:
                    return False
            # We are scanning an entire out array port. As soon as the
            # size has been set, we can return our value
            else:
                if out_port not in self.out_array_lookup:
                    return True
                else:
                    return False
        else:
            return not bool(self.out_buffer[out_port])
        
    def pass_value(self, value):
        """ Provides a way to bypass completely the component and send data to
        the outports """
        for out_port in self.comp.zf_out_array_ports:
            for number_port in self.out_array_lookup[out_port]:
                number_port.append(value)
        
        for buffer in self.out_buffer.itervalues():
            buffer.append(value)

    def yield_value(self, out_port, idx):
        """ Provide the value for the given outport and out array index. """
        is_out_array_port = out_port in self.comp.zf_out_array_ports
        if is_out_array_port:
            if idx != -1:
                return self.out_array_lookup[out_port][idx].pop(0), False
            else:
                return [self(out_port, i) for i in range(len(self.out_array_lookup[out_port]))], True
        else:
            return self.out_buffer[out_port].pop(0), False

    def __call__(self, out_port, idx=-1):
        """ This is the runtime engine """
        def run():
            while True:
                while self.buffer_empty(out_port, idx):
                    result = self.generator.next()
                    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], PortNumber):
                        this_port = self.out_lookup[result[0]]
                        line = result[1]
                        self.out_buffer[this_port].append(line)
                    elif isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], ArrayPortSizeSpec):
                        this_port = self.out_lookup[result[0].port]
                        self.out_array_lookup[out_port] = [[] for i in range(result[1])]
                    elif isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], ArrayPortSpec):
                        # Pushing a value in an array output index
                        this_port = self.out_lookup[result[0].port]
                        index = result[0].idx
                        if this_port not in self.out_array_lookup:
                            raise ValueError, ("Encountered OUT array port value before a size has been specified "
                                "on component %r, port %r" % (self.comp.zf_name, this_port))
                        self.out_array_lookup[this_port][index].append(result[1])
                    elif self.comp.zf_generator_port:
                        self.out_buffer[self.comp.zf_generator_port].append(result)
                    else:
                        raise ValueError, ("component %r yielded invalid value %r. "
                            "Please provide a generator_port or yield (port, value)" % (self.comp.zf_name, result))
                value, stop = self.yield_value(out_port, idx)
                if stop:
                    for v in value:
                        yield v
                    return
                else:
                    yield value

        # We have to put this here so we can detect in on in_connect to hook up out arrays to in arrays
        # properly
        gen = run()
        if out_port in self.comp.zf_out_array_ports and idx == -1:
            return OutArrayIterator(gen)
        else:
            return gen

class OutArrayIterator(object):
    """ We have to make this wrapper because we can't assign zf_is_array to a generator object
    because it's attributes are read only. """
    def __init__(self, gen):
        self.gen = gen
        self.zf_is_array = True
    def __iter__(self):
        return self.gen
