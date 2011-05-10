from pyec.db.models import *
from pyec.util.benchmark import *
import cPickle

import sys
import os 
import os.path

def gather(seg):
   data = Segment.objects.getAvgMax(seg, 100)
   f = open(os.path.join('data2', seg.name + '.data'), 'w')
   cPickle.dump(data, f)
   f.close()

def comps():
   benchmarks = ["whitley", "ackley", "shekelsFoxholes"]
   algos = ['sa']#,["de", "pso", "ga", "boa", "es"]

   for alg in algos:
      for bm in allBenchmarks:
         if bm.name in benchmarks:
         
            prefix = alg + '.' + bm.name + '.'
            segments = Segment.objects.filter(name__startswith=prefix)
            print prefix, len(segments)
            for seg in segments:
               try:
                  gather(seg)
               except Exception, msg:
                  print "problem with segment ", seg.name, " - ", msg

if __name__ == "__main__":
   print "running gather on ", sys.argv[1]
   if sys.argv[1] == 'comps':
      comps()
   else:
      gather(Segment.objects.get(name=sys.argv[1]))

