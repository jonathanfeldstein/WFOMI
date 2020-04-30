from sympy import *

class Term(object):
    def __init__(self, data=None, args=(), bounds=()):
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
        if type(args) == list:
            self.args = args
        else:
            self.args = [args]

    def __add__(self, other):
        result = Term(self.data, self.args, self.bounds)
        for data, args, bound in zip(other.data, other.args, other.bounds):
            result.data.append(data)
            result.args.append(args)
            result.bounds.append(bound)
        return result
    
    def __mul__(self, other):
        newData = []
        newArgs = []
        newBounds = []
        for lhsData, lhsArg, lhsBound in zip(self.data, self.args, self.bounds):
            for rhsData, rhsArg, rhsBound in zip(other.data, other.args, other.bounds):
                newData.append(lhsData * rhsData)
                if lhsArg != rhsArg:
                    newArgs.append([lhsArg, rhsArg])
                else:
                    newArgs.append(lhsArg)
                if rhsBound != ():
                    if lhsBound != ():
                        newBounds.append((max(lhsBound[0], rhsBound[0]), min(lhsBound[1], rhsBound[1])))
                    else:
                        newBounds.append(rhsBound)
                else:
                    newBounds.append(lhsBound)
        result = Term(newData, newArgs, newBounds)
        return result
    
    def __str__(self):
        return "data: " + str(self.data) + "args:" + str(self.args)  + " bounds: " + str(self.bounds)

    def integrate(self):
        if [x for x in self.bounds if x == ()]:
            return sum(self.data)
        
        integrals = []
        for data, args, bound in zip(self.data, self.args, self.bounds):
            integrals.append(Integral(data, (args, bound[0], bound[1])).evalf())
        return sum(integrals)

