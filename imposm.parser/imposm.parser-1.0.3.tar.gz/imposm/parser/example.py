# Copyright 2011 Omniscale GmbH & Co. KG
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import multiprocessing
from imposm.parser import OSMParser

if __name__ == '__main__':
    
    class Counter(object):
        def __init__(self):
            self.coords_counter = 0
            self.nodes_counter = 0
            self.ways_counter = 0
            self.relations_counter = 0

        def incr_coords(self, coords):
            self.coords_counter += len(coords)
        def incr_nodes(self, nodes):
            self.nodes_counter += len(nodes)
        def incr_ways(self, ways):
            self.ways_counter += len(ways)
        def incr_relations(self, relations):
            self.relations_counter += len(relations)
            
    counter = Counter()
    
    p = OSMParser(
        nodes_callback=counter.incr_nodes,
        coords_callback=counter.incr_coords,
        ways_callback=counter.incr_ways,
        relations_callback=counter.incr_relations)
    p.parse(sys.argv[1])
    print counter.coords_counter, counter.nodes_counter, counter.ways_counter, counter.relations_counter