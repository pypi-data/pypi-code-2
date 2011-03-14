# Create the variables and sets
model.M = RangeSet(0,2)

def nRule(m, model):
    if m == 0:
        return [0,1,2]
    elif m == 1:
        return [2,3,4]
    else:
        return [4,5,6]

model.N = Set(model.M, initialize=nRule)
model.W = RangeSet(0,8)
model.x = Var(model.W)

# Make 3 SOS1 constraints
model.sos1 = SOSConstraint(model.M, var=model.x, set=model.N,
                           level=1)
