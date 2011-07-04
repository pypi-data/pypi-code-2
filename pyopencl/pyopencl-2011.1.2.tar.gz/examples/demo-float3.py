import pyopencl as cl
import numpy

a = numpy.random.rand(50000).astype(numpy.float32)
b = numpy.random.rand(50000).astype(numpy.float32)

ctx = cl.create_some_context()
queue = cl.CommandQueue(ctx)

mf = cl.mem_flags
a_buf = cl.Buffer(ctx, mf.READ_WRITE | mf.COPY_HOST_PTR, hostbuf=a)

prg = cl.Program(ctx, """
    __kernel void sum(__global float *c)
    {
      int gid = get_global_id(0);
      c[gid] = sizeof(float3);
    }
    """).build()

prg.sum(queue, a.shape, None, a_buf)

cl.enqueue_copy(queue, a, a_buf)
print a
