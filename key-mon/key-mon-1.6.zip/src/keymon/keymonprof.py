#!/usr/bin/python
import pstats

if __name__ == '__main__':
  p = pstats.Stats('keymonprof')
  #p.strip_dirs().sort_stats(-1).print_stats(10)

  p.sort_stats('time').print_stats(10)

  p.sort_stats('cumulative').print_stats(10)

