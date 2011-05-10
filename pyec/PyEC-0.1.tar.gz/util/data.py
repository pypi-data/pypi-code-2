import os.path, sys, traceback
from numpy import *
import random

class discretizer(object):
   """ Find optimal cut-points using MDLPC ~ Fayyad-Irani (1993) """ 

   def __init__(self, index, cmpIndex):
      self.index = index
      self.cmpIndex = cmpIndex

   def __call__(self, data, categories):
      #print "discretizing: ", len(categories[self.index])
      self.length = len(data)
      for x in data:
         x[self.index] = float(x[self.index])
      #print "converted data"
      numCats = len(categories[self.cmpIndex])
      sortdata = sorted(data, key=lambda x: x[self.index])
      toSplit = [(sortdata, numCats, (-1e1000, 1e1000))]
      cuts = []
      while len(toSplit) > 0:
         d, numActiveCats, rnge = toSplit[0]
         #print "attempting to split: ", rnge
         accept, cut, idx, under, over = self.explore(d, numActiveCats, numCats)
         if accept:
            #print "accepted: ", cut, idx, len(d), rnge, under, over
            toSplit.append((d[:idx], under, (rnge[0], cut) ))
            toSplit.append((d[idx:], over, (cut, rnge[1]) ))
         else:
            #print "added: ", rnge
            cuts.append(rnge)
         toSplit = toSplit[1:]
      for x in data:
         for i, (lower, upper) in enumerate(cuts):
            if x[self.index] >= lower and x[self.index] < upper:
               x[self.index] = i + 1
               break
      print "completed discretization", self.index, len(categories[self.index]), len(cuts)
      categories[self.index] = cuts
      return data, categories
   
   def explore(self, data, numActiveCats, numCats):
      mincut = None
      minunder = None
      minover = None
      catsunder = None
      catsover = None
      minval = 1e1000
      minidx = -1
      for i in xrange(len(data) - 1):
         if data[i][self.index] != data[i+1][self.index]:
            #print "checking: ", i, data[i][self.index], len(data)
            cut = data[i][self.index] + .5 * (data[i+1][self.index] - data[i][self.index])
            underent, numCatsUnder = self.entropy(data[:i+1], numCats)
            overent, numCatsOver = self.entropy(data[i+1:], numCats)
            ent = (i + 1.) / (len(data) + 0.) * underent
            ent += (len(data) - i - 1.0) / len(data) * overent
            #print "candidate: ", ent, underent, overent
            if ent < minval:
               minval = ent
               mincut = cut
               minidx = i + 1
               minunder = underent
               minover = overent
               catsunder = numCatsUnder
               catsover = numCatsOver
               
      if mincut is None:
         return False, None, None, None, None
      totalent, numActive = self.entropy(data, numCats)
      gain = totalent - minval
      delta = log2((3**numActiveCats) - 2) - numActiveCats * totalent + catsunder * minunder + catsover * minover
      #print totalent, minval, gain, (log2(len(data) - 1) + delta)/ len(data)
      accept = gain > (log2(len(data) - 1) + delta)/ len(data)
      return accept, mincut, minidx, catsunder, catsover
   
   def entropy(self, data, numCats):
      catProbs = zeros(numCats)
      for x in data:
         catProbs[x[self.cmpIndex] - 1] += 1
      numAfter = int((catProbs / maximum(catProbs, .1)).sum())
      catProbs /= len(data)
      #print "probs: ", catProbs
      #print "log: ", (-catProbs * log2(maximum(catProbs, 0.00000001))) 
      ret = (-catProbs * log2(maximum(catProbs, 0.00000001))).sum()
      return ret, numAfter


class multinomial_data(object):
   def __init__(self, fname, sort=True, cmpIndex=0):
      self.parse(fname, sort, cmpIndex)
   
   
   def splitTrain(self, percent=.8):
      """
      provide the first <percent>% of entries for training; 
      data should not be sorted
      """
      index = int(len(self.data) * percent)
      return self.data[:index]
   
   def splitTest(self, percent=.8):
      """
      provide the last <1 - percent>% of entries for training; 
      data should not be sorted
      """
      index = int(len(self.data) * percent)
      return self.data[index:]
   
   def crossValidateTrain(self, index, numParts=5):
      return list([d for i,d in enumerate(self.data) if (i % numParts) != index])
      
   def crossValidateTest(self, index, numParts=5):
      return list([d for i,d in enumerate(self.data) if (i % numParts) == index])   
   
   def discretize(self, cmpIndex):
      for i in xrange(len(self.categories)):
         if i != cmpIndex:
            try:
               self.data, self.categories = discretizer(i, cmpIndex)(self.data, self.categories)
            except:
               print sys.exc_info()
               traceback.print_exc()
   
   def parse(self, fname, sort=True, cmpIndex=0):
      f = open(fname)
      rows = []
      vals = {}
      numVars = 0
      
      for line in f.readlines():
         if line.strip() == "":
            continue
         row = line.strip().split(",")
         d = []
         numVars = len(row)
         for i, val in enumerate(row):
            if vals.has_key(i):
               if not val in vals[i]:
                  vals[i].append(val)
            else:
               vals[i] = [val]
            d.append(vals[i].index(val) + 1)
         rows.append(d)
      
      self.numVariables = numVars
      self.data = rows
      self.vals = vals
      self.cnts = dict(((i, len(options)) for i, options in vals.iteritems()))
      self.categories = [[] for i in xrange(self.numVariables)]
      for i, cats in self.vals.iteritems():
         self.categories[i] = cats
         
      # sort by column 0
      if sort:
         self.data = sorted(self.data, key=lambda x: x[cmpIndex])
      
     


class chess(multinomial_data):
   def __init__(self):
      super(chess, self).__init__(os.path.join(os.path.dirname(__file__), 'chess.data'), False )
      random.seed(3454983945)
      random.shuffle(self.data)
      random.seed()
      
class letter(multinomial_data):
   def __init__(self):
      super(letter, self).__init__(os.path.join(os.path.dirname(__file__), 'letter-recognition.data'), False)
      self.discretize(0)
      
class soybean(multinomial_data):
   def __init__(self, appendTest = True):
      super(soybean, self).__init__(os.path.join(os.path.dirname(__file__), 'soybean-large.data'))
      self.mainData = self.data
      if appendTest:
         self.parse(os.path.join(os.path.dirname(__file__), 'soybean-large.test'))
         self.mainData.extend(self.data)
         self.data = self.mainData

class satimage(multinomial_data):
   def __init__(self, appendTest = True):
      super(satimage, self).__init__(os.path.join(os.path.dirname(__file__), 'satimage.data'), False)
      self.mainData = self.data
      if appendTest:
         self.parse(os.path.join(os.path.dirname(__file__), 'satimage.test'), False)
         self.mainData.extend(self.data)
         self.data = self.mainData
      self.discretize(36)
            

class soybeanTest(multinomial_data):
   def __init__(self):
      super(soybeanTest, self).__init__(os.path.join(os.path.dirname(__file__), 'soybean-large.test'))   
      
class pima(multinomial_data):
   def __init__(self):
      super(pima, self).__init__(os.path.join(os.path.dirname(__file__), 'pima-indians-diabetes.data'), True, 8)
      self.discretize(8)
      for x in self.data:
         print x   
   

         
datasets = {
   # name :   (class, split method, CV # or percent for test, index of target)
   'soybean': (soybean, "cross", 5, 0),
   'chess': (chess, "split", .6665, 36),
   'letter': (letter, "split", .8, 0),
   'satimage': (satimage, "split", .6892, 36),
   'pima': (pima, "cross", 5, 8) # not multinomial!!!!
}