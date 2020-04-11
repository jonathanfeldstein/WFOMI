from sympy import *

class Term(object):
    def __init__(self, data=None, bounds=()):
        self.data = [data]
        self.bounds = [bounds]

    def __add__(self, other):
        for data, bound in zip(other.data, other.bounds):
            self.data.append(data)
            self.bounds.append(bound)
        return self
    
    def __mul__(self, other):
        newData = []
        newBounds = []
        for lhsData, lhsBound in zip(self.data, self.bounds):
            for rhsData, rhsBound in zip(other.data, other.bounds):
                newData.append(lhsData * rhsData)
                if rhsBound != ():
                    if lhsBound != ():
                        newBounds.append((max(lhsBound[0], rhsBound[0]), min(lhsBound[1], rhsBound[1])))
                    else:
                        newBounds.append(rhsBound)
                else:
                    newBounds.append(lhsBound)
        self.data = newData
        self.bounds = newBounds
        return self
    
    def __str__(self):
        return "data: " + str(self.data) + " bounds: " + str(self.bounds)

    def integrate(self):
        if [x for x in self.bounds if x == ()]:
            return sum(self.data)
        integrals = []
        for data, bound in zip(self.data, self.bounds):
            integrals.append(Integral(data, ('x', bound[0], bound[1])).evalf())
        return sum(integrals)

