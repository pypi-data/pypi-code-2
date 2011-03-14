# Create the variables and sets
model.M = RangeSet(0,10)
model.N = Set(initialize=[1,3,5,7,9])
model.x = Var(model.M)

# Create SOS1 constraints for the odd-indexed x variables
model.sos1 = SOSConstraint(var=model.x, set=model.M, level=1)
