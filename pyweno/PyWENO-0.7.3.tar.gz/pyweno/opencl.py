



#### OpenCL
    


#     def __init__(self, k, ctx=None, queue=None, **kwargs):

#         if ctx is None:
#             ctx = cl.create_some_context()

#         if queue is None:
#             queue = cl.CommandQueue(ctx)

#         src = _kernel_pmweno(k)
#         self.weno5 = cl.Program(ctx, src).build()

#         self.ctx = ctx
#         self.queue = queue

#         self.k = k


#     ##################################################################
#     # reconstruct
#     #

#     def reconstruct(self, q, q_plus, q_minus):
#         """Reconstruct *q* at the left edge of each cell and store the
#            results in *q_plus* (right/+ limit) and *q_minus* (left/-
#            limit).

#            **Arguments:**

#            * *q* - cell averages of function to reconstruct
#            * *q_plus* - store + reconstruction here
#            * *q_minus* - store - reconstruction here

#            NOTE: the domain boundaries are avoided (zeroed out in
#            *q_plus* and *q_minus*).
#         """

#         k = self.k

#         q32 = q.astype(np.float32)
#         p32 = q_plus.astype(np.float32)
#         m32 = q_minus.astype(np.float32)

#         mf = cl.mem_flags
#         q_buf = cl.Buffer(self.ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=q32)
#         p_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, p32.nbytes)
#         m_buf = cl.Buffer(self.ctx, mf.WRITE_ONLY, m32.nbytes)

#         length = (q32.shape[0] - (2*k-1),)
#         #length = (q32.shape[0],)

#         self.weno5.weno5(self.queue, length, None, q_buf, p_buf, m_buf)
#         cl.enqueue_read_buffer(self.queue, p_buf, p32).wait()
#         cl.enqueue_read_buffer(self.queue, m_buf, m32).wait()

#         q_plus[:]  = p32.astype(q_plus.dtype)
#         q_minus[:] = m32.astype(q_minus.dtype)

#         # zero out boundaries
#         q_plus[:k] = np.zeros(k, dtype=q_plus.dtype)
#         q_minus[:k] = np.zeros(k, dtype=q_plus.dtype)
#         q_plus[-k+1:] = np.zeros(k-1, dtype=q_plus.dtype)
#         q_minus[-k+1:] = np.zeros(k-1, dtype=q_plus.dtype)
