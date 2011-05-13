import g_pipe
import Num

LREG = "/home/gpk/misctts/lreg_fit2"

def fill(f, wt, s):
	assert len(f)==len(wt)
	pi, po = g_pipe.popen2(LREG, ["lreg_fit2", "-smooth", "%g" % s])

	for tfw in zip(f, wt):
		pi.write("%g %g\n" % tfw)
	pi.close()
	o = map(float, po.readlines())
	po.close()
	assert len(o) == len(f)
	tmp = Num.asarray(o, Num.Float)
	return tmp

