# Copyright 2010 Oren Zomer <oren.zomer@gmail.com>
#
# This file is part of pypsifas.

# pypsifas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pypsifas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with pypsifas.  If not, see <http://www.gnu.org/licenses/>.

from psifas_exceptions import *

try:
    import scapy.all as _scapy
except ImportError:
    raise ImportWarning("psifas will not support scapy wrappers because scapy is not installed")

from base import *
from utils import *

from datatypes.container import Container

from itertools import count, izip
from functools import partial
from copy import deepcopy

import re as _re

_layer_field_syntax = _re.compile(r"(layer[1-9]\d*|layer[1-9]\d*_type)$")

class _ScapyDissector(Psifas):
    def __init__(self, context_path):
        super(_ScapyDissector, self).__init__(Field('dissector_context', CLinkContainer(context_path)))
        
    def _decipher_values(self, location, all_fields):
        dissector = location.context().value
        if not isinstance(dissector, _scapy.Packet):
            layer_classes = []
            for layer_no in count(1):
                layer_class = location.context('dissector_context/layer%d_type' % (layer_no,)).value
                if layer_class is Bottom:
                    return (Bottom, Bottom) # not finished
                if layer_class is Default:
                    break
                layer_classes.append(layer_class)
                if layer_class in (_scapy.Raw, _scapy.NoPayload):
                    break
            if len(layer_classes) == 0:
                return (Bottom, Bottom)
            layer_objects = [cls() for cls in layer_classes]
            for underlayer, upperlayer in pairwise(layer_objects):
                upperlayer.underlayer = underlayer
                underlayer.upperlayer = upperlayer
            dissector = layer_objects[0]
        else:
            dissector_layer = dissector
            for layer_no in count(1):
                if dissector_layer is None:
                    break
                location.context('dissector_context/layer%d_type' % (layer_no,)).set_value(dissector_layer.__class__, location)
                if isinstance(dissector_layer, _scapy.Raw) or isinstance(dissector_layer, _scapy.NoPayload):
                    break
                dissector_layer = getattr(dissector_layer, 'upperlayer', None)
        return (dissector, AcceptAll)

        
    

class _ScapyPacket(Psifas):
    def __init__(self, context_path, struct_path):
        super(_ScapyPacket, self).__init__(Field('packet_context', CLinkContainer(context_path)),
                                           Field('packet_struct', CLinkContainer(struct_path)))

    def merge_struct_context(self, location):
        """
        Merges the container at packet_struct (its layer, layer_type attributes)
        with the packet_context's sub-contexts.
        """
        struct_container = location.context('packet_struct').value
        if isinstance(struct_container, Container):
            # put the container in the context-layers
            for attr, value in struct_container.iter_fields():
                if _layer_field_syntax.match(attr) is None:
                    continue
                location.context('packet_context/' + attr).set_value(value, location)
        
        struct_container = Container()
        for layer_no in count(1):
            layer_container = location.context('packet_context/layer%d' % (layer_no,)).value
            if layer_container not in (Bottom, Default):
                setattr(struct_container, 'layer%d' % (layer_no,), layer_container)

            layer_type = location.context('packet_context/layer%d_type' % (layer_no,)).value
            if layer_type not in (Bottom, Default):
                setattr(struct_container, 'layer%d_type' % (layer_no,), layer_type)
            else:
                break
        location.context('packet_struct').set_value(struct_container, location)
            
    def _decipher_values(self, location, all_fields):
        self.merge_struct_context(location)

        scapy_packet = location.context().value
        if not isinstance(scapy_packet, _scapy.Packet):
            layer_classes = []
            for layer_no in count(1):
                layer_class = location.context('packet_context/layer%d_type' % (layer_no,)).value
                if layer_class is Bottom:
                    return (Bottom, Bottom) # not finished
                if layer_class is Default:
                    break
                layer_classes.append(layer_class)
                if layer_class in (_scapy.Raw, _scapy.NoPayload):
                    break
            if len(layer_classes) == 0:
                return (Bottom, Bottom)
            
            layer_objects = [cls() for cls in layer_classes]
            for layer_no, scapy_layer in enumerate(layer_objects):
                # if it is Bottom, use an empty Container
                location.context('packet_context/layer%d' % (layer_no + 1,)).set_value(Container(), location)
                layer_container = location.context('packet_context/layer%d' % (layer_no + 1,)).value
    
                for field_name in set(scapy_layer.default_fields.keys() + scapy_layer.overloaded_fields.keys() + scapy_layer.fields.keys()):
                    # The field-value is in its context or in its layer-container.
                    # One of them might be Bottom or Default - which means we need the other one.
                    # The best way to choose is to merge them.
                    location.context('packet_context/layer%d/%s' % (layer_no + 1, field_name)).set_value(getattr(layer_container, field_name, Bottom), location)
                    field_value = location.context('packet_context/layer%d/%s' % (layer_no + 1, field_name)).value
                    if field_value is Bottom:
                        return (Bottom, Bottom)
                    elif field_value is not Default:
                        scapy_layer.setfieldval(field_name, field_value)
            for underlayer, upperlayer in pairwise(layer_objects):
                underlayer.add_payload(upperlayer)
            scapy_packet = layer_objects[0]
            # we calculated the scapy_packet, but some Default contexts should be overwritten.
        
        scapy_layer = scapy_packet
        for layer_no in count(1):
            # put the scapy-layer in the layer-contexts
            location.context('packet_context/layer%d_type' % (layer_no,)).set_value(scapy_layer.__class__, location)
            # TODO: is there a more efficient way to evaluate the final values of all the fields?
            layer_fields = scapy_layer.__class__(str(scapy_layer)).fields
            layer_container = Container()
            for field_name, value in layer_fields.iteritems():
                location.context('packet_context/layer%d/%s' % (layer_no, field_name)).set_value(value, location)
                setattr(layer_container, field_name, value)
            location.context('packet_context/layer%d' % (layer_no,)).set_value(layer_container, location)
            if isinstance(scapy_layer, _scapy.Raw) or isinstance(scapy_layer, _scapy.NoPayload):
                break
            scapy_layer = scapy_layer.payload
            
        self.merge_struct_context(location)
        
        return (scapy_packet, AcceptAll)

    def _decipher_location(self, location, all_fields):
        values = self._decipher_location_set(location, all_fields)
        return all((v is AcceptAll or not is_abstract(v)) for v in values)

class Scapy(Psifas):
    def __init__(self, first_psifas, *other_psifases):
        all_psifases = (first_psifas,) + other_psifases
        layers_psifases = all_psifases[:-1]
        payload_psifas = all_psifases[-1]
        if isinstance(payload_psifas, str):
            payload_psifas = Link('.../' + payload_psifas)
        layers_fields = [Field('layer%d_type' % (layer_index + 1,), layer_psifas) for layer_index, layer_psifas in enumerate(layers_psifases)]
        layers_fields.append(Field('layer%d_type' % (len(layers_psifases) + 1,), Constant(Default)))
        
        super(Scapy, self).__init__(UniqueField('.scapy_dissector', _ScapyDissector('..')),
                                    Field('payload', payload_psifas),
                                    Field('.scapy_packet', _ScapyPacket('..', '../.scapy_struct')),
                                    Field('.scapy_struct', Constant(Container())),
                                    *layers_fields)
        
    def do_dissect_payload(self, underlayer, s):
        if s and hasattr(underlayer, 'upperlayer'):
            upperlayer = underlayer.upperlayer
            try:
                upperlayer.dissect(s)
                upperlayer.dissection_done(upperlayer)
            except:
                upperlayer = _scapy.Raw(s, _internal = 1, _underlayer = underlayer)
            underlayer.add_payload(upperlayer)
        
    def _connections_decipher(self, scapy_dissector, payload, scapy_packet, scapy_struct):
        if not is_abstract(scapy_dissector) and not is_abstract(payload):
            # the dissection process
            new_scapy_packet = deepcopy(scapy_dissector)
            layer = new_scapy_packet
            while hasattr(layer, 'upperlayer'):
                layer.do_dissect_payload = partial(self.do_dissect_payload, layer)
                layer = layer.upperlayer
            new_scapy_packet.dissect(payload)
            new_scapy_packet = new_scapy_packet.copy() # removes the garbage attrs: upperlayer, do_dissect_payload
        else:
            new_scapy_packet = scapy_packet

        if isinstance(scapy_packet, _scapy.Packet):
            new_payload = str(scapy_packet)
        else:
            new_payload = payload

        return (scapy_dissector, new_payload, new_scapy_packet, scapy_struct)

    def _decipher(self, location, res, scapy_dissector, payload, scapy_packet, scapy_struct, *layer_types):
        scapy_packet = location.imerge(scapy_packet, res)
        scapy_dissector, payload, scapy_packet, scapy_struct = self._connections_decipher(scapy_dissector, payload, scapy_packet, scapy_struct)        
        return (scapy_packet, scapy_dissector, payload, scapy_packet, scapy_struct) + layer_types

class ScapyStruct(Scapy):
    def _decipher(self, location, res, scapy_dissector, payload, scapy_packet, scapy_struct, *layer_types):
        scapy_struct = location.imerge(scapy_struct, res)
        scapy_dissector, payload, scapy_packet, scapy_struct = self._connections_decipher(scapy_dissector, payload, scapy_packet, scapy_struct)

        if Bottom not in (scapy_dissector, payload, scapy_packet, scapy_struct):
            new_res = scapy_struct
        else:
            new_res = Bottom # we will return the scapy_struct Container only at the end

        return (new_res, scapy_dissector, payload, scapy_packet, res) + layer_types
