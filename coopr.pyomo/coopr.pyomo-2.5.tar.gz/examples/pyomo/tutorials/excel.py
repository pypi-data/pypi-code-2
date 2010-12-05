#
# Imports
#
import sys
sys.path.append("../../..")
from coopr.pyomo import *
import coopr
#pyomo.set_debugging()

##
## Using a Model
##
#
# Pyomo makes a fundamental distinction between an abstract model and a
# problem instance.  The Pyomo Model() class is used to manage the 
# declaration of model components (e.g. sets and variables), and to 
# generate a problem instance.
#
model = Model()

##
## Declaring Sets
##
#
# An unordered set of arbitrary objects
#
model.A = Set()
#
# An unordered set of numeric values
#
model.B = Set()
#
# A simple cross-product
#
model.C = model.A * model.B
#
# A simple cross-product loaded with a tabular data format
#
model.D = Set(within=model.A * model.B)
#
# A multiple cross-product
#
model.E = Set(within=model.A * model.B * model.A)

#
# An indexed set
# 
model.F = Set(model.A)
#
# An indexed set
# 
model.G = Set(model.A,model.B)
#
# A simple set
#
model.H = Set()
#
# A simple set
#
model.I = Set()
#
# A two-dimensional set
#
model.J = Set(dimen=2)

##
## Declaring Params
##
#
#
# A simple parameter
#
model.Z = Param()
#
# A single-dimension parameter
#
model.Y = Param(model.A)
#
# An example of initializing two single-dimension parameters together
#
model.X = Param(model.A)
model.W = Param(model.A)
#
# Initializing a parameter with two indices
#
model.U = Param(model.I,model.A)
model.T = Param(model.A,model.I)
#
# Initializing a parameter with missing data
#
model.S = Param(model.A)
#
# An example of initializing two single-dimension parameters together with
# an index set
#
model.R = Param(model.H, within=Reals)
model.Q = Param(model.H, within=Reals)
#
# An example of initializing parameters with a two-dimensional index set
#
model.P = Param(model.J, within=Reals)
model.PP = Param(model.J, within=Reals)
model.O = Param(model.J, within=Reals)
   
##
## Process an input file and confirm that we get appropriate 
## set instances.
##
#model.pprint()

data = ModelData(model)
data.add_table("excel.xls", "Atable")
data.add_table("excel.xls", "Btable")
data.add_table("excel.xls", "Ctable", set="C")
data.add_table("excel.xls", "Dtable", set="D", format="array")
data.add_table("excel.xls", "Etable", set="E")
data.add_table("excel.xls", "Itable")
data.add_table("excel.xls", "Zparam", param="Z")
data.add_table("excel.xls", "Ytable")
data.add_table("excel.xls", "XWtable")
data.add_table("excel.xls", "Ttable", param="T", format="transposed_array")
data.add_table("excel.xls", "Utable", param="U", format="array")
data.add_table("excel.xls", "Stable")
data.add_table("excel.xls", "RQtable", index="H")
data.add_table("excel.xls", "POtable", index="J", param=("P","O"))
data.add_table("excel.xls", "PPtable", param="PP")
try:
  data.read()
except coopr.ApplicationError:
  sys.exit(0)


instance = model.create(data)
instance.pprint()

