import pyopencl as cl
import pyopencl.array as cl_array
import numpy as np

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

n = 10**6
a_gpu = cl_array.to_device(
        queue, np.random.randn(n).astype(np.float32))
b_gpu = cl_array.to_device(
        queue, np.random.randn(n).astype(np.float32))

cl_sum = cl_array.sum(a_gpu).get()
numpy_sum = np.sum(a_gpu.get())

print cl_sum, numpy_sum
