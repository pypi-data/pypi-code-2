# Create the variables
model.N = RangeSet(0,10)
model.x = Var(model.N)

# Apply SOS2 constraints
model.sos1 = SOSConstraint(var=model.x, level=2)
