import itertools
import HTSeq

samfile = "../example_data/yeast_RNASeq_excerpt.sam"

for l in itertools.islice( open( samfile ), 30 ):
   if l.startswith( "@" ):
      continue
   a = HTSeq.SAM_Alignment( l )
   print l,
   print a
   print a.get_sam_line()
   print
