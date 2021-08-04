"""
.. module:: circuit
   :synopsis: The nodes represent the nodes of the cicuit 
each node has a compute class which follows the computation step of the algorithm for the given node
the maxDomainSize is used to compute the maximum domain size for the existential node
.. moduleauthor:: Marcin Korecki
"""

from sympy import *
from sympy.abc import *
from term import *


class Node(object):
    """
    The base class defining a node, all other nodes inherit from it
    """
    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def compute(self):
        raise NotImplementedError("Subclass must implement abstract method")
    def maxDomainSize(self):
        """
        used to compute the maximum domain size for the existential node
        """
        raise NotImplementedError("Subclass must implement abstract method")

class ForAllNode(Node):
    def __init__(self, var=None, domData=None):
        """
        initialises the universal node with the variables it quantifies over and the data on the domain that 
           the variables correspond to

        :param var: the name of the variable that the universal quantifies over
        :param domData: the dictionary containing the data on the domains corresponding to variables, the data stores 3 values for
        each variable, the list of objects in the domain, the domain type (top or bot depending on the existential split) and the without set 
        representing the objects removed from the domain 
        """
        super().__init__()
        self.var = var
        self.domData = domData

    def compute(self, domSize=None, removed=None):
        """
        computes the numerical value at the universal node based on the size of the domain it quantifies over taking into account the 
        objects that have been removed from it
    
        :param domSize: the size of the domain the universal is quantifying over
        :param removed: the list of objects removed from the domain

        :returns: the :class:`.Term` with a cosntant equal to 1, empty bounds and the result of the integration at the universal node 
        raised to the power of its domain size
        """
        domain, domType, without, _ = self.domData[self.var]
        domain = list(set(domain) - set(without))

        if domSize is None:
            domSize = [len(domain), len(domain)]

        if domType == 'bot':
            exponent = domSize[1]
        elif domType == 'top':
            exponent = domSize[0]
        else:
            exponent = len(domain)

        term = self.left.compute(domSize=domSize, removed=removed)
        result = term.integrate()
        return Term([1], [{}], [result.const[0]**exponent])

    def maxDomainSize(self):
        """
        used to compute the maximum domain size for the existential node

        :returns: the maximum size of the domain at the given node and the set of objects removed from it
        """
        domain, _, without, _ = self.domData[self.var]
        return len(list(set(domain) - set(without))), without

class ExistsNode(Node):
    def __init__(self, var=None, domData=None):
        """
        initialises the existential node with the variables it quantifies over and the data on the corresponding domains]

        :param var: the name of the variable that the universal quantifies over
        :param domData: the dictionary containing the data on the domains corresponding to variables, the data stores 3 values for
        each variable, the list of objects in the domain, the domain type (top or bot depending on the existential split) and the without set 
        representing the objects removed from the domain
        """
        super().__init__()
        self.var = var
        self.domData = domData

    def compute(self, domSize=None, removed=None):
        """
        computes the symbolic value at the existential node based on the size of the domain it quantifies over and taking into account the
        objects removed from it

        :param domSize: the size of the domain the existential is quantifying over
        :param removed: the list of objects removed from the domain

        :returns: the :class:`.Term` representing the value at the existential node
        """
        maxSize, removed = self.left.maxDomainSize()

        if domSize is None:
            domSize = [maxSize, maxSize, maxSize]

        result = Term([1], [{}], [0])

        for i in range(0, maxSize + 1):
            coeff = Term([1], [{}], [binomial(maxSize, i)])
            compute = self.left.compute(domSize=[i, domSize[0] - i, maxSize], removed=removed)
            result += coeff * compute
        return result

    def maxDomainSize(self):
        """
        used to compute the maximum domain size for the existential node
        
        :returns: the maximum size of the domain at the given node and the set of objects removed from it
        """
        domain, _, without, _ = self.domData[self.var]
        return len(list(set(domain) - set(without))), without

class OrNode(Node):
    def compute(self, domSize=None, removed=None):
        """
        computes the symbolic value at the or node by adding two terms at its child nodes, the setsize and removed are passed for potential 
        existential and universals that may be the node's descendants

        :param domSize: the size of the domain of the ancestor quantifiers
        :param removed: the list of objects removed from the domain

        :returns: the :class:`.Term` representing the sum of the values at the child nodes of the or node
        """
        leftTerm = self.left.compute(domSize=domSize, removed=removed)
        rightTerm = self.right.compute(domSize=domSize, removed=removed)
        return leftTerm + rightTerm

    def maxDomainSize(self):
        """
        used to compute the maximum domain size for the existential node, the maxDomain is the larger domain out of the domains of the
        left and right children

        :returns: the maximum size of the domain at the given node and the set of objects removed from it 
        """
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return left[0], left[1]
        else:
            return right[0], right[1]

class AndNode(Node):
    def compute(self, domSize=None, removed=None):
        """
        computes the symbolic value at the and node by multiplying two terms at its child nodes. the domSize and removed are passed for 
        potential existential and universals that may be the node's descendants
        
        :param domSize: the size of the domain of the ancestor quantifiers
        :param removed: the list of objects removed from the domain

        :returns: the :class:`.Term` representing the multiplication of the values at the child nodes of the or node
        """
        leftTerm = self.left.compute(domSize=domSize, removed=removed)
        rightTerm = self.right.compute(domSize=domSize, removed=removed)
        return leftTerm * rightTerm

    def maxDomainSize(self):
        """
        used to compute the maximum domain size for the existential node, the maxDomain is the larger domain out of the domains of the
        left and right children

        :returns: the maximum size of the domain at the given node and the set of objects removed from it 
        """
        left = self.left.maxDomainSize()
        right = self.right.maxDomainSize()
        if left[0] > right[0]:
            return left[0], left[1]
        else:
            return right[0], right[1]

class ConstNode(Node):
    def __init__(self, data=None, nodeName=None, varList=None, domData=None):
        """
        initialises the constant node with the

        :param data: represents the type of a constant node (and, or, leaf)
        :param nodeName: used as a key in a dictionary storing the domains of the nodes
        :param varList: the list of variables the constant node deals with
        :param domData: the dictionary containing the data on the domains corresponding to variables, the data stores 3 values for
        each variable, the list of objects in the domain, the domain type (top or bot depending on the existential split) and the without set 
        representing the objects removed from the domain       
        """
        super().__init__()
        self.data = data
        self.varList = varList
        self.nodeName = nodeName
        self.domData = domData
        self.shouldIntegrate = True

    def compute(self, domSize=None, removed=None):
        """
        Computes the symbolic value at the constant node depending on its type

        :param domSize: the size of the domain of the ancestor quantifiers
        :param removed: the list of objects removed from the domain

        :returns: the :class:`.Term` representing the value at the constant node which is eithe symbolic if the node is under a universal 
        node quantifying over the same domain or otherwise numeric corresponding to universal quantification over its domain
        """
        if domSize is None:
            domain, _, _, _ = self.domData[self.nodeName + self.varList[0]]
            domSize = [len(domain), len(domain), len(domain)]

        if removed is None:
            removed = []

        exponent = 1
        for var in self.varList:
            key = self.nodeName + var
            domain, domType, without, _ = self.domData[key]

            dec = 0
            for otherVar in self.varList:
                if var != otherVar and otherVar in without:
                    dec = 1

            without = set(without) - set(self.varList)
            without = (without - set(removed))

            if domType == "bot":
                exponent *= max(0, domSize[1] - len(without))
            elif domType == "top":
                exponent *= max(0, domSize[0] - len(without))
            else:
                exponent *= max(0, domSize[2] - len(without))
            exponent = max(0, exponent - dec)

        if self.data == "or":
            leftTerm = self.left.compute(domSize=domSize)
            rightTerm = self.right.compute(domSize=domSize)
            result = leftTerm + rightTerm
        elif self.data == "and":
            leftTerm = self.left.compute(domSize=domSize)
            rightTerm = self.right.compute(domSize=domSize)
            result = leftTerm * rightTerm
        else:
            result = self.left.compute(domSize=domSize)

        if self.shouldIntegrate:
            result = result.integrate()
            return Term([1], [{}], [result.const[0]**exponent])
        else:
            return result
    
    def maxDomainSize(self):
        """
        used to compute the maximum domain size for the existential node based on the largest domain of the variables of the constant node

        :returns: the maximum size of the domain at the given node and the set of objects removed from it 
        """
        domSize = 0
        without = None
        for var in self.varList:
            key = self.nodeName + var
            domain, _, without, _ = self.domData[key]
            if len(list(set(domain) - set(without))) > domSize:
                domSize = len(list(set(domain) - set(without)))
        return domSize, without


class LeafNode(Node):
    def __init__(self, data=None, weights=None):
        """
        initialises the leaf node
        
        :param data: the key for the dictionary containing the weights 
        :param weights: a dictionary containing all the data pertaining to the weights of a predicate. In case of simple weights it is a 
        single value. In case of complex weights it is the symbolic weight function, the bounds, the arguments of the function and the
        constant multiplier in that order
        """
        super().__init__()
        self.data = data
        self.weight = weights[data]

    def compute(self, domSize=None, removed=None):
        """
        computes the symbolic value at the leaves depending on weather the corresponding weight is a float or a function

        :param domSize: the size of the domain of the ancestor quantifiers
        :param removed: the list of objects removed from the domain

        :retuns: the term corresponding to the weight function of the predicate at the node
        """
        if type(self.weight) == tuple:
            if len(self.weight) > 2:
                weight = [sympify(self.weight[0])]
                args = [sympify(arg) for arg in self.weight[2]]
                const = int(self.weight[3])
                bounds = [list(bound) for bound in self.weight[1]]
                bounds = [dict(zip(args, bounds))]
                result = Term(weight, bounds, [const])
                return result
            else:
                return Term([sympify(self.weight[0])], [{}], [self.weight[1]])
        else:
            return Term([sympify(self.weight)], [{}], [1])

    def maxDomainSize(self):
        """
        used to compute the maximum domain size for the existential node

        :returns: 0 as the domain of the leaf node is empty as it does not quantify over anything
        """
        return 0
