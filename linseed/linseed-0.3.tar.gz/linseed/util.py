def pct(val):
    return int(val * 100)

def div(num, den):
    try:
        return float(num) / den
    except ZeroDivisionError:
        return 0

class Quantity(object):
    def __init__(self, value, unit):
        self.value = value
        self.unit = unit
