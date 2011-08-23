"""PyWENO OpenCL WENO reconstructor."""

import math
import numpy as np

import pyopencl as cl

valid_k = (5, 17)
valid_points = [ 'left', 'right', 'middle', '+/-',
                 'gauss', 'gauss_legendre',
                 'gauss_lobatto',
                 'gauss_radau' ]


programs = {}


def reconstruct(q, k, points, ctx=None, queue=None, qr=None, n=None):
  """Perform WENO reconstruction of q.

  :param q:      cell-averaged unknown to reconstruct
  :param k:      order of reconstruction (5 to 17)
  :param points: reconstruction points (see below)
  :param n:      number of reconstruction points (see below)
  """

  if (k % 2) == 0:
    raise ValueError, 'even order WENO reconstructions are not supported'

  if k < valid_k[0] or k > valid_k[1]:
    raise ValueError, '%d order WENO reconstructions are not supported' % k

  if not (points in valid_points):
    raise ValueError, "'points' must be one of: " + ', '.join(valid_points)

  if points == 'gauss':
    points = 'gauss_legendre'

  N = q.shape[0]
  k = (k+1)/2

  # validate n

  if points in [ 'left', 'right', 'middle' ]:
    n = 1
  elif n is None:
    n = k

  if points in [ '+/-' ]:
    n = 2

  assert(n > 0)

  # queue, context, program

  if queue is None:
    queue = cl.CommandQueue(ctx)

  if (points, n) not in programs:
    programs[(points, n)] = cl.Program(ctx, XXX).build()

  program = programs[(points, n)]


  if points == '+/-':
    raise NotImplementedError, '+/- not implemented yet'  

  mf = cl.mem_flags
  if not isinstance(q, cl.MemoryObject):
    qb = cl.Buffer(ctx, mf.READ_ONLY | mf.COPY_HOST_PTR, hostbuf=q)
  else:
    qb = q

  if qr is None:
    qr  = np.zeros((N,n))
    qrb = cl.Buffer(ctx, mf.READ_ONLY | mf.WRITE_ONLY, qr.nbytes)
  else:
    qrb = qr


  self.weno5.weno5(self.queue, length, None, q_buf, p_buf, m_buf)
  cl.enqueue_read_buffer(self.queue, p_buf, p32).wait()
  cl.enqueue_read_buffer(self.queue, m_buf, m32).wait()

  q_plus[:]  = p32.astype(q_plus.dtype)
  q_minus[:] = m32.astype(q_minus.dtype)

  # zero out boundaries
  q_plus[:k] = np.zeros(k, dtype=q_plus.dtype)
  q_minus[:k] = np.zeros(k, dtype=q_plus.dtype)
  q_plus[-k+1:] = np.zeros(k-1, dtype=q_plus.dtype)
  q_minus[-k+1:] = np.zeros(k-1, dtype=q_plus.dtype)




  # done!
  if squeeze:
    qr      = qr.squeeze()
    if weights and return_weights:
      weights = weights.squeeze()

  if return_smoothness and return_weights:
    return (qr, smoothness, weights)

  if return_smoothness:
    return (qr, smoothness)

  if return_weights:
    return (qr, weights)

  return qr



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
