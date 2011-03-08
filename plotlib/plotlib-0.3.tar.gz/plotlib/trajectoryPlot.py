import numpy as np
def trajectoryPlot(traj, timesteps = 'All', species='All', pylab=None):
    if pylab:
        import pylab
    # get species indices--assume no change of species
    struct = traj.getStructure(0)
    if timesteps=='All':
        ti=(0,traj.num_timesteps,1)
    else:
        ti=timesteps
    if species=='All':
        indices=np.arange(len(struct))
    else:
        indices=[]
        for ind,atom in enumerate(struct):
            if atom.symbol in species: 
                indices.append(ind)   
        indices = np.array(indices)
    for ts in range(traj.num_timesteps)[ti[0]:ti[1]:ti[2]]:
        struct = traj.getStructure(ts)
        positions = np.array(struct.xyz_cartn)
        xPos = positions[indices,0]
        yPos = positions[indices,1]
        pylab.plot(xPos,yPos,'.b')
