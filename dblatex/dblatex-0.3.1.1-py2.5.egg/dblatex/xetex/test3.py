# 

test_cases1 = [
(2, "[[2]]"),
(4, "[[2], [4]]"),
(3, "[[2, 4]]"),
(3, "[[2, 4]]"),
(5, "[[2, 5]]"),
(1, "[[1, 5]]"),
(8, "[[1, 5], [8]]"),
(9, "[[1, 5], [8, 9]]"),
(11,"[[1, 5], [8, 9], [11]]"),
(10,"[[1, 5], [8, 11]]"),
(20,"[[1, 5], [8, 11], [20]]"),
(15,"[[1, 5], [8, 11], [15], [20]]"),
(0, "[[0, 5], [8, 11], [15], [20]]"),
(-2,"[[-2], [0, 5], [8, 11], [15], [20]]")
]

test_cases2 = [
((1,   6),"[[-2], [0, 6], [8, 11], [15], [20]]"),
((12, 14),"[[-2], [0, 6], [8, 15], [20]]"),
((1,  23),"[[-2], [0, 23]]"),
((2,  24),"[[-2], [0, 24]]"),
((-3, -2),"[[-3, -2], [0, 24]]")
]


from urange import URange, UInterval

def test_char(r, val):
    r.add_char(val)
    s = str(r)
    return s

r = URange()

for (val, result) in test_cases1:
    s = test_char(r, val)
    print s
    assert(s==result)

print 

for (ui, result) in test_cases2:
    r.add_interval(UInterval(ui[0], ui[1]))
    s = str(r)
    print s
    assert(s==result)

