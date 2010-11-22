import _texture
import numpy as np
f = np.array([
          [0,1,1,1],
          [0,0,1,1],
          [2,2,2,2],
        ])

Bc = np.zeros((3,3), f.dtype)
Bc[1,2] = 1
res = np.zeros((5,5), np.int32)
_texture.cooccurence(f, res, Bc, 1)
print res
