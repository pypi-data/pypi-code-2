from chiplotle.hpgl.commands import PM, EP, FP 
from chiplotle.hpgl.compound.compound import _CompoundHPGL

class Polygon(_CompoundHPGL):
   '''A Polygon that models the HPGL polygon definition via PM.
      
      - `subshapes` : a list of _CompoundHPGL commands that make up
         the totality of the polygon. Each subshape is ended with 'PM1;'
         in the HPGL returned by the formatter.
   '''
   def __init__(self, xy, subshapes, filled=False, pen=None):
      _CompoundHPGL.__init__(self, xy, pen)
      self.subshapes = subshapes
      self.filled = filled
      

   @apply
   def subshapes( ):
      def fget(self):
         return self._subshapes
      def fset(self, arg):
         if not isinstance(arg, (list, tuple)):
            raise TypeError('`arg` must be a list or tuple.')
         for shape in arg:
            if not isinstance(shape, _CompoundHPGL):
               raise TypeError('all subshapes must be _CompoundHPGL.')
         self._subshapes = arg
      return property(**locals( ))
         

   @property
   def _subcommands(self):
      result = _CompoundHPGL._subcommands.fget(self)
      result.append(PM(0))
      for shape in self.subshapes:
         result += shape._subcommands
         result.append(PM(1))
      ## remove the last PM(1)... is this necessary?
      result.pop(-1)
      result.append(PM(2))
      if self.filled:
         result.append(FP( ))
      result.append(EP( ))
      return result

