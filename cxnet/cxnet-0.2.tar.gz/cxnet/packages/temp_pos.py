def get_name_from_networkx_pos(x,y, limit=0.02):
    for i in pos.keys():
	 if abs(pos[i] - a).max() < limit:
	     print i, pos[i]

