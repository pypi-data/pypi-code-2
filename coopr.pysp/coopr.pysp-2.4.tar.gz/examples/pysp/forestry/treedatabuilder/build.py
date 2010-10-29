#  tree generator
#
#  Main assumptions:
#     Data at Root Node is known
#     Price, Demand bounds and yield are the uncertainties
#     Price and Demand bounds are correlated
# 
from random import *

# to easily get random numbers
class MyRandom(object):
   randomtypes = ['uniform','normal','weibull']
   def __init__(self, alpha, beta, lb, ub, type):
      self.alpha = alpha
      self.beta = beta
      self.lb = lb
      self.ub = ub
      if type not in self.randomtypes:
         print "not valid random type, using default uniform"
         self.type = uniform
      self.type = type
   def get(self):
      if self.type == "uniform":
         return uniform(self.lb,self.ub)
      if self.type == "normal":
         aux = normalvariate(self.alpha,self.beta)
         if aux < self.lb:
            aux = self.lb
         if aux > self.ub:
            aux = self.ub
         return aux
      if self.type == "weibull":
         aux = weibullvariate(self.alpha,self.beta)
         if aux < self.lb:
            aux = self.lb
         if aux > self.ub:
            aux = self.ub
         return aux
# test the classMyRandom(1, 0.05*i, 0.9, 1.1, "normal")
#for i in range(1,5):
#   for type in MyRandom.randomtypes:
#      test = MyRandom(5,2,0,6,type)
#      print "type,get()=",type,"\t",test.get()

class Node(object):
   def __init__(self):
      self._name = ""
      self._stage = None
      self._parent = None
      self._children = [] # a collection of ScenarioTreeNodes
      self._conditional_probability = None # conditional on parent
      self._prob = None # conditional
      self._scenarios = [] # a collection of all Scenarios passing through this node in the tree
      self._Zlb = None 
      self._gapToZub = None
      self._Zub = None
      self._R = None
      self._yr = None
   def ver(self):
      print self._name,"\t","Zlb=",self._Zlb,"\t","Zub=",self._Zub,"\t R=",self._R,"yr",self._yr
      NodeFile = open(self._name+".dat",'w')
      NodeFile.write("#Random seed : "+str(SEED)+"\n")
      NodeFile.write("param R := E1 Ano"+str(self._stage)+" "+str(self._R)+";\n")
      NodeFile.write("param Zlb := Ano"+str(self._stage)+" "+str(self._Zlb)+";\n")
      NodeFile.write("param Zub := Ano"+str(self._stage)+" "+str(self._Zub)+";\n")
      NodeFile.write("param yr := Ano"+str(self._stage)+" "+str(self._yr)+";\n")
      NodeFile.close()

class Stage(object):
   def __init__(self):
      self.stagenumber   = None 
      self.PD_branching  = None 
      self.Y_branching   = None 
      self.PD_randomGen  = None 
      self.Y_randomGen   = None
      self.NodeList        = []

# Here starts the main

# Read file input
#global things
SEED = 17
seed(SEED)
#Root data input
R = 45
Zlb = 30000
Zub = 40000
yr = 1 #yield not year
#n of stages
TotalStages=4
#Branching
BranchAtStagePD = [1,3,2,2]
BranchAtStageY = [1,2,2,1]
# probability distribution function info
#pdf_Yield      = MyRandom(1,0.05,0.9,1.1,"normal")
#pdf_Zlb        = MyRandom(1,0.05,0.9,1.1,"normal")
pdf_GapToZub   = MyRandom(1,0.05,0.9,1.1,"normal")
pdf_R          = MyRandom(1,0.1 ,0.75,1.25,"normal")
# end file input

#Create Stages
Stages = []
for i in range(1,TotalStages+1):
   Stages.append( Stage() )
   Stages[i-1].stagenumber = i
   # just for fun... these should be read from a data file
   Stages[i-1].PD_randomGen = MyRandom(1, 0.05*i, 0.9, 1.1, "normal")
   Stages[i-1].Y_randomGen =  MyRandom(1+0.01*i, 0.03*i, 0.9, 1.1, "normal")
   Stages[i-1].PD_branching = BranchAtStagePD[i-1] 
   Stages[i-1].Y_branching = BranchAtStageY[i-1]

#Create RootNode
RootNode = Node()
RootNode._name = "NodeStage1"
RootNode._stage = Stages[0]
RootNode._Zlb      =  Zlb 
RootNode._gapToZub =  Zub - Zlb 
RootNode._R        =  R 
RootNode._yr       =  1 
RootNode._prob     =  1 
Stages[0].NodeList.append( RootNode )

for i in range(1,TotalStages):
   ymult = []
   for yb in range(1,Stages[i].Y_branching+1):
      if Stages[i].Y_branching == 1:
         ymult.append(1)
      else:
         ymult.append( Stages[i].Y_randomGen.get() )
   for ParentNode in Stages[i-1].NodeList:
      for pdb in range(1,Stages[i].PD_branching+1):
         if Stages[i].PD_branching == 1:
            zlbmult = 1
            gapmult = 1
            rmult = 1
         else:
            zlbmult = Stages[i].PD_randomGen.get()
            gapmult = zlbmult*pdf_GapToZub.get()
            rmult   = zlbmult*pdf_R.get()
         for yb in range(1,Stages[i].Y_branching+1):
            # create a new node with the new parameters
            newnode = Node()
            newnode._name = ParentNode._name.replace("Stage"+str(Stages[i-1].stagenumber),"Stage"+str(Stages[i].stagenumber))+"_PD"+str(pdb)+"Y"+str(yb)
            newnode._Zlb = int(zlbmult * ParentNode._Zlb)
            newnode._gapToZub = int(ParentNode._gapToZub * gapmult)
            newnode._Zub = newnode._Zlb + newnode._gapToZub
            newnode._R = int(ParentNode._R * rmult )
            newnode._yr = ymult[yb-1] * ParentNode._yr
            newnode._prob =  1.0/( Stages[i].Y_branching * Stages[i].PD_branching ) 
            newnode._parent = ParentNode
            newnode._stage = Stages[i].stagenumber 
            newnode.ver()
            ParentNode._children.append( newnode )
            # append it to the stage list
            Stages[i].NodeList.append( newnode ) 
         
# writing ScenarioStructure.dat
ScenarioStructureFile = open('ScenarioStructure.dat','w')
print "set Stages :="
ScenarioStructureFile.write("set Stages :=\n")
for Stage in range(TotalStages):
   print "\t\tAno"+str(Stage+1)+"Stage"
   ScenarioStructureFile.write("\t\tAno"+str(Stage+1)+"Stage\n")
print ";"
ScenarioStructureFile.write(";\n")

print "set Nodes := NodeStage1"
ScenarioStructureFile.write("set Nodes := NodeStage1\n")
for i in range(1,TotalStages):
   for ParentNode in Stages[i-1].NodeList:
      for children in ParentNode._children:
         print "\t",children._name
         ScenarioStructureFile.write("\t"+children._name+"\n")
print ";"
ScenarioStructureFile.write(";\n")

print "param NodeStage :=	NodeStage1      		Ano1Stage"
ScenarioStructureFile.write("param NodeStage :=	NodeStage1      		Ano1Stage\n")
for i in range(1,TotalStages):
   for ParentNode in Stages[i-1].NodeList:
      for children in ParentNode._children:
         print "\t",children._name,"\t\t\tAno"+str(i+1)+"Stage"
         ScenarioStructureFile.write("\t"+children._name+"\t\t\tAno"+str(i+1)+"Stage\n")
print ";"
ScenarioStructureFile.write(";\n")

for i in range(1,TotalStages):
   for ParentNode in Stages[i-1].NodeList:
      print "set Children["+ParentNode._name+"]:="
      ScenarioStructureFile.write("set Children["+ParentNode._name+"]:=\n")
      for children in ParentNode._children:
         print "\t",children._name
         ScenarioStructureFile.write("\t"+children._name+"\n")
      print ";"
      ScenarioStructureFile.write(";\n")

print "param ConditionalProbability := NodeStage1 1"
ScenarioStructureFile.write("param ConditionalProbability := NodeStage1 1\n")
for i in range(1,TotalStages):
   for ParentNode in Stages[i-1].NodeList:
      for children in ParentNode._children:
         print "\t",children._name,"\t\t\t",children._prob
         ScenarioStructureFile.write("\t"+children._name+"\t\t\t"+str(children._prob)+"\n")
print ";"
ScenarioStructureFile.write(";\n")

print "set Scenarios :="
ScenarioStructureFile.write("set Scenarios :=\n")
total = 1
for i in range(TotalStages):
   total *=Stages[i].Y_branching * Stages[i].PD_branching
for i in range(total):
   print "\tScenario"+str(i+1)
   ScenarioStructureFile.write("\tScenario"+str(i+1)+"\n")
print ";"
ScenarioStructureFile.write(";\n")

print "param ScenarioLeafNode :="
ScenarioStructureFile.write("param ScenarioLeafNode :=\n")
leafnode = Stages[TotalStages-1].NodeList
for i in range(len(leafnode)):
   print "\tScenario"+str(i+1),"\t\t",leafnode[i]._name
   ScenarioStructureFile.write("\tScenario"+str(i+1)+"\t\t"+leafnode[i]._name+"\n")
print ";"
ScenarioStructureFile.write(";\n")

#read and write StageVariables
StageVariablesFile = open('StageVariables.dat','r')
ScenarioStructureFile.write(StageVariablesFile.read())
StageVariablesFile.close() 
ScenarioStructureFile.close()

