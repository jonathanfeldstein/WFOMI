from sympy import *
import time

class Term(object):
    def __init__(self, data=None, args=(), bounds=()):
        if type(data) == list:
            self.data = data
        else:
            self.data = [data]
        if data is None:
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
                if lhsArg != rhsArg and lhsArg != () and rhsArg != ():
                    newArgs.append((lhsArg, rhsArg))
                    newBounds.append((lhsBound, rhsBound))
                if rhsBound != ():
                    if lhsBound != ():
                        newBounds.append((max(lhsBound[0], rhsBound[0]), min(lhsBound[1], rhsBound[1])))
                        newArgs.append(lhsArg)
                    else:
                        newBounds.append(rhsBound)
                        newArgs.append(rhsArg)
                else:
                    newBounds.append(lhsBound)
                    newArgs.append(lhsArg)
        result = Term(newData, newArgs, newBounds)
        return result

    def __str__(self):
        return "data: " + str(self.data) + "args:" + str(self.args) + " bounds: " + str(self.bounds)

    def integrate(self):
        if [x for x in self.bounds if x == ()]:
            return sum(self.data)

        integrals = []
        for data, args, bounds in zip(self.data, self.args, self.bounds):
            # Simplify expression, by expanding into sum of simple functions, e.g. x*(x**2+2)=> x**3+2x
            data = data.expand()
            if len(args) == 1:
                integrals.append(Integral(data, (args, bounds[0], bounds[1])).evalf())
            else:
                integral = None
                for arg, bound in zip(args, bounds):
                    if integral is None:
                        integral = Integral(data, (arg, bound[0], bound[1])).evalf()
                    else:
                        integral = Integral(integral, (arg, bound[0], bound[1])).evalf()
                integrals.append(integral)
        return sum(integrals)
