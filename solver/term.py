"""
.. module:: term
   :synopsis: conatins the term module used to represent the unit of symbolic computations in the graph
.. moduleauthor:: Marcin Korecki
"""
from sympy import *
import time


def symbolicToNumeric(weight, bounds):
    """
    helper function for the integration
   
    :param weight: the weight function
    :param bounds: the bounds of the weight function

    :retuns: the numeric value of the integal within the given bounds
    """
    result = weight
    for arg, bound in bounds.items():
        result = result.subs(arg, bound[1])-result.subs(arg, bound[0])
    return result

def integrateFromDict(weight, bounds):
    """
    helper function for the integration

    :param weight: the weight function
    :param bounds: the bounds of the weight function

    :retuns: the numeric value of the integrated weight function
    """
    result = weight
    for key, value in bounds.items():
        result = weight.integrate([key, value[0], value[1]])
    return result

class Term(object):
    """
    The Term object represent the smallest computational unit over the circuit representation. The Term is used to store the weight
    functions in symbolic form, the associated bounds and the constant multiplier. The term implements multiplication and addition as well
    as integration. The weights, bounds and constants are all lists and their elements corresponding to elements of a sum.
    """
    def __init__(self, weights=None, bounds=None, const=None):
        """
        initialises the term object with specified weights, bounds and constant multiplier

        :param weights: the weight function
        :param bounds: the bounds of the weight function containing the integrated variable, the lower and upper bounds in that order
        :param const: the constant multiplier 
        """
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
        if const is None:
            self.const = [1]
        else:
            self.const = const

    def __add__(self, other):
        """
        Implements addition for two terms.

        :param other: the right hand side :class:`.Term` of addition

        :returns: the :class:`.Term` representing the sum of two terms
        """
        weights = self.weights + other.weights
        bounds = self.bounds + other.bounds
        const = self.const + other.const
        return Term(weights, bounds, const)

    def __mul__(self, other):
        """
        Implements multiplication for two terms taking care of bounds of functions of the same variables.

        :param other: the right hand side :class:`.Term` of multiplication

        :returns: the :class:`.Term` representing the multiplied terms
        """
        weights = flatten(Matrix(self.weights) * Matrix(other.weights).T)
        const = flatten(Matrix(self.const) * Matrix(other.const).T)
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
        return Term(weights, bounds, const)

    def __str__(self):
        """prints the term"""
        return "weights: " + str(self.weights) + " bounds: " + str(self.bounds) + "const: " + str(self.const)

    def integrate(self):
        """
        Implements efficient integation of a term.
    
        :returns: the :class:`.Term` with constant multiplier 1, empty bounds and the numerical value of the integrated constituent terms summed
        """
        integrated = {wf: wf.integrate(*wf.free_symbols) if hasattr(wf, 'free_symbols') and (len(wf.free_symbols) != 0) else wf for wf in set(self.weights)}
        integral = [symbolicToNumeric(integrated[self.weights[i]], self.bounds[i])*self.const[i] if hasattr(self.weights[i], 'free_symbols') else self.weights[i]*self.const[i] for i in range(len(self.weights))]
        return Term([1], [{}], [sum(integral)])
