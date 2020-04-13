from sympy import *

class Term(object):
    def __init__(self, data=None, bounds=()):
        if type(data) == list:
            self.data = data
        else:
            self.data = [data]
        if data == None:
            self.data = []
        if type(bounds) == list:
            self.bounds = bounds
        else:
            self.bounds = [bounds]

    def __add__(self, other):
        result = Term(self.data, self.bounds)
        for data, bound in zip(other.data, other.bounds):
            result.data.append(data)
            result.bounds.append(bound)
        return result
    
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
        result = Term(newData, newBounds)
        return result
    
    def __str__(self):
        return "data: " + str(self.data) + " bounds: " + str(self.bounds)

    def integrate(self):
        if [x for x in self.bounds if x == ()]:
            return sum(self.data)
        integrals = []
        for data, bound in zip(self.data, self.bounds):
            integrals.append(Integral(data, ('x', bound[0], bound[1])).evalf())
        return sum(integrals)

