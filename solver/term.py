from sympy import *
import time

def symbolicToNumeric(wf, bounds):
    result = wf
    for arg, bound in bounds.items():
        result = result.subs(arg, bound[1])-result.subs(arg, bound[0])
    return result

def integrateFromDict(wf, bounds):
    result = wf
    for key, value in bounds.items():
        result = wf.integrate([key, value[0], value[1]])
    return result

class Term(object):
    def __init__(self, weights=None, bounds=None, constant=None):
        if weights is None:
            self.weights = [1]
        else:
            self.weights = weights
        # bounds are integral bounds
        if bounds is None:
            self.bounds = [{}]
        else:
            self.bounds = bounds
        # constant value carried separately for speed improvement.
        # Default is 1 in which case the weight function is not altered by the cst.
        if constant is None:
            self.constant = [1]
        else:
            self.constant = constant

    def __add__(self, other):
        weights = self.weights + other.weights
        bounds = self.bounds + other.bounds
        constant = self.constant + other.constant
        return Term(weights, bounds, constant)

    def __mul__(self, other):
        weights = flatten(Matrix(self.weights) * Matrix(other.weights).T)
        constant = flatten(Matrix(self.constant) * Matrix(other.constant).T)
        bounds = []
        for bounds1 in self.bounds:
            for bounds2 in other.bounds:
                newBound = bounds1.copy()
                bounds1set = set(bounds1)
                bounds2set = set(bounds2)
                for variable in bounds1set & bounds2set:
                    newBound[variable] = [max(bounds1.get(variable)[0], bounds2.get(variable)[0]), min(bounds1.get(variable)[1], bounds2.get(variable)[1])]
                for variable in bounds2set-bounds1set:
                    newBound[variable] = bounds2.get(variable)
                bounds.append(newBound)
        return Term(weights, bounds, constant)

    def __str__(self):
        return "weights: " + str(self.weights) + " bounds: " + str(self.bounds) + "constant: " + str(self.constant)

    def integrate(self):
        integrated = {wf: wf.integrate(*wf.free_symbols) if hasattr(wf, 'free_symbols') and (len(wf.free_symbols) != 0) else wf for wf in set(self.weights)}
        integral = [symbolicToNumeric(integrated[self.weights[i]], self.bounds[i])*self.constant[i] if hasattr(self.weights[i], 'free_symbols') else self.weights[i]*self.constant[i] for i in range(len(self.weights))]
        # integral = [integrateFromDict(self.weights[i], self.bounds[i])*self.constant[i] if hasattr(self.wfs[i], 'free_symbols') else self.weights[i]*self.constant[i] for i in range(len(self.weights))]
        return Term([1], [{}], [sum(integral)])
