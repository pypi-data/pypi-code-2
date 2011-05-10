import subprocess
import sys, os.path

algorithm = sys.argv[1]
benchmark = sys.argv[2]

start = 1
runs = 1
cmds = ['python26']
cmds.append(os.path.join(os.path.dirname(__file__), 'benchmark.py'))
cmds.append(algorithm)
cmds.append(benchmark)
for arg in sys.argv[3:]:
   if arg[:7] == '--runs=':
      runs = int(arg[7:])
   elif arg[:8] == '--start=':
      start = int(arg[8:])
   elif arg[:6] == '--seg=':
      pass
   elif arg[:5] == '--db=':
      pass
   else:
      cmds.append(arg)
cmds.append('--seg=%s.%s' % (algorithm, benchmark))
cmds.append('--db=%s%s' % (algorithm.lower(), benchmark.lower()))

for i in xrange(runs - start + 1):
   cmds[-2] = '--seg=%s.%s.%s' % (algorithm, benchmark, i+start)
   cmds[-1] = '--db=%s%s%s' % (algorithm.lower(), benchmark.lower(), i+start)
   subprocess.Popen(cmds).wait()

