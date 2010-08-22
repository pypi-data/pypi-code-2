from __future__ import division
import sys

#f=open("connected_near_nodes2.txt", "w")
f=sys.stdout

for x in linspace(.2, 1, 9):
    num = num_with_edge = max_predecessors= 0
    for i,j,p in N:
	if x<=p<x+0.1:
	    num +=1
	    mx = max([len(G.predecessors(i)),len(G.predecessors(j))])
	    if mx >50 and p>0.9: print G.node_names[i].center(20), G.node_names[j].center(20), "%5d"%mx,p
	    if mx > max_predecessors:
		max_predecessors = mx
	    if (G.has_edge((i,j)) or G.has_edge((j,i))):
		num_with_edge +=1
    print >>f, "| %5.1f | %5d | %5d | %5.3f | %5d | " %  (x, num, num_with_edge, num_with_edge/num, max_predecessors)
    print >>f, "+-------+-------+-------+-------+-------+"
if f.name != "<stdout>":
    f.close()
