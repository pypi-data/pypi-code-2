import time
from dana import *
import scipy.sparse as sp

n      = 64
src    = np.ones((n,n))
dst    = np.zeros((n,n))
kernel = np.zeros((n,n))
kernel[n//2,n//2] = 1

t0 = time.clock()
nz_rows, nz_cols = kernel.nonzero()
nz_data  = kernel[nz_rows, nz_cols]
nz_rows += src.shape[0]//2 - kernel.shape[0]//2
nz_cols += src.shape[1]//2 - kernel.shape[1]//2
boundary = False
#k_shape_0, k_shape_1 = kernel.shape[0], kernel.shape[1]
k_shape_0, k_shape_1     = src.shape[0], src.shape[1]
dst_shape_0, dst_shape_1 = dst.shape[0], dst.shape[1]
src_shape_0, src_shape_1 = src.shape[0], src.shape[1]
R, C, D = [], [], []
for i in xrange(src_shape_0):
    if boundary:
        nz_rows_1 = (nz_rows - i) % k_shape_0
    else:
        nz_rows_1 = (nz_rows - k_shape_0//2+i)
    n = np.where((nz_rows_1 >= 0)*(nz_rows_1 < k_shape_0))[0]
    nz_rows_1 = nz_rows_1[n]
    nz_cols_1 = nz_cols[n]
    nz_data_1 = nz_data[n]
    for j in xrange(src_shape_1):
        if boundary:
            nz_cols_2 = (nz_cols_1 - j) % k_shape_1
        else:
            nz_cols_2 = (nz_cols_1 - k_shape_1//2+j)
        n = np.where((nz_cols_2 >= 0)*(nz_cols_2 < k_shape_1))[0]
        nz_rows_2 = nz_rows_1[n]
        nz_cols_2 = nz_cols_2[n]
        nz_data_2 = nz_data_1[n]
        index = i*src_shape_1+j
        R.extend( [index,]*len(nz_data_2) )
        C.extend( (nz_rows_2*k_shape_0 + nz_cols_2).tolist() )
        D.extend( nz_data_2.tolist() )

M = sp.coo_matrix( (D,(R,C)), (src.size,dst.size))
print time.clock()-t0


#print M.todense()
#print
#print (src.flatten()*M).reshape(src.shape)
#print    

t0 =time.clock()
SparseConnection(src,dst,kernel)
print time.clock()-t0


# t0 = time.clock()
# I, J, D = [], [], []
# K = sp.coo_matrix(kernel)
# for i in range(src.shape[0]):
#     K1 = K.copy()
#     if boundary:
#         K1.row = (K1.row - i) % K.shape[0]
#     else:
#         K1.row = (K1.row - K.shape[0]//2+i)
#         n = np.where((K1.row >= 0)*(K1.row < K.shape[0]))[0]
#         K1.row  = K1.row[n]
#         K1.col  = K1.col[n]
#         K1.data = K1.data[n]
#     for j in range(src.shape[1]):
#         K2 = K1.copy()
#         if boundary:
#             K2.col = (K2.col - j) % K.shape[1]
#         else:
#             K2.col = (K2.col - K.shape[1]//2+j)
#             n = np.where((K2.col >= 0)*(K2.col < K.shape[1]))[0]
#             K2.row  = K2.row[n]
#             K2.col  = K2.col[n]
#             K2.data = K2.data[n]
#         # K2.row * K.shape[0] + K2.col
#         index = i*src.shape[1]+j
#         I.extend( [index,]*len(K2.data) )
#         J.extend( (K2.row * K.shape[0] + K2.col).tolist() )
#         D.extend( K2.data.tolist() )
# M = sp.coo_matrix( (D,(I,J)), (src.size,dst.size))
# print time.clock()-t0

# #print M.todense()
# #print
# #print (src.flatten()*M.todense()).reshape(src.shape)
# #print
